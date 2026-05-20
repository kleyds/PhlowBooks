import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.schema import DDL


def _database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://phlowbooks:phlowbooks@localhost:5432/phlowbooks",
    )


DATABASE_URL = _database_url()
_IS_SQLITE = DATABASE_URL.startswith("sqlite")
CONNECT_ARGS = {"check_same_thread": False} if _IS_SQLITE else {}

_engine_kwargs = {"connect_args": CONNECT_ARGS}
if not _IS_SQLITE:
    _engine_kwargs.update(
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
    )

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Tables that existed before Alembic was introduced. If a database already has
# these but no `alembic_version`, it predates migrations and we patch any
# remaining gaps then stamp it at head instead of re-running the baseline.
_PRE_ALEMBIC_TABLES = {
    "users",
    "clients",
    "receipts",
    "receipt_data",
    "line_items",
    "bank_transactions",
    "reconciliations",
}

# Backfill targets for pre-Alembic databases. The 2307 columns were added via
# a startup ALTER TABLE patch before Alembic existed; the verification columns
# came from a later lightweight-migration helper. Both run before stamping so
# the stamped revision matches the actual schema.
_RECONCILIATION_COLUMNS: dict[str, str] = {
    "form_2307_status": "VARCHAR(20) NOT NULL DEFAULT 'missing'",
    "form_2307_file_path": "VARCHAR(500)",
    "form_2307_original_name": "VARCHAR(255)",
    "form_2307_mime_type": "VARCHAR(100)",
    "form_2307_uploaded_at": "TIMESTAMP",
    "form_2307_requested_at": "TIMESTAMP",
    "form_2307_received_at": "TIMESTAMP",
    "form_2307_notes": "TEXT",
}

_USER_COLUMNS: dict[str, str] = {
    "is_verified": "BOOLEAN NOT NULL DEFAULT FALSE",
    "verification_token": "VARCHAR(128)",
    "verification_token_expires_at": "TIMESTAMP",
    "verification_sent_at": "TIMESTAMP",
}

_RECEIPT_COLUMNS: dict[str, str] = {
    "upload_link_id": "INTEGER",
}

_ALLOWED_COLUMN_NAME = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


def _safe_identifier(name: str) -> str:
    if not name or any(ch not in _ALLOWED_COLUMN_NAME for ch in name):
        raise ValueError(f"Unsafe identifier: {name!r}")
    return name


def _add_missing_columns(table: str, columns: dict[str, str]) -> None:
    inspector = inspect(engine)
    if table not in inspector.get_table_names():
        return
    table_safe = _safe_identifier(table)
    existing = {column["name"] for column in inspector.get_columns(table)}
    with engine.begin() as connection:
        for column_name, column_definition in columns.items():
            if column_name in existing:
                continue
            column_safe = _safe_identifier(column_name)
            connection.execute(
                DDL(f"ALTER TABLE {table_safe} ADD COLUMN {column_safe} {column_definition}")
            )


def _alembic_config():
    from alembic.config import Config

    backend_root = Path(__file__).resolve().parent.parent
    cfg = Config(str(backend_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return cfg


def init_db() -> None:
    """Bring the database up to the latest Alembic revision.

    For pre-Alembic databases (created by the previous `Base.metadata.create_all`
    + lightweight-migration path), backfill any missing columns and stamp the
    head revision so we don't try to recreate existing tables.
    """
    from alembic import command

    from app import models  # noqa: F401  (ensure models register on Base.metadata)

    cfg = _alembic_config()

    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    has_version_table = "alembic_version" in existing
    looks_pre_alembic = (not has_version_table) and _PRE_ALEMBIC_TABLES.issubset(existing)

    if looks_pre_alembic:
        _add_missing_columns("reconciliations", _RECONCILIATION_COLUMNS)
        _add_missing_columns("users", _USER_COLUMNS)
        _add_missing_columns("receipts", _RECEIPT_COLUMNS)
        Base.metadata.create_all(bind=engine)
        command.stamp(cfg, "head")
    else:
        command.upgrade(cfg, "head")
