# PhlowBooks

Bookkeeping infrastructure for Filipino bookkeepers, accountants, and SMBs.

This monorepo contains:

- `frontend/` - PhlowBooks marketing site and web app.
- `backend/` - PhlowBooks API built with FastAPI, SQLAlchemy on PostgreSQL, Tesseract OCR, and OpenAI extraction.
- `PHLOWBOOKS_HANDOFF.md` - implementation handoff and next-work checklist.

## PhlowBooks

PhlowBooks is bookkeeping infrastructure for Filipino accounting firms. It currently supports:

- Bookkeeper signup with email verification + JWT login.
- Multi-client workspace.
- Batch receipt/invoice upload.
- Image/PDF OCR and PH/BIR-aware OpenAI extraction.
- Review queue with editable extracted fields.
- Receipt archive with filters and read-only modal document detail.
- CSV export for Generic, QuickBooks, and Xero formats.
- Bank CSV import.
- PH bank CSV template presets for Generic, BDO, BPI, Metrobank, and UnionBank imports.
- Bank import duplicate skipping and row-level error reporting.
- Reconciliation match suggestions, including 1%/2% withholding variance detection.
- Reconciled transaction view with undo/unmatch and manual receipt search.
- Form 2307 status tracking and attachment workflow.
- Dashboard metrics for unprocessed invoices, unreconciled bank entries, and missing 2307s.
- Bulk bank transaction categorization.
- BIR compliance exports: SLSP, SAWT, 4-column journal, upcoming deadlines.
- Client portal: tokenized public upload links, mobile-first upload page, expiry/limit/revoke controls, receipt comments, and bookkeeper replies.
- Portal notifications for new client uploads and portal comments via best-effort SMTP email.
- Unified dark workflow UI across review, archive, bank reconciliation, and BIR compliance.
- Client homepage "Back to workspace" confirmation; workflow tabs keep direct "Back to client" navigation.

PDF files are stored and previewed in-app as rendered page images with page navigation. PyMuPDF extracts embedded PDF text and renders scanned PDF pages; Tesseract OCR is required for image OCR and scanned PDF page OCR.

## Prerequisites

1. Python 3.13 recommended.
2. Node.js 20+.
3. PostgreSQL 14+ running locally (or any reachable Postgres instance).
   - macOS: `brew install postgresql@16 && brew services start postgresql@16`
   - Linux: `sudo apt install postgresql`
   - Windows: install via the EnterpriseDB installer.
   - Create a database and role, e.g.:
     ```sql
     CREATE ROLE phlowbooks WITH LOGIN PASSWORD 'phlowbooks';
     CREATE DATABASE phlowbooks OWNER phlowbooks;
     ```
4. Tesseract OCR.
   - Windows: install from UB-Mannheim builds and set `TESSERACT_CMD` if it is not on PATH.
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`
   - `pytesseract` is only the Python wrapper. The native `tesseract` executable must also be installed or OCR will fail with a PATH error.
5. OpenAI API key for extraction.
6. SMTP credentials for sending verification emails (Gmail, SendGrid, Mailgun, etc.). For Gmail, use an [app password](https://support.google.com/accounts/answer/185833) and set `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`.
7. PyMuPDF is installed from `backend/requirements.txt` for PDF OCR; no Poppler install is required.

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env`:

```text
APP_ENV=development
SECRET_KEY=<random 32-byte hex>
API_KEY=<legacy-api-key>
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
TESSERACT_CMD=
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=20
MAX_FILES_PER_UPLOAD=50

# PostgreSQL is required.
DATABASE_URL=postgresql+psycopg2://phlowbooks:phlowbooks@localhost:5432/phlowbooks

# SMTP for verification emails. With Gmail, SMTP_USER is your address
# and SMTP_PASSWORD is a 16-character Google App Password.
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
SMTP_FROM=you@gmail.com
SMTP_USE_TLS=true
FRONTEND_BASE_URL=http://localhost:5174
```

> PostgreSQL is required. The backend uses `psycopg2-binary`; provision Postgres
> before starting the backend and set `DATABASE_URL` accordingly:
>
> ```text
> DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/phlowbooks
> ```

> If `SMTP_HOST` is unset, registration still succeeds and the verification link is
> printed to the backend log so you can verify accounts during local development.

Run database migrations (also runs automatically on app startup):

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

To create a new migration after editing `app/models.py`:

```powershell
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe change"
```

Run the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Run backend regression tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

Current regression coverage includes reconciliation and Form 2307 tracking, PDF page previews, portal comments, dashboard metrics, upload limits, BIR export CSVs/deadlines, and auth/email verification.

API docs:

```text
http://127.0.0.1:8001/docs
```

## Frontend Setup

```powershell
cd frontend
npm install
$env:VITE_API_BASE_URL='http://127.0.0.1:8001/v1'
npm.cmd run dev -- --host 127.0.0.1 --port 5174
```

Visit:

```text
http://127.0.0.1:5174
```

Key routes:

- `/`
- `/products`
- `/phlowbooks`
- `/docs`
- `/login`
- `/signup`
- `/app`
- `/app/clients/new`
- `/app/clients/:id`
- `/app/clients/:id/review`
- `/app/clients/:id/archive`
- `/app/clients/:id/reconciliation`
- `/app/clients/:id/compliance`
- `/portal/:token` (public client upload page)

Client navigation behavior:

- `/app/clients/:id` uses `Back to workspace` and asks for Yes/No confirmation before returning to `/app`.
- Workflow routes such as review, archive, reconciliation, and compliance use `Back to client` and navigate directly within the selected client.

## Verification

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m compileall app
```

Frontend:

```powershell
cd frontend
npm.cmd run build
```

Recent UI verification should include the client homepage confirmation modal, workflow tab navigation labels, global date/month picker icons on dark inputs, and the bank reconciliation CSV import layout.

## Important API Areas

Auth:

- `POST /v1/auth/register` (sends verification email; does not return a token)
- `POST /v1/auth/verify-email` (consumes the token from the email and returns an access token)
- `POST /v1/auth/resend-verification`
- `POST /v1/auth/login` (rejects unverified users)
- `GET /v1/auth/me`

Clients:

- `GET /v1/clients`
- `GET /v1/clients/metrics`
- `POST /v1/clients`
- `GET /v1/clients/{id}`
- `PUT /v1/clients/{id}`
- `DELETE /v1/clients/{id}`

Receipts:

- `POST /v1/clients/{id}/receipts/upload`
- `GET /v1/clients/{id}/receipts`
- `GET /v1/clients/{id}/receipts/queue`
- `GET /v1/receipts/{id}`
- `POST /v1/receipts/{id}/reprocess`
- `GET /v1/receipts/{id}/file` (Authorization header)
- `GET /v1/receipts/{id}/preview?page=1` (Authorization header; PDFs return page-count headers)
- `PATCH /v1/receipts/{id}`
- `GET /v1/receipts/{id}/comments`
- `POST /v1/receipts/{id}/comments`
- `POST /v1/receipts/{id}/comments/read`

Exports:

- `GET /v1/clients/{id}/export?format=generic|qbo|xero`
- `GET /v1/clients/{id}/exports/slsp?quarter=YYYY-Qn`
- `GET /v1/clients/{id}/exports/sawt?quarter=YYYY-Qn`
- `GET /v1/clients/{id}/exports/journal?month=YYYY-MM`
- `GET /v1/clients/{id}/compliance/deadlines`

Client portal:

- `POST /v1/clients/{id}/upload-links`
- `GET /v1/clients/{id}/upload-links`
- `DELETE /v1/clients/{id}/upload-links/{link_id}`
- `GET /v1/portal/{token}` (public)
- `POST /v1/portal/{token}/upload` (public)
- `GET /v1/portal/{token}/receipts` (public)
- `GET /v1/portal/{token}/receipts/{receipt_id}/comments` (public)
- `POST /v1/portal/{token}/receipts/{receipt_id}/comments` (public)

Bank/reconciliation:

- `POST /v1/clients/{id}/bank/import?bank_template=generic|bdo|bpi|metrobank|unionbank`
- `GET /v1/clients/{id}/bank/transactions`
- `GET /v1/clients/{id}/bank/transactions/{tx_id}/matches`
- `GET /v1/clients/{id}/bank/transactions/{tx_id}/manual-matches?q=...`
- `POST /v1/clients/{id}/bank/transactions/{tx_id}/reconcile`
- `GET /v1/clients/{id}/bank/reconciliations`
- `DELETE /v1/clients/{id}/bank/reconciliations/{reconciliation_id}`
- `GET /v1/clients/{id}/bank/reconciliations?requires_2307=true`
- `PATCH /v1/clients/{id}/bank/reconciliations/{reconciliation_id}/2307`
- `POST /v1/clients/{id}/bank/reconciliations/{reconciliation_id}/2307/file`
- `GET /v1/clients/{id}/bank/reconciliations/{reconciliation_id}/2307/file` (Authorization header)
- `PATCH /v1/clients/{id}/bank/transactions/category`

Legacy endpoint:

- `POST /v1/extract-receipt`

## Next Work

See `PHLOWBOOKS_HANDOFF.md` for the fuller handoff. High-priority next slices:

- PostgreSQL production validation.
- OCR processing success/error regression tests.
- Bank CSV import and receipt review/export filter regression tests.
- Docker deployment setup.
