# Phlow Handoff

## Current State

Stack:
- Frontend: Vue 3 + Vite, running on `http://127.0.0.1:5174`
- Backend: FastAPI + SQLAlchemy 2 + Alembic, running on `http://127.0.0.1:8001`
- Database: PostgreSQL (psycopg2-binary). SQLite still works for ad-hoc local testing because models use portable types, but production assumes Postgres
- Auth: JWT + bcrypt with mandatory email verification
- Email: SMTP via `app/email_service.py`; falls back to logging the verification link when `SMTP_HOST` is unset
- Portal notifications: best-effort SMTP email for new portal uploads and client comments; failures are logged and do not block uploads/comments
- File storage: local disk under `backend/uploads/`
- Migrations: Alembic (`backend/alembic/`); pre-Alembic databases are auto-stamped to head on startup with column backfills first

## Implemented

### Public/Product
- Phlow public pages
- Phlow product page aligned to PRD
- API docs page

### Auth
- Signup/login/verify-email frontend
- `POST /v1/auth/register` — sends verification email; does NOT return a token
- `POST /v1/auth/verify-email` — consumes the token from the email and returns the access token
- `POST /v1/auth/resend-verification`
- `POST /v1/auth/login` — rejects unverified users with a clear error
- `GET /v1/auth/me`
- JWT stored in `localStorage`
- Protected `/app` routes
- `users` table carries `is_verified`, `verification_token`, `verification_token_expires_at`, `verification_sent_at`
- `app/email_service.py` sends HTML verification emails via SMTP; in dev, missing SMTP config logs the verification link to stdout

### Client Workspace
- `Client` model
- Client CRUD API:
  - `GET /v1/clients`
  - `POST /v1/clients`
  - `GET /v1/clients/{id}`
  - `PUT /v1/clients/{id}`
  - `DELETE /v1/clients/{id}`
- Client metrics API:
  - `GET /v1/clients/metrics`
- Client dashboard
- Create client page
- Client detail page
- Dashboard cards show real counts for unprocessed invoices, unreconciled bank entries, missing/outstanding 2307s, and total open work
- App header keeps the Phlow brand across public and `/app` routes
- Client detail metadata is collapsed by default so upload and workflow actions stay above the fold
- Client detail uses compact upload/workflow/portal panels with hover/focus tooltips for helper copy and a tab-like workflow navigation row
- Client detail uses "Back to workspace" with a Yes/No confirmation modal before returning to `/app`; workflow tabs keep direct "Back to client" links

### Receipt/Invoice Workflow
- Receipt models: `receipts`, `receipt_data`, `line_items`
- Batch upload:
  - `POST /v1/clients/{id}/receipts/upload`
- Receipt list/detail:
  - `GET /v1/clients/{id}/receipts`
  - `GET /v1/receipts/{id}`
- Receipt reprocess/retry:
  - `POST /v1/receipts/{id}/reprocess`
- Protected file access:
  - `GET /v1/receipts/{id}/file` (Authorization header)
- Protected image/PDF preview:
  - `GET /v1/receipts/{id}/preview` (Authorization header)
- OCR/OpenAI extraction for image and PDF files
- PDFs are rendered with PyMuPDF for OCR and previewed in-app through the protected preview route
- PH/BIR extraction fields:
  - vendor TIN
  - OR/SI number
  - VAT type
  - VATable amount
  - VAT amount
  - document type
  - confidence

### Review Queue
- `GET /v1/clients/{id}/receipts/queue`
- `PATCH /v1/receipts/{id}`
- `/app/clients/:id/review`
- Side-by-side document and editable fields
- Approve/reject flow
- Retry OCR action for failed receipts
- Confidence highlighting
- Enter-to-approve shortcut
- Review page uses a fixed-height workbench layout on desktop
- Queue, document/PDF preview, and extracted-field panes scroll independently with scroll chaining contained
- PDF receipts preview as app-rendered page images so the native browser PDF download toolbar is not shown; image receipts keep app-level zoom controls
- Multi-page PDFs expose page navigation in the review preview using the protected preview endpoint's page-count headers
- Document previews are anchored to the top center so zoomed-out PDFs do not float below blank space
- Review queue cards clamp long file names so PDF names do not overflow the sidebar
- Empty review queue shows an "You're all caught up" state with upload/archive actions
- Review, archive, reconciliation, and compliance workflow pages now share the dark Client Detail workspace styling, compact headers, polished panels, and consistent form/table controls
- Global date/month picker icons are brightened for the dark theme

### Archive/Export
- `/app/clients/:id/archive`
- Filter approved receipts by:
  - month
  - vendor
  - document type
  - VAT type
  - amount range
- CSV export:
  - `GET /v1/clients/{id}/export`
  - formats: `generic`, `qbo`, `xero`
- Archive read-only detail modal:
  - app-rendered image/PDF preview
  - PDF page navigation
  - zoom controls
  - fixed popup header with internal detail scrolling
  - extracted BIR fields
  - line items
  - raw OCR text
- Protected receipt previews are served through app-rendered image/PDF page previews; 2307 file responses are served inline for browser preview

### Client Portal
- `ClientUploadLink` model with token, optional label, expires_at, max_uploads, uploads_count, revoked_at, last_used_at
- `ReceiptComment` model for receipt-level clarification threads
- Receipts uploaded through a portal link store `upload_link_id` so public portal receipt/comment access is token-scoped
- Auth admin APIs:
  - `POST /v1/clients/{id}/upload-links`
  - `GET /v1/clients/{id}/upload-links`
  - `DELETE /v1/clients/{id}/upload-links/{link_id}`
- Public APIs (no auth, token-scoped):
  - `GET /v1/portal/{token}` — returns client name, label, remaining uploads, expiry
  - `POST /v1/portal/{token}/upload` — accepts JPEG/PNG/WebP/PDF, queues for OCR
  - `GET /v1/portal/{token}/receipts`
  - `GET /v1/portal/{token}/receipts/{receipt_id}/comments`
  - `POST /v1/portal/{token}/receipts/{receipt_id}/comments`
- Authenticated bookkeeper comment APIs:
  - `GET /v1/receipts/{receipt_id}/comments`
  - `POST /v1/receipts/{receipt_id}/comments`
  - `POST /v1/receipts/{receipt_id}/comments/read`
- Client detail page exposes link create/copy/revoke, unread portal comment counts, and a comment/reply modal
- `/portal/:token` is now a compact dashboard with upload first, uploaded receipts below, and receipt comment threads
- Public route renders without app navigation chrome (`meta.publicChrome`)
- New portal uploads and client comments send best-effort email notifications to the owning bookkeeper

### Bank Reconciliation
- Models:
  - `bank_transactions`
  - `reconciliations`
- Bank CSV import:
  - `POST /v1/clients/{id}/bank/import`
- Bank CSV template presets:
  - Generic
  - BDO
  - BPI
  - Metrobank
  - UnionBank
- Bank import skips likely duplicate rows and returns row-level parse errors for bad amount rows
- Bank transaction list:
  - `GET /v1/clients/{id}/bank/transactions`
- Match suggestions:
  - `GET /v1/clients/{id}/bank/transactions/{tx_id}/matches`
- Match logic:
  - exact amount
  - 1%/2% withholding variance
  - date within 7 days
  - vendor similarity
- Reconcile action:
  - `POST /v1/clients/{id}/bank/transactions/{tx_id}/reconcile`
- Reconciled transaction list:
  - `GET /v1/clients/{id}/bank/reconciliations`
- Manual receipt match search:
  - `GET /v1/clients/{id}/bank/transactions/{tx_id}/manual-matches?q=...`
- Undo/unmatch:
  - `DELETE /v1/clients/{id}/bank/reconciliations/{reconciliation_id}`
- Bulk categorization:
  - `PATCH /v1/clients/{id}/bank/transactions/category`
- `/app/clients/:id/reconciliation` includes unreconciled entries, suggested matches, manual search, reconciled entries, undo match, and Form 2307 follow-up
- Bank reconciliation uses compact section eyebrows, hover/focus tooltips for helper copy, a styled CSV file picker, and contained import controls to avoid overflow

### Form 2307 Tracking
- Reconciliation-level 2307 status fields:
  - `missing`
  - `requested`
  - `received`
  - `attached`
- Reconciliation-level 2307 workflow metadata:
  - requested timestamp
  - received timestamp
  - attachment upload timestamp
  - follow-up notes
- Alembic manages schema; pre-Alembic databases are auto-stamped to head on startup, with the legacy 2307-column patch applied first to backfill any gap
- 2307 follow-up APIs:
  - `GET /v1/clients/{id}/bank/reconciliations?requires_2307=true`
  - `GET /v1/clients/{id}/bank/reconciliations?requires_2307=true&form_2307_status=requested`
  - `PATCH /v1/clients/{id}/bank/reconciliations/{reconciliation_id}/2307` for status and notes
  - `POST /v1/clients/{id}/bank/reconciliations/{reconciliation_id}/2307/file`
  - `GET /v1/clients/{id}/bank/reconciliations/{reconciliation_id}/2307/file` (Authorization header)
- Status transitions automatically stamp requested/received dates, and `attached` requires a file upload
- `/app/clients/:id/reconciliation` now includes a Form 2307 follow-up panel for withholding-variance matches, status filtering, timestamps, notes, and attachment links
- 2307 attachments are stored locally under the upload root and support PDF/JPEG/PNG/WebP

## Important Files

Backend:
- `backend/app/main.py`
- `backend/app/database.py`
- `backend/app/models.py`
- `backend/app/auth.py`
- `backend/app/auth_routes.py`
- `backend/app/email_service.py`
- `backend/app/client_routes.py`
- `backend/app/receipt_routes.py`
- `backend/app/bank_routes.py`
- `backend/app/compliance_routes.py`
- `backend/app/portal_routes.py`
- `backend/app/schemas.py`
- `backend/app/extract.py`
- `backend/app/ocr.py`
- `backend/alembic/env.py`
- `backend/alembic/versions/` (`5c15a1fe35aa` baseline, `c6cda2519628` upload links, `e864ea5fcdb6` user verification, `f43a9d2b7c10` receipt comments)

Frontend:
- `frontend/src/api.js`
- `frontend/src/main.js`
- `frontend/src/App.vue` (gates app chrome via `meta.publicChrome`)
- `frontend/src/views/Login.vue`
- `frontend/src/views/Signup.vue`
- `frontend/src/views/VerifyEmail.vue`
- `frontend/src/views/AppDashboard.vue`
- `frontend/src/views/ClientNew.vue`
- `frontend/src/views/ClientDetail.vue`
- `frontend/src/views/ClientReview.vue`
- `frontend/src/views/ClientArchive.vue`
- `frontend/src/views/ClientReconciliation.vue`
- `frontend/src/views/ClientCompliance.vue`
- `frontend/src/views/ClientPortalUpload.vue` (public, no app chrome)
- `frontend/src/style.css` (global app tokens and dark date/month picker indicator styling)

## OCR Notes

- `pytesseract` is a Python wrapper only; the native `tesseract` executable must be installed locally.
- `TESSERACT_CMD` in `backend/.env` can point to `tesseract.exe` when it is not on PATH.
- PyMuPDF handles PDF text extraction and PDF/page preview rendering. Scanned PDF pages still require Tesseract after PyMuPDF renders them to images.
- If Tesseract is missing, receipt processing can show `tesseract is not installed or it's not in your PATH` in the review queue.

## Known Gaps / Needs Completion

High priority:
- PostgreSQL production validation
- Broaden automated regression tests beyond the current API coverage, especially OCR processing success/error paths, bank CSV import edge cases, and receipt review/export filters

### BIR Compliance
- `GET /v1/clients/{id}/exports/slsp?quarter=YYYY-Qn` — Summary List of Purchases CSV grouped by supplier TIN
- `GET /v1/clients/{id}/exports/sawt?quarter=YYYY-Qn` — Summary Alphalist of Withholding Taxes CSV from 2307-flagged reconciliations
- `GET /v1/clients/{id}/exports/journal?month=YYYY-MM` — 4-column journal CSV with input VAT split when present
- `GET /v1/clients/{id}/compliance/deadlines` — Static schedule of monthly/quarterly BIR forms in the next 120 days
- `/app/clients/:id/compliance` page surfaces the four exports and a deadline table

## Recommended Next Product Slices

1. Billing/limits
   - Receipt limits per plan
   - Paymongo integration
   - Billing status/settings page

2. Deployment
   - Dockerfile/backend
   - Dockerfile/frontend or static build
   - docker-compose with DB
   - environment docs
   - production CORS/secret handling

3. Regression test suite
   - Current backend API coverage: reconciliation matching and 2307 tracking, PDF multi-page preview, portal comments and notification path, dashboard metrics, upload limits, BIR export CSVs/deadlines, auth/email verification
   - Next coverage candidates: OCR processing success/error paths, bank CSV import edge cases, receipt review edits/export filters

## Current Test Commands

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m pytest tests
```

Frontend:

```powershell
cd frontend
npm.cmd run build
```

## Current Dev Servers

```text
Backend:  http://127.0.0.1:8001
Frontend: http://127.0.0.1:5174
```

Frontend must be started with:

```powershell
$env:VITE_API_BASE_URL='http://127.0.0.1:8001/v1'
npm.cmd run dev -- --host 127.0.0.1 --port 5174
```
