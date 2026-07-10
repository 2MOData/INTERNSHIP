from fastapi.testclient import TestClient

from app.main import app, get_pdf_source_indexing_service
from app.source_indexing_service import IndexedPdfSourceResult
from tests.test_sources import PDF_CONTENT, create_agent, create_corpus


class FakePdfSourceIndexingService:
    def __init__(self, source: dict[str, object]) -> None:
        self._source = source

    def upload_and_index(
        self,
        *,
        corpus_id,
        original_filename: str,
        content_type: str,
        content: bytes,
    ) -> IndexedPdfSourceResult:
        source = type(
            "FakeSource",
            (),
            self._source,
        )()

        return IndexedPdfSourceResult(
            source=source,
            chunks_created=3,
            embeddings_created=3,
        )


def test_upload_and_index_pdf_source(client: TestClient) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    source_payload = {
        "id": "00000000-0000-0000-0000-000000000001",
        "corpus_id": corpus["id"],
        "source_type": "pdf",
        "original_filename": "policy.pdf",
        "content_type": "application/pdf",
        "size_bytes": len(PDF_CONTENT),
        "status": "ready",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }

    def override_pdf_source_indexing_service() -> FakePdfSourceIndexingService:
        return FakePdfSourceIndexingService(source_payload)

    app.dependency_overrides[get_pdf_source_indexing_service] = (
        override_pdf_source_indexing_service
    )

    try:
        response = client.post(
            f"/api/corpora/{corpus['id']}/sources/pdf/index",
            files={
                "file": (
                    "policy.pdf",
                    PDF_CONTENT,
                    "application/pdf",
                )
            },
        )
    finally:
        app.dependency_overrides.pop(get_pdf_source_indexing_service, None)

    assert response.status_code == 201
    assert response.json() == {
        "source": source_payload,
        "chunks_created": 3,
        "embeddings_created": 3,
    }