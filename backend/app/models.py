from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    receipts_used_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    billing_period_start: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    paymongo_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    paymongo_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    verification_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verification_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    clients: Mapped[list["Client"]] = relationship(back_populates="owner")
    receipts: Mapped[list["Receipt"]] = relationship(back_populates="owner")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tin: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    software: Mapped[str] = mapped_column(String(50), default="other", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    owner: Mapped[User] = relationship(back_populates="clients")
    receipts: Mapped[list["Receipt"]] = relationship(back_populates="client")
    bank_transactions: Mapped[list["BankTransaction"]] = relationship(back_populates="client")


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    upload_link_id: Mapped[Optional[int]] = mapped_column(ForeignKey("client_upload_links.id"), index=True, nullable=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size_kb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    client: Mapped[Client] = relationship(back_populates="receipts")
    owner: Mapped[User] = relationship(back_populates="receipts")
    data: Mapped[Optional["ReceiptDataRecord"]] = relationship(
        back_populates="receipt",
        cascade="all, delete-orphan",
        uselist=False,
    )
    line_items: Mapped[list["LineItemRecord"]] = relationship(
        back_populates="receipt",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["ReceiptComment"]] = relationship(
        back_populates="receipt",
        cascade="all, delete-orphan",
        order_by="ReceiptComment.created_at.asc()",
    )
    audit_logs: Mapped[list["ReceiptAuditLog"]] = relationship(
        back_populates="receipt",
        cascade="all, delete-orphan",
        order_by="ReceiptAuditLog.created_at.desc()",
    )

    @property
    def comment_count(self) -> int:
        return len(self.comments)

    @property
    def unread_portal_comment_count(self) -> int:
        return len(
            [
                comment
                for comment in self.comments
                if comment.author_type == "client" and not comment.is_read_by_bookkeeper
            ]
        )

    @property
    def latest_comment(self) -> Optional["ReceiptComment"]:
        if not self.comments:
            return None
        return self.comments[-1]


class ReceiptDataRecord(Base):
    __tablename__ = "receipt_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"), unique=True, nullable=False)
    vendor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vendor_tin: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    or_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    si_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    atp_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), default="PHP", nullable=True)
    subtotal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tax: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vat_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    vatable_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vat_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    doc_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    receipt: Mapped[Receipt] = relationship(back_populates="data")

    @property
    def vat_sanity_status(self) -> Optional[str]:
        if self.vatable_amount is None or self.vat_amount is None:
            return None
        if (self.vat_type or "").lower() in {"zero_rated", "exempt", "non_vat"} and self.vat_amount == 0:
            return None
        expected = round(self.vatable_amount * 0.12, 2)
        difference = round(self.vat_amount - expected, 2)
        return "warning" if abs(difference) > 1 else "ok"

    @property
    def vat_sanity_message(self) -> Optional[str]:
        if self.vat_sanity_status != "warning" or self.vatable_amount is None or self.vat_amount is None:
            return None
        expected = round(self.vatable_amount * 0.12, 2)
        difference = round(self.vat_amount - expected, 2)
        return f"Expected VAT around {expected:.2f}; captured {self.vat_amount:.2f} ({difference:+.2f})."


class LineItemRecord(Base):
    __tablename__ = "line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    receipt: Mapped[Receipt] = relationship(back_populates="line_items")


class ReceiptComment(Base):
    __tablename__ = "receipt_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"), index=True, nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    author_type: Mapped[str] = mapped_column(String(20), nullable=False)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read_by_bookkeeper: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    receipt: Mapped[Receipt] = relationship(back_populates="comments")
    client: Mapped[Client] = relationship()
    owner: Mapped[User] = relationship()


class ReceiptAuditLog(Base):
    __tablename__ = "receipt_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"), index=True, nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    field_name: Mapped[str] = mapped_column(String(120), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    receipt: Mapped[Receipt] = relationship(back_populates="audit_logs")
    client: Mapped[Client] = relationship()
    actor: Mapped[User] = relationship()

    @property
    def actor_name(self) -> Optional[str]:
        return self.actor.name if self.actor else None


class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transaction_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String(10), default="outflow", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="unreconciled", nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    client: Mapped[Client] = relationship(back_populates="bank_transactions")


class Reconciliation(Base):
    __tablename__ = "reconciliations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"), index=True, nullable=False)
    bank_transaction_id: Mapped[int] = mapped_column(ForeignKey("bank_transactions.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="matched", nullable=False)
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    requires_2307: Mapped[str] = mapped_column(String(5), default="false", nullable=False)
    form_2307_status: Mapped[str] = mapped_column(String(20), default="missing", nullable=False)
    form_2307_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    form_2307_original_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    form_2307_mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    form_2307_uploaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    form_2307_requested_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    form_2307_received_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    form_2307_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    receipt: Mapped[Receipt] = relationship()
    bank_transaction: Mapped[BankTransaction] = relationship()

    @property
    def has_form_2307_file(self) -> bool:
        return bool(self.form_2307_file_path)


class ClientUploadLink(Base):
    __tablename__ = "client_upload_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    max_uploads: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    uploads_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    client: Mapped[Client] = relationship()
