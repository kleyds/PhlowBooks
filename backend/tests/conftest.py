from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("UPLOAD_DIR", str(BACKEND_ROOT / ".test-uploads"))

from app.auth import get_current_user  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Client, User  # noqa: E402


@pytest.fixture()
def db_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Session, None, None]:
    upload_dir = tmp_path / "uploads"
    monkeypatch.setenv("UPLOAD_DIR", str(upload_dir))

    engine = create_engine(
        f"sqlite:///{tmp_path / 'phlow-test.db'}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def current_user(db_session: Session) -> User:
    user = User(
        name="Test Bookkeeper",
        email="bookkeeper@example.com",
        password="hashed",
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def api_client(db_session: Session, current_user: User) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    def override_get_current_user():
        return current_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        app.dependency_overrides.clear()


@pytest.fixture()
def client_record(db_session: Session, current_user: User) -> Client:
    client = Client(
        user_id=current_user.id,
        name="Acme Retail PH",
        tin="123-456-789-000",
        software="quickbooks",
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client
