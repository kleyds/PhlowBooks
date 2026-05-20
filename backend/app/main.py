from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth_routes import router as auth_router
from app.bank_routes import router as bank_router
from app.client_routes import router as client_router
from app.compliance_routes import router as compliance_router
from app.database import init_db
from app.portal_routes import auth_router as portal_admin_router, public_router as portal_public_router
from app.receipt_routes import router as receipt_router
from app.routes import router


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

app = FastAPI(
    title="PhlowBooks API",
    description="Bookkeeping infrastructure for Filipino accounting firms.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-PDF-Page", "X-PDF-Page-Count"],
)

app.include_router(auth_router, prefix="/v1")
app.include_router(client_router, prefix="/v1")
app.include_router(bank_router, prefix="/v1")
app.include_router(receipt_router, prefix="/v1")
app.include_router(compliance_router, prefix="/v1")
app.include_router(portal_admin_router, prefix="/v1")
app.include_router(portal_public_router, prefix="/v1")
app.include_router(router, prefix="/v1")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"name": "PhlowBooks API", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
