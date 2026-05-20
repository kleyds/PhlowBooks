from __future__ import annotations

import csv
import io
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import fitz
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import get_current_user, user_from_token
from app.database import SessionLocal, get_db
from app.extract import extract_receipt
from app.models import Client, LineItemRecord, Receipt, ReceiptComment, ReceiptDataRecord, User
from app.ocr import image_to_text, pdf_to_text
from app.schemas import (
    ReceiptPatchRequest,
    ReceiptCommentCreateRequest,
    ReceiptCommentPublic,
    ReceiptCommentsResponse,
    ReceiptPublic,
    ReceiptsResponse,
    ReceiptUploadItem,
    ReceiptUploadResponse,
)

router = APIRouter(tags=["receipts"])

IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_TYPES = IMAGE_TYPES | {"application/pdf"}


def _upload_root() -> Path:
    return Path(os.getenv("UPLOAD_DIR", "./uploads")).resolve()


def _client_or_404(client_id: int, user_id: int, db: Session) -> Client:
    client = db.scalar(
        select(Client).where(
            Client.id == client_id,
            Client.user_id == user_id,
            Client.deleted_at.is_(None),
        )
    )
    if not client:
        raise HTTPException(404, "Client not found")
    return client


def _receipt_or_404(receipt_id: int, user_id: int, db: Session) -> Receipt:
    receipt = db.scalar(
        select(Receipt)
        .options(selectinload(Receipt.data), selectinload(Receipt.line_items), selectinload(Receipt.comments))
        .where(Receipt.id == receipt_id, Receipt.user_id == user_id)
    )
    if not receipt:
        raise HTTPException(404, "Receipt not found")
    return receipt


def _extension(filename: Optional[str], content_type: Optional[str]) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".pdf"}:
        return suffix
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "application/pdf": ".pdf",
    }.get(content_type or "", "")


def _next_month(month: str) -> str:
    year, month_number = [int(part) for part in month.split("-")]
    if month_number == 12:
        return f"{year + 1}-01-01"
    return f"{year}-{month_number + 1:02d}-01"


def _receipt_statement(
    client_id: int,
    user_id: int,
    status: Optional[str] = None,
    month: Optional[str] = None,
    vendor: Optional[str] = None,
    doc_type: Optional[str] = None,
    vat_type: Optional[str] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
):
    statement = (
        select(Receipt)
        .options(selectinload(Receipt.data), selectinload(Receipt.line_items), selectinload(Receipt.comments))
        .where(Receipt.client_id == client_id, Receipt.user_id == user_id)
    )

    joined_data = False

    def with_data_join():
        nonlocal statement, joined_data
        if not joined_data:
            statement = statement.join(ReceiptDataRecord, ReceiptDataRecord.receipt_id == Receipt.id)
            joined_data = True

    if status:
        statement = statement.where(Receipt.status == status)
    if month:
        with_data_join()
        statement = statement.where(ReceiptDataRecord.date >= f"{month}-01", ReceiptDataRecord.date < _next_month(month))
    if vendor:
        with_data_join()
        statement = statement.where(ReceiptDataRecord.vendor.ilike(f"%{vendor}%"))
    if doc_type:
        with_data_join()
        statement = statement.where(ReceiptDataRecord.doc_type == doc_type)
    if vat_type:
        with_data_join()
        statement = statement.where(ReceiptDataRecord.vat_type == vat_type)
    if min_total is not None:
        with_data_join()
        statement = statement.where(ReceiptDataRecord.total >= min_total)
    if max_total is not None:
        with_data_join()
        statement = statement.where(ReceiptDataRecord.total <= max_total)

    return statement


def _write_csv(headers: list[str], rows: list[list[Optional[object]]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


def _receipt_reference(receipt: Receipt) -> str:
    data = receipt.data
    if not data:
        return ""
    return data.or_number or data.si_number or ""


def _csv_for_receipts(receipts: list[Receipt], export_format: str) -> str:
    if export_format == "qbo":
        headers = ["Date", "Description", "Account", "Debit", "Credit", "Memo", "Name"]
        rows = [
            [
                receipt.data.date if receipt.data else "",
                receipt.data.vendor if receipt.data else receipt.original_name,
                "Uncategorized Expense",
                receipt.data.total if receipt.data else "",
                "",
                _receipt_reference(receipt),
                receipt.data.vendor if receipt.data else "",
            ]
            for receipt in receipts
        ]
        return _write_csv(headers, rows)

    if export_format == "xero":
        headers = ["Date", "Amount", "Payee", "Description", "Reference", "Account Code"]
        rows = [
            [
                receipt.data.date if receipt.data else "",
                receipt.data.total if receipt.data else "",
                receipt.data.vendor if receipt.data else "",
                receipt.original_name or f"Receipt #{receipt.id}",
                _receipt_reference(receipt),
                "",
            ]
            for receipt in receipts
        ]
        return _write_csv(headers, rows)

    headers = [
        "receipt_id",
        "date",
        "vendor",
        "vendor_tin",
        "or_number",
        "si_number",
        "currency",
        "subtotal",
        "tax",
        "vat_type",
        "vatable_amount",
        "vat_amount",
        "total",
        "doc_type",
        "confidence",
        "original_name",
    ]
    rows = [
        [
            receipt.id,
            receipt.data.date if receipt.data else "",
            receipt.data.vendor if receipt.data else "",
            receipt.data.vendor_tin if receipt.data else "",
            receipt.data.or_number if receipt.data else "",
            receipt.data.si_number if receipt.data else "",
            receipt.data.currency if receipt.data else "PHP",
            receipt.data.subtotal if receipt.data else "",
            receipt.data.tax if receipt.data else "",
            receipt.data.vat_type if receipt.data else "",
            receipt.data.vatable_amount if receipt.data else "",
            receipt.data.vat_amount if receipt.data else "",
            receipt.data.total if receipt.data else "",
            receipt.data.doc_type if receipt.data else "",
            receipt.data.confidence if receipt.data else "",
            receipt.original_name,
        ]
        for receipt in receipts
    ]
    return _write_csv(headers, rows)


def _persist_extracted_data(db: Session, receipt: Receipt, raw_text: str) -> None:
    extracted = extract_receipt(raw_text)
    payload = extracted.model_dump()
    line_items = payload.pop("line_items", [])

    if receipt.data is None:
        receipt.data = ReceiptDataRecord(receipt_id=receipt.id)
    for key, value in payload.items():
        setattr(receipt.data, key, value)
    receipt.data.raw_json = extracted.model_dump()
    receipt.line_items = [
        LineItemRecord(
            receipt_id=receipt.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total=item.total,
        )
        for item in extracted.line_items
    ]


def _persist_blank_data(receipt: Receipt, error_message: str) -> None:
    if receipt.data is None:
        receipt.data = ReceiptDataRecord(receipt_id=receipt.id)
    receipt.data.confidence = None
    receipt.data.raw_json = {"extraction_error": error_message}
    receipt.line_items = []


def _clean_comment_body(body: str) -> str:
    cleaned = body.strip()
    if not cleaned:
        raise HTTPException(422, "Comment cannot be blank")
    if len(cleaned) > 2000:
        raise HTTPException(422, "Comment is too long")
    return cleaned


def process_receipt(receipt_id: int) -> None:
    db = SessionLocal()
    try:
        receipt = db.get(Receipt, receipt_id)
        if not receipt:
            return

        receipt.status = "processing"
        receipt.error_message = None
        db.commit()

        with open(receipt.file_path, "rb") as file:
            content = file.read()

        if receipt.mime_type in IMAGE_TYPES:
            raw_text = image_to_text(content)
        elif receipt.mime_type == "application/pdf":
            raw_text = pdf_to_text(content)
        else:
            raise ValueError(f"Unsupported file type: {receipt.mime_type}")

        if not raw_text.strip():
            raise ValueError("No OCR text could be extracted from this file.")

        receipt.raw_text = raw_text
        try:
            _persist_extracted_data(db, receipt, raw_text)
            receipt.error_message = None
        except Exception as exc:
            _persist_blank_data(receipt, str(exc))
            receipt.error_message = f"Structured extraction skipped: {exc}"
        receipt.status = "done"
        receipt.processed_at = datetime.utcnow()
        db.commit()
    except Exception as exc:
        receipt = db.get(Receipt, receipt_id)
        if receipt:
            receipt.status = "error"
            receipt.error_message = str(exc)
            receipt.processed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post(
    "/clients/{client_id}/receipts/upload",
    response_model=ReceiptUploadResponse,
    status_code=201,
)
async def upload_receipts(
    client_id: int,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(..., description="Receipt, invoice, or bank document files"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _client_or_404(client_id, current_user.id, db)

    max_files = int(os.getenv("MAX_FILES_PER_UPLOAD", "50"))
    max_mb = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
    if len(files) > max_files:
        raise HTTPException(400, f"Too many files; max is {max_files}")

    target_dir = _upload_root() / str(current_user.id) / str(client_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    created: list[Receipt] = []
    for file in files:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(400, f"Unsupported file type: {file.content_type}")

        content = await file.read()
        if len(content) > max_mb * 1024 * 1024:
            raise HTTPException(413, f"{file.filename or 'File'} is too large (max {max_mb} MB)")

        ext = _extension(file.filename, file.content_type)
        stored_name = f"{uuid.uuid4().hex}{ext}"
        file_path = target_dir / stored_name
        file_path.write_bytes(content)

        receipt = Receipt(
            client_id=client_id,
            user_id=current_user.id,
            file_path=str(file_path),
            original_name=file.filename,
            mime_type=file.content_type,
            file_size_kb=max(1, round(len(content) / 1024)),
            status="pending",
        )
        db.add(receipt)
        created.append(receipt)

    db.commit()
    for receipt in created:
        db.refresh(receipt)
        background_tasks.add_task(process_receipt, receipt.id)

    return ReceiptUploadResponse(
        receipts=[
            ReceiptUploadItem(
                receipt_id=receipt.id,
                original_name=receipt.original_name,
                status=receipt.status,
            )
            for receipt in created
        ]
    )


@router.get("/clients/{client_id}/receipts", response_model=ReceiptsResponse)
def list_receipts(
    client_id: int,
    status: Optional[str] = None,
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    vendor: Optional[str] = None,
    doc_type: Optional[str] = None,
    vat_type: Optional[str] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _client_or_404(client_id, current_user.id, db)
    statement = _receipt_statement(
        client_id=client_id,
        user_id=current_user.id,
        status=status,
        month=month,
        vendor=vendor,
        doc_type=doc_type,
        vat_type=vat_type,
        min_total=min_total,
        max_total=max_total,
    )
    receipts = db.scalars(statement.order_by(Receipt.created_at.desc())).all()
    return ReceiptsResponse(receipts=receipts)


@router.get("/clients/{client_id}/export")
def export_receipts(
    client_id: int,
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    format: str = Query("generic", pattern=r"^(generic|qbo|xero)$"),
    vendor: Optional[str] = None,
    doc_type: Optional[str] = None,
    vat_type: Optional[str] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _client_or_404(client_id, current_user.id, db)
    statement = _receipt_statement(
        client_id=client_id,
        user_id=current_user.id,
        status="approved",
        month=month,
        vendor=vendor,
        doc_type=doc_type,
        vat_type=vat_type,
        min_total=min_total,
        max_total=max_total,
    )
    receipts = db.scalars(statement.order_by(Receipt.created_at.asc())).all()
    csv_text = _csv_for_receipts(receipts, format)
    filename_month = month or "all"
    filename = f"phlow-client-{client_id}-{format}-{filename_month}.csv"
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/clients/{client_id}/receipts/queue", response_model=ReceiptsResponse)
def review_queue(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _client_or_404(client_id, current_user.id, db)
    receipts = db.scalars(
        select(Receipt)
        .options(selectinload(Receipt.data), selectinload(Receipt.line_items), selectinload(Receipt.comments))
        .where(
            Receipt.client_id == client_id,
            Receipt.user_id == current_user.id,
            Receipt.status.in_(["pending", "processing", "done", "error"]),
        )
        .order_by(Receipt.created_at.asc())
    ).all()
    return ReceiptsResponse(receipts=receipts)


@router.get("/receipts/{receipt_id}", response_model=ReceiptPublic)
def get_receipt(
    receipt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _receipt_or_404(receipt_id, current_user.id, db)


@router.get("/receipts/{receipt_id}/comments", response_model=ReceiptCommentsResponse)
def list_receipt_comments(
    receipt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _receipt_or_404(receipt_id, current_user.id, db)
    comments = db.scalars(
        select(ReceiptComment)
        .where(ReceiptComment.receipt_id == receipt_id, ReceiptComment.user_id == current_user.id)
        .order_by(ReceiptComment.created_at.asc())
    ).all()
    return ReceiptCommentsResponse(comments=comments)


@router.post("/receipts/{receipt_id}/comments", response_model=ReceiptCommentPublic, status_code=201)
def create_receipt_comment(
    receipt_id: int,
    payload: ReceiptCommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receipt = _receipt_or_404(receipt_id, current_user.id, db)
    comment = ReceiptComment(
        receipt_id=receipt.id,
        client_id=receipt.client_id,
        user_id=current_user.id,
        author_type="bookkeeper",
        author_name=current_user.name,
        body=_clean_comment_body(payload.body),
        is_read_by_bookkeeper=True,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.post("/receipts/{receipt_id}/comments/read", response_model=ReceiptCommentsResponse)
def mark_receipt_comments_read(
    receipt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _receipt_or_404(receipt_id, current_user.id, db)
    comments = db.scalars(
        select(ReceiptComment)
        .where(ReceiptComment.receipt_id == receipt_id, ReceiptComment.user_id == current_user.id)
        .order_by(ReceiptComment.created_at.asc())
    ).all()
    changed = False
    for comment in comments:
        if comment.author_type == "client" and not comment.is_read_by_bookkeeper:
            comment.is_read_by_bookkeeper = True
            changed = True
    if changed:
        db.commit()
        for comment in comments:
            db.refresh(comment)
    return ReceiptCommentsResponse(comments=comments)


@router.post("/receipts/{receipt_id}/reprocess", response_model=ReceiptPublic)
def reprocess_receipt(
    receipt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receipt = _receipt_or_404(receipt_id, current_user.id, db)
    process_receipt(receipt.id)
    return _receipt_or_404(receipt.id, current_user.id, db)


@router.get("/receipts/{receipt_id}/file")
def get_receipt_file(
    receipt_id: int,
    token: str,
    db: Session = Depends(get_db),
):
    current_user = user_from_token(token, db)
    receipt = _receipt_or_404(receipt_id, current_user.id, db)
    path = Path(receipt.file_path)
    if not path.exists():
        raise HTTPException(404, "Receipt file not found")
    return FileResponse(
        path,
        media_type=receipt.mime_type,
        filename=receipt.original_name,
        content_disposition_type="inline",
    )


@router.get("/receipts/{receipt_id}/preview")
def get_receipt_preview(
    receipt_id: int,
    page: int = Query(1, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receipt = _receipt_or_404(receipt_id, current_user.id, db)
    path = Path(receipt.file_path)
    if not path.exists():
        raise HTTPException(404, "Receipt file not found")

    if receipt.mime_type in IMAGE_TYPES:
        return FileResponse(path, media_type=receipt.mime_type)
    if receipt.mime_type != "application/pdf":
        raise HTTPException(415, "Preview is only available for images and PDFs")

    try:
        with fitz.open(str(path)) as document:
            if page > len(document):
                raise HTTPException(404, "PDF page not found")
            pixmap = document.load_page(page - 1).get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            return Response(
                content=pixmap.tobytes("png"),
                media_type="image/png",
                headers={
                    "X-PDF-Page": str(page),
                    "X-PDF-Page-Count": str(len(document)),
                },
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Could not render PDF preview: {exc}") from exc


@router.patch("/receipts/{receipt_id}", response_model=ReceiptPublic)
def update_receipt(
    receipt_id: int,
    payload: ReceiptPatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receipt = _receipt_or_404(receipt_id, current_user.id, db)

    if payload.status is not None:
        if payload.status not in {"pending", "processing", "done", "error", "approved", "rejected"}:
            raise HTTPException(422, "Invalid receipt status")
        receipt.status = payload.status
        if payload.status in {"done", "approved", "rejected", "error"}:
            receipt.processed_at = datetime.utcnow()

    if payload.data is not None:
        data_payload = payload.data.model_dump()
        if receipt.data is None:
            receipt.data = ReceiptDataRecord(receipt_id=receipt.id, raw_json=data_payload)
        for key, value in data_payload.items():
            setattr(receipt.data, key, value)
        receipt.data.raw_json = data_payload

    if payload.line_items is not None:
        receipt.line_items = [
            LineItemRecord(
                receipt_id=receipt.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total=item.total,
            )
            for item in payload.line_items
        ]

    db.commit()
    db.refresh(receipt)
    return _receipt_or_404(receipt.id, current_user.id, db)
