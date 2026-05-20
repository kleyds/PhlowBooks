# Product Requirements Document
## PhlowBooks — Bookkeeping Infrastructure for Filipino Accounting Firms
**Version:** 0.1 · **Status:** Pre-MVP · **Product:** PhlowBooks (`phlowbooks.app`)

---

## 1. Overview

PhlowBooks is a hosted SaaS product that turns receipts, invoices, and bank statements into clean accounting entries for Filipino bookkeepers and accounting firms. It replaces the manual process of typing receipts one-by-one into QuickBooks, Xero, or JuanTax.

**Tagline:** *"Stop typing resibos."*

**Live site (frontend):** `phlowbooks.app`
**API base URL (backend):** `api.phlowbooks.app`
**GitHub:** `https://github.com/kleyds/phlowbooks` (private)

---

## 2. Problem

Filipino bookkeepers spend hours every week:

1. Manually re-typing receipts their clients send via Viber, Messenger, or email.
2. Parsing BIR-specific fields (TIN, OR/SI #, ATP) that global tools like Hubdoc/Dext don't extract.
3. Reading handwritten receipts from sari-sari stores, palengke vendors, and jeepney drivers that cloud OCR fails on.
4. Manually reconciling GCash, Maya, BPI, BDO, and Metrobank PDFs — all in different formats.

Global tools (Hubdoc, Dext, Textract) are priced in USD, built for North American workflows, and don't handle PH-specific document formats.

---

## 3. Target Customer

**Primary:** Filipino bookkeepers and small accounting firms (1–20 staff).
- Currently use QuickBooks Online, Xero, JuanTax, or Excel.
- Manage 5–50 SMB clients each.
- Willing to pay ₱1,500–8,000/month for a tool that saves 10+ hours/week.

**Secondary (later):** SMB owners who are clients of the bookkeeper — they use a free "client portal" to upload receipts; their bookkeeper pays for the account.

**Not the target:** Enterprise companies, multinational firms, payroll bureaus.

---

## 4. Business Model

- **Subscription, peso-denominated, per-seat.**
- Payment processor: **Paymongo** or **Xendit** (PH-native, supports GCash/Maya/credit card).
- Pricing tiers (placeholder — validate with customers):

| Tier | Price | Receipts/mo | Clients | Users |
|---|---|---|---|---|
| Solo | ₱1,500 | 500 | 10 | 1 |
| Firm | ₱5,000 | 2,000 | Unlimited | 5 |
| Agency | ₱12,000 | 10,000 | Unlimited | Unlimited |
| Free client portal | ₱0 | — | — | — |

- **Client portal seats are always free** — bookkeeper pays, SMB clients upload for free.

---

## 5. Tech Stack

### Backend
- **Runtime:** Python 3.13
- **Framework:** FastAPI 0.115.x
- **ASGI server:** Uvicorn
- **OCR engine:** Tesseract (via `pytesseract`) + Pillow
- **AI extraction:** OpenAI `gpt-4o-mini` (receipt → structured JSON)
- **Database:** PostgreSQL 16 (via `SQLAlchemy` + `psycopg` 3)
- **Auth:** JWT (`python-jose`) + bcrypt password hashing — not yet installed
- **Queue (v1):** Redis + RQ — not yet installed
- **File storage (v0):** Local disk. (v1+: MinIO or S3-compatible)
- **Payments:** Paymongo (PH) or Xendit — not yet installed

### Frontend
- **Framework:** Vue 3.5 + Vite 5
- **Router:** Vue Router 4.4
- **Styling:** Scoped CSS (no Tailwind — custom CSS variables, dark theme)
- **HTTP client:** Native `fetch` — Axios not installed yet

### Infrastructure
- **v0:** Self-hosted on mini PC, domain `phlowbooks.app`
- **v1:** Cloudflare in front (TLS, DDoS protection, hides origin IP)
- **Reverse proxy:** Nginx or Caddy

---

## 6. Existing Codebase

### Directory structure
```
phlowbooks/
├── README.md
├── PRD.md                          ← this file
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   └── app/
│       ├── __init__.py
│       ├── main.py                 ← FastAPI app, CORS, router registration
│       ├── auth.py                 ← API key check (x-api-key header) — single hardcoded key
│       ├── routes.py               ← POST /v1/extract-receipt endpoint
│       ├── ocr.py                  ← Tesseract image → raw text
│       ├── extract.py              ← OpenAI raw text → ReceiptData JSON
│       └── schemas.py              ← Pydantic models: ReceiptData, LineItem, ExtractResponse
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js                 ← Vue app + Vue Router setup
        ├── style.css               ← Global CSS variables (dark theme)
        ├── App.vue                 ← Layout shell: Nav + <router-view> + footer
        ├── components/
        │   └── Nav.vue             ← Top nav: PhlowBooks brand + Platform/Docs/About links
        └── views/
            ├── Home.vue            ← PhlowBooks landing (/)
            ├── Products.vue        ← Platform overview (/products)
            ├── PhlowBooks.vue           ← PhlowBooks product page (/phlowbooks) — waitlist form
            ├── Docs.vue            ← PhlowBooks API docs (/docs)
            └── About.vue           ← Product/company about (/about)
```

### What's already working
- `POST /v1/extract-receipt` — upload a JPEG/PNG/WebP receipt, get back `raw_text` + structured `ReceiptData` (vendor, date, currency, subtotal, tax, total, line_items).
- Single hardcoded `API_KEY` auth via `x-api-key` header.
- Vue frontend with 5 routes: `/`, `/products`, `/phlowbooks`, `/docs`, `/about`.
- Waitlist email form on `/phlowbooks` (UI only — not wired to backend yet).

### Current schemas (`backend/app/schemas.py`)
```python
class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None

class ReceiptData(BaseModel):
    vendor: Optional[str]
    date: Optional[str]          # ISO YYYY-MM-DD
    currency: Optional[str]      # ISO 4217 (PHP, USD, ...)
    subtotal: Optional[float]
    tax: Optional[float]
    total: Optional[float]
    line_items: List[LineItem]

class ExtractResponse(BaseModel):
    raw_text: str
    data: ReceiptData
```

---

## 7. MVP Feature Scope

> Build exactly these 8 features. Nothing more. Ship, get 5 paying customers, then proceed to v1.

### Feature 1 — Bookkeeper Auth
- Email + password registration and login.
- Passwords hashed with bcrypt.
- JWT access token (7-day expiry) returned on login, stored in `localStorage`.
- JWT verified on all protected API routes via a FastAPI dependency.
- No OAuth, no SSO for MVP.

**Screens:** `/signup`, `/login`

**API endpoints:**
```
POST /v1/auth/register    { email, password, name } → { access_token, user }
POST /v1/auth/login       { email, password }       → { access_token, user }
GET  /v1/auth/me                                    → { user }
```

**DB table: `users`**
```sql
CREATE TABLE users (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(255) NOT NULL,
  email       VARCHAR(255) NOT NULL UNIQUE,
  password    VARCHAR(255) NOT NULL,   -- bcrypt hash
  plan        ENUM('free','solo','firm','agency') DEFAULT 'free',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### Feature 2 — Multi-Client Workspace
- A bookkeeper can create multiple clients (each client = one business they manage books for).
- All receipts, documents, and exports are scoped to a client.
- Client has: name, TIN (optional), industry (optional), accounting software preference.

**Screens:** `/app` (client list), `/app/clients/new`, `/app/clients/:id`

**API endpoints:**
```
GET    /v1/clients              → list bookkeeper's clients
POST   /v1/clients              { name, tin, industry, software } → client
GET    /v1/clients/:id          → client detail
PUT    /v1/clients/:id          → update client
DELETE /v1/clients/:id          → soft delete
```

**DB table: `clients`**
```sql
CREATE TABLE clients (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id     INT UNSIGNED NOT NULL,   -- bookkeeper who owns this client
  name        VARCHAR(255) NOT NULL,
  tin         VARCHAR(20),             -- e.g. 123-456-789-000
  industry    VARCHAR(100),
  software    ENUM('quickbooks','xero','juantax','excel','other') DEFAULT 'other',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted_at  DATETIME,                -- soft delete
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

### Feature 3 — Batch Receipt Upload
- Bookkeeper selects a client, then drags-and-drops or selects up to 50 files at once.
- Accepted formats: JPEG, PNG, WebP, PDF (single or multi-page).
- Each file is saved to disk (path: `uploads/{user_id}/{client_id}/{uuid}.{ext}`).
- Each file creates one `receipt` record with status `pending`.
- Upload returns immediately with a list of receipt IDs — extraction runs async (v0: background task; v1: RQ queue).

**API endpoints:**
```
POST /v1/clients/:id/receipts/upload   multipart, field: files[] → [{ receipt_id, status }]
GET  /v1/clients/:id/receipts          ?month=2026-05 → paginated receipt list
GET  /v1/receipts/:id                  → single receipt detail
```

**DB table: `receipts`**
```sql
CREATE TABLE receipts (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  client_id     INT UNSIGNED NOT NULL,
  user_id       INT UNSIGNED NOT NULL,
  file_path     VARCHAR(500) NOT NULL,
  original_name VARCHAR(255),
  mime_type     VARCHAR(50),
  file_size_kb  INT,
  status        ENUM('pending','processing','done','error') DEFAULT 'pending',
  raw_text      TEXT,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  processed_at  DATETIME,
  FOREIGN KEY (client_id) REFERENCES clients(id),
  FOREIGN KEY (user_id)   REFERENCES users(id)
);
```

---

### Feature 4 — PH-Tuned AI Extraction
- Extend existing OCR + OpenAI pipeline with BIR-specific fields.
- System prompt must explicitly ask for: `or_number`, `si_number`, `vendor_tin`, `vat_type`, `vatable_amount`, `vat_amount`.
- If the receipt is a GCash/Maya/bank screenshot, detect the document type and use a different extraction prompt.

**Extended schema (`ReceiptData`):**
```python
class ReceiptData(BaseModel):
    vendor: Optional[str]
    vendor_tin: Optional[str]       # Philippine TIN: XXX-XXX-XXX-XXX
    or_number: Optional[str]        # Official Receipt number
    si_number: Optional[str]        # Sales Invoice number
    date: Optional[str]             # ISO YYYY-MM-DD
    currency: Optional[str]         # PHP default
    vat_type: Optional[str]         # 'vatable' | 'zero_rated' | 'exempt' | 'non_vat'
    vatable_amount: Optional[float]
    vat_amount: Optional[float]     # typically 12% of vatable_amount
    total: Optional[float]
    line_items: List[LineItem]
    doc_type: Optional[str]         # 'official_receipt' | 'sales_invoice' | 'gcash' | 'maya' | 'bank_statement' | 'other'
    confidence: Optional[float]     # 0.0–1.0 self-assessed by model
```

**DB table: `receipt_data`**
```sql
CREATE TABLE receipt_data (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  receipt_id      INT UNSIGNED NOT NULL UNIQUE,
  vendor          VARCHAR(255),
  vendor_tin      VARCHAR(25),
  or_number       VARCHAR(100),
  si_number       VARCHAR(100),
  date            DATE,
  currency        CHAR(3) DEFAULT 'PHP',
  doc_type        VARCHAR(50),
  vat_type        VARCHAR(20),
  vatable_amount  DECIMAL(12,2),
  vat_amount      DECIMAL(12,2),
  total           DECIMAL(12,2),
  confidence      DECIMAL(3,2),
  raw_json        JSON,               -- full OpenAI response for debugging
  FOREIGN KEY (receipt_id) REFERENCES receipts(id)
);

CREATE TABLE line_items (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  receipt_id  INT UNSIGNED NOT NULL,
  description VARCHAR(500),
  quantity    DECIMAL(10,3),
  unit_price  DECIMAL(12,2),
  total       DECIMAL(12,2),
  FOREIGN KEY (receipt_id) REFERENCES receipts(id)
);
```

---

### Feature 5 — Review Queue
- The core UX: bookkeeper sees a two-panel view.
  - **Left panel:** original image (or PDF page rendered as image).
  - **Right panel:** extracted fields, all editable.
- One-click **Approve** marks receipt as `done`.
- One-click **Reject** marks as `error` and removes from queue.
- Keyboard shortcut: `Tab` moves between fields, `Enter` approves.
- Show a confidence indicator — low-confidence fields highlighted in amber.
- Show count: "12 of 47 remaining."

**Screen:** `/app/clients/:id/review`

**API endpoints:**
```
GET   /v1/clients/:id/receipts/queue     → receipts with status 'done'=false, ordered oldest first
PATCH /v1/receipts/:id                   { status, data: ReceiptData } → updated receipt
```

---

### Feature 6 — CSV Export
- Export all approved receipts for a client for a given month.
- Offer 3 CSV flavors: **QuickBooks Online**, **Xero**, **Generic**.
- QBO format: `Date, Description, Account, Debit, Credit, Memo, Name`.
- Xero format: `Date, Amount, Payee, Description, Reference, Account Code`.
- Generic format: all extracted fields, one row per receipt.

**Screen:** Export button on `/app/clients/:id` page, month selector.

**API endpoint:**
```
GET /v1/clients/:id/export?month=2026-05&format=qbo|xero|generic
→ Content-Type: text/csv, Content-Disposition: attachment
```

---

### Feature 7 — Receipts Archive
- All approved receipts stored and searchable per client.
- Filter by: month, vendor name, amount range, doc type, VAT type.
- Thumbnail grid view + list view toggle.
- Click receipt to open review panel in read-only mode.
- Receipts retained indefinitely (bookkeeper owns their data).

**Screen:** `/app/clients/:id/archive`

---

### Feature 8 — Billing (Subscription)
- Bookkeeper subscribes via Paymongo (GCash, Maya, credit card).
- Plan gates: free plan = 25 receipts/month. Paid = per-tier limits.
- If monthly receipt limit reached → show upgrade prompt, block new uploads.
- Webhook endpoint receives Paymongo events to update `users.plan`.

**API endpoints:**
```
POST /v1/billing/subscribe     { plan, payment_method_id } → { checkout_url }
POST /v1/billing/webhook       Paymongo webhook handler (raw body, verify signature)
GET  /v1/billing/status        → { plan, receipts_used, receipts_limit, renews_at }
```

**DB columns added to `users`:**
```sql
ALTER TABLE users ADD COLUMN receipts_used_this_month INT DEFAULT 0;
ALTER TABLE users ADD COLUMN billing_period_start DATE;
ALTER TABLE users ADD COLUMN paymongo_customer_id VARCHAR(100);
ALTER TABLE users ADD COLUMN paymongo_subscription_id VARCHAR(100);
```

---

## 8. v1 Features (after MVP)

Build these only after 10+ paying customers.

| # | Feature | Description |
|---|---|---|
| 9 | **Client portal** | Free per-client URL (`phlowbooks.app/c/{token}`). SMB owner uploads receipts directly. Bookkeeper gets them in their queue. No login required for client. |
| 10 | **Email-to-upload** | Unique inbound email per client (e.g. `abc123@in.phlowbooks.app`). Client forwards receipt emails. Attachments auto-enqueued. |
| 11 | **Bank statement parsing** | Upload BPI/BDO/Metrobank/GCash/Maya PDF statements. Extract transaction rows. Match against receipts. |
| 12 | **Auto-categorization** | Suggest expense category (Transport, Meals, Office Supplies, Utilities, etc.) from vendor name using OpenAI. Bookkeeper can override. |
| 13 | **VAT sanity check** | Flag receipts where `vat_amount ≠ vatable_amount × 0.12` (within ₱1 tolerance). |
| 14 | **Duplicate detection** | Hash file content on upload. Warn if same file was uploaded before for this client. |
| 15 | **Search** | Full-text search across vendor, OR number, amount for a client's archive. |
| 16 | **Audit log** | Log every field edit (who, what, when). Viewable per receipt. Required for BIR audit defence. |

---

## 9. Non-Goals (never build these)

- ❌ Payroll processing
- ❌ Tax return filing or BIR form submission
- ❌ General ledger / journal entries / chart of accounts
- ❌ Invoicing / billing to clients
- ❌ Inventory management
- ❌ Multi-currency conversion
- ❌ Financial reporting / P&L / balance sheets

PhlowBooks is a **receipt-to-entry feeder**. Accounting software (QBO, Xero, JuanTax) remains the system of record.

---

## 10. Frontend Screens (MVP)

```
Public (no auth required):
/                          PhlowBooks landing
/products                  Platform overview
/phlowbooks                 PhlowBooks marketing + waitlist
/docs                      PhlowBooks API docs
/about                     Product/company about

Auth:
/login                     Email + password login
/signup                    Bookkeeper registration

App (requires JWT):
/app                       Dashboard — client list + usage stats
/app/clients/new           Create new client
/app/clients/:id           Client overview — upload + export
/app/clients/:id/review    Review queue — photo + fields side-by-side
/app/clients/:id/archive   Receipt archive — search, filter, export
/app/settings              Account settings, billing, plan
```

---

## 11. API Route Summary (MVP)

```
# Auth
POST   /v1/auth/register
POST   /v1/auth/login
GET    /v1/auth/me

# Clients
GET    /v1/clients
POST   /v1/clients
GET    /v1/clients/:id
PUT    /v1/clients/:id
DELETE /v1/clients/:id

# Receipts
POST   /v1/clients/:id/receipts/upload
GET    /v1/clients/:id/receipts
GET    /v1/clients/:id/receipts/queue
GET    /v1/receipts/:id
PATCH  /v1/receipts/:id

# Export
GET    /v1/clients/:id/export?month=YYYY-MM&format=qbo|xero|generic

# Billing
POST   /v1/billing/subscribe
POST   /v1/billing/webhook
GET    /v1/billing/status

# Existing (already built)
POST   /v1/extract-receipt       legacy single-file endpoint, keep for API users
GET    /health
GET    /
```

---

## 12. Database Schema — Full MVP

> Reference DDL below uses MySQL syntax from the original PRD; the live schema is now managed by SQLAlchemy models + Alembic against PostgreSQL.

```sql
CREATE TABLE users (
  id                         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name                       VARCHAR(255) NOT NULL,
  email                      VARCHAR(255) NOT NULL UNIQUE,
  password                   VARCHAR(255) NOT NULL,
  plan                       ENUM('free','solo','firm','agency') DEFAULT 'free',
  receipts_used_this_month   INT UNSIGNED DEFAULT 0,
  billing_period_start       DATE,
  paymongo_customer_id       VARCHAR(100),
  paymongo_subscription_id   VARCHAR(100),
  created_at                 DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clients (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id     INT UNSIGNED NOT NULL,
  name        VARCHAR(255) NOT NULL,
  tin         VARCHAR(20),
  industry    VARCHAR(100),
  software    ENUM('quickbooks','xero','juantax','excel','other') DEFAULT 'other',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted_at  DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE receipts (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  client_id     INT UNSIGNED NOT NULL,
  user_id       INT UNSIGNED NOT NULL,
  file_path     VARCHAR(500) NOT NULL,
  original_name VARCHAR(255),
  mime_type     VARCHAR(50),
  file_size_kb  INT,
  file_hash     CHAR(64),              -- SHA-256 for duplicate detection (v1)
  status        ENUM('pending','processing','done','error') DEFAULT 'pending',
  raw_text      TEXT,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  processed_at  DATETIME,
  FOREIGN KEY (client_id) REFERENCES clients(id),
  FOREIGN KEY (user_id)   REFERENCES users(id)
);

CREATE TABLE receipt_data (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  receipt_id      INT UNSIGNED NOT NULL UNIQUE,
  vendor          VARCHAR(255),
  vendor_tin      VARCHAR(25),
  or_number       VARCHAR(100),
  si_number       VARCHAR(100),
  date            DATE,
  currency        CHAR(3) DEFAULT 'PHP',
  doc_type        VARCHAR(50),
  vat_type        VARCHAR(20),
  vatable_amount  DECIMAL(12,2),
  vat_amount      DECIMAL(12,2),
  total           DECIMAL(12,2),
  confidence      DECIMAL(3,2),
  raw_json        JSON,
  edited_by       INT UNSIGNED,        -- user_id who last edited
  edited_at       DATETIME,
  FOREIGN KEY (receipt_id) REFERENCES receipts(id),
  FOREIGN KEY (edited_by)  REFERENCES users(id)
);

CREATE TABLE line_items (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  receipt_id  INT UNSIGNED NOT NULL,
  description VARCHAR(500),
  quantity    DECIMAL(10,3),
  unit_price  DECIMAL(12,2),
  total       DECIMAL(12,2),
  FOREIGN KEY (receipt_id) REFERENCES receipts(id)
);
```

---

## 13. Environment Variables

```bash
# backend/.env
APP_ENV=development                  # development | production
SECRET_KEY=<random 32-byte hex>      # JWT signing key
API_KEY=<random string>              # legacy single-key auth (keep for /v1/extract-receipt)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
TESSERACT_CMD=                       # full path on Windows, blank elsewhere
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=20
MAX_FILES_PER_UPLOAD=50
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/phlowbooks
PAYMONGO_SECRET_KEY=sk_...
PAYMONGO_WEBHOOK_SECRET=whsec_...
CORS_ORIGINS=http://localhost:5173,https://phlowbooks.app
```

---

## 14. Constraints & Decisions

| Decision | Choice | Reason |
|---|---|---|
| Backend language | Python | Richer OCR/AI library ecosystem |
| Frontend framework | Vue 3 + Vite | Already in codebase, developer familiarity |
| Database | PostgreSQL 16 | Strong relational + JSON support, widely hosted, suits structured accounting data |
| File storage v0 | Local disk | No S3 cost/complexity for early validation |
| OCR engine | Tesseract | Free, runs locally, no per-page cost |
| AI model | gpt-4o-mini | Cost-effective (~$0.001–0.005/receipt), handles noisy text |
| Payments | Paymongo | PH-native, supports GCash/Maya, PHP billing |
| Auth | JWT (no refresh tokens for MVP) | Simple to implement, good enough for MVP |
| PDF support | NOT in MVP | Needs `poppler` system dependency; add in v1 |
| Queue | FastAPI BackgroundTasks in MVP, RQ in v1 | Avoid Redis complexity until batch sizes grow |
| Deployment | Mini PC + Nginx + Cloudflare | Low cost, fast to ship; move to cloud when warranted |

---

## 15. Sprint Plan (suggested)

### Sprint 1 (Week 1–2): Foundation
- PostgreSQL setup + SQLAlchemy models for all MVP tables.
- Auth endpoints (`/register`, `/login`, `/me`) + JWT dependency.
- Replace hardcoded API key auth with JWT on all new routes.
- Frontend: `/login` and `/signup` pages wired to API.

### Sprint 2 (Week 3–4): Core workflow
- Clients CRUD (API + frontend `/app` and `/app/clients/new`).
- Batch upload endpoint (up to 50 files, save to disk, create `receipt` rows as `pending`).
- Extend OCR + AI pipeline with BIR fields (`or_number`, `vendor_tin`, `vat_type`, etc.).
- Background extraction task after upload.

### Sprint 3 (Week 5–6): Review queue
- Review queue API endpoints.
- Review queue UI (`/app/clients/:id/review`) — photo + editable fields side-by-side.
- Approve / reject flow. Keyboard shortcuts.
- Receipt archive view (`/app/clients/:id/archive`).

### Sprint 4 (Week 7–8): Export + billing
- CSV export (QBO, Xero, Generic formats).
- Paymongo subscription integration.
- Plan-based receipt limits.
- `/app/settings` billing page.

### Sprint 5 (Week 9–10): Polish + launch prep
- Error handling throughout (upload failures, extraction errors, payment failures).
- Loading states and empty states on all screens.
- Mobile-responsive review queue.
- Deploy to mini PC: Nginx config, Cloudflare setup, SSL.
- Waitlist email → real signup flow.

---

*End of PRD — v0.1*
