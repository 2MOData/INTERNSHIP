from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_database_session
from app.document_storage import LocalDocumentStorage
from app.main import app, get_pdf_source_service
from app.source_repository import SourceRepository
from app.source_service import PdfSourceService
from app.pdf_extractor import ExtractedPdfPage

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def prepare_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def document_storage_path(tmp_path: Path) -> Path:
    return tmp_path / "documents"

@pytest.fixture
def test_session() -> Generator[Session, None, None]:
    with TestSessionLocal() as session:
        yield session

@pytest.fixture
def client(
    document_storage_path: Path,
) -> Generator[TestClient, None, None]:
    def override_database_session() -> Generator[Session, None, None]:
        with TestSessionLocal() as session:
            yield session

    def override_pdf_source_service() -> Generator[
        PdfSourceService,
        None,
        None,
    ]:
        with TestSessionLocal() as session:
            yield PdfSourceService(
                repository=SourceRepository(session),
                storage=LocalDocumentStorage(str(document_storage_path)),
                max_upload_size_bytes=1024 * 1024,
                pdf_extractor=lambda path: [
                    ExtractedPdfPage(
                        page_number=1,
                        text="Texte extrait du PDF de test.",
                    )
                ],
            )
    app.dependency_overrides[get_database_session] = (
        override_database_session
    )
    app.dependency_overrides[get_pdf_source_service] = (
        override_pdf_source_service
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()