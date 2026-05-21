from __future__ import annotations

import csv
import io

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Client, Receipt, ReceiptDataRecord, User


def _csv_rows(response) -> list[dict[str, str]]:
    assert response.headers["content-type"].startswith("text/csv")
    return list(csv.DictReader(io.StringIO(response.text)))


def _receipt_with_data(db: Session, client: Client, user: User) -> Receipt:
    receipt = Receipt(
        client_id=client.id,
        user_id=user.id,
        file_path="/tmp/trust-layer-receipt.pdf",
        original_name="trust-layer-receipt.pdf",
        mime_type="application/pdf",
        file_size_kb=1,
        status="done",
    )
    db.add(receipt)
    db.flush()
    db.add(
        ReceiptDataRecord(
            receipt_id=receipt.id,
            vendor="Old Supplier",
            vendor_tin="111-222-333-000",
            or_number="OR-OLD",
            si_number="SI-OLD",
            atp_number="ATP-OLD",
            date="2026-05-01",
            currency="PHP",
            vat_type="vatable",
            vatable_amount=1000.0,
            vat_amount=120.0,
            total=1120.0,
            doc_type="official_receipt",
            confidence=0.95,
        )
    )
    db.commit()
    db.refresh(receipt)
    return receipt


def test_receipt_patch_tracks_atp_vat_warning_and_audit_logs(
    api_client: TestClient,
    db_session: Session,
    client_record: Client,
    current_user: User,
):
    receipt = _receipt_with_data(db_session, client_record, current_user)

    response = api_client.patch(
        f"/v1/receipts/{receipt.id}",
        json={
            "status": "approved",
            "data": {
                "vendor": "New Supplier",
                "vendor_tin": "111-222-333-000",
                "or_number": "OR-NEW",
                "si_number": "SI-OLD",
                "atp_number": "ATP-NEW",
                "date": "2026-05-01",
                "currency": "PHP",
                "subtotal": None,
                "tax": None,
                "vat_type": "vatable",
                "vatable_amount": 1000.0,
                "vat_amount": 100.0,
                "total": 1100.0,
                "doc_type": "official_receipt",
                "confidence": 0.95,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "approved"
    assert payload["data"]["atp_number"] == "ATP-NEW"
    assert payload["data"]["vat_sanity_status"] == "warning"
    assert "Expected VAT around 120.00" in payload["data"]["vat_sanity_message"]

    audit_response = api_client.get(f"/v1/receipts/{receipt.id}/audit-logs")

    assert audit_response.status_code == 200
    audit_logs = audit_response.json()["audit_logs"]
    changes = {entry["field_name"]: entry for entry in audit_logs}
    assert changes["receipt.status"]["old_value"] == "done"
    assert changes["receipt.status"]["new_value"] == "approved"
    assert changes["receipt_data.vendor"]["old_value"] == "Old Supplier"
    assert changes["receipt_data.vendor"]["new_value"] == "New Supplier"
    assert changes["receipt_data.atp_number"]["old_value"] == "ATP-OLD"
    assert changes["receipt_data.atp_number"]["new_value"] == "ATP-NEW"
    assert changes["receipt_data.vat_amount"]["old_value"] == "120.0"
    assert changes["receipt_data.vat_amount"]["new_value"] == "100.0"
    assert all(entry["actor_name"] == current_user.name for entry in audit_logs)


def test_generic_receipt_export_includes_atp_number(
    api_client: TestClient,
    db_session: Session,
    client_record: Client,
    current_user: User,
):
    receipt = _receipt_with_data(db_session, client_record, current_user)
    receipt.status = "approved"
    db_session.commit()

    response = api_client.get(f"/v1/clients/{client_record.id}/export", params={"format": "generic"})

    assert response.status_code == 200
    rows = _csv_rows(response)
    assert rows[0]["atp_number"] == "ATP-OLD"
