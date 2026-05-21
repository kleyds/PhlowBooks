import json
import os

from openai import OpenAI

from app.schemas import ReceiptData

SYSTEM_PROMPT = """You extract structured data from Philippine receipt, invoice, wallet, and bank OCR text.
The OCR text may be noisy or contain errors. Make best-effort guesses for fields you can identify.
Use null for any field you cannot determine.

Rules:
- Dates must be ISO format YYYY-MM-DD.
- Currency must be a 3-letter ISO 4217 code. Default to PHP for Philippine documents.
- Numbers must be plain numeric values, never strings, never with currency symbols.
- Extract BIR-specific fields when visible: vendor_tin, or_number, si_number, atp_number, vat_type, vatable_amount, vat_amount.
- vat_type must be one of: vatable, zero_rated, exempt, non_vat.
- doc_type must be one of: official_receipt, sales_invoice, gcash, maya, bank_statement, other.
- For GCash, Maya, or bank screenshots/statements, focus on payee/vendor, date, amount, reference/OR/SI numbers if visible, doc_type, and confidence.
- confidence is a 0.0 to 1.0 self-assessment of extraction quality.
- line_items should reflect each purchased item if visible; empty array if not parseable.

Return JSON only, matching the requested schema."""


def extract_receipt(raw_text: str) -> ReceiptData:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY env var not set")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    schema_hint = json.dumps(ReceiptData.model_json_schema(), indent=2)
    user_msg = (
        f"OCR text:\n```\n{raw_text}\n```\n\n"
        f"Return JSON matching this schema:\n```json\n{schema_hint}\n```"
    )

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    payload = json.loads(response.choices[0].message.content or "{}")
    return ReceiptData(**payload)
