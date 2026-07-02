from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app, get_source_chunk_embedding_service
from app.source_chunk_embedding_service import SourceHasNoChunksError
from tests.test_sources import PDF_CONTENT, create_agent, create_corpus


class FakeSourceChunkEmbeddingService:
    def __init__(self) -> None:
        self.generated_source_ids: list[UUID] = []

    def generate_for_source(self, source_id: UUID) -> list[object]:
        self.generated_source_ids.append(source_id)

        return [
            object(),
            object(),
        ]


class FakeSourceChunkEmbeddingServiceWithoutChunks:
    def generate_for_source(self, source_id: UUID) -> list[object]:
        raise SourceHasNoChunksError


def upload_ready_source(client: TestClient) -> dict[str, object]:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    response = client.post(
        f"/api/corpora/{corpus['id']}/sources/pdf",
        files={
            "file": (
                "policy.pdf",
                PDF_CONTENT,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    return response.json()


def test_generate_source_chunk_embeddings_uses_service(
    client: TestClient,
) -> None:
    fake_service = FakeSourceChunkEmbeddingService()

    def override_source_chunk_embedding_service() -> FakeSourceChunkEmbeddingService:
        return fake_service

    app.dependency_overrides[get_source_chunk_embedding_service] = (
        override_source_chunk_embedding_service
    )

    try:
        source = upload_ready_source(client)

        response = client.post(f"/api/sources/{source['id']}/embeddings")
    finally:
        app.dependency_overrides.pop(
            get_source_chunk_embedding_service,
            None,
        )

    assert response.status_code == 201
    assert response.json() == {"created": 2}
    assert fake_service.generated_source_ids == [UUID(source["id"])]


def test_generate_source_chunk_embeddings_without_chunks_returns_409(
    client: TestClient,
) -> None:
    def override_source_chunk_embedding_service() -> (
        FakeSourceChunkEmbeddingServiceWithoutChunks
    ):
        return FakeSourceChunkEmbeddingServiceWithoutChunks()

    app.dependency_overrides[get_source_chunk_embedding_service] = (
        override_source_chunk_embedding_service
    )

    try:
        source = upload_ready_source(client)

        response = client.post(f"/api/sources/{source['id']}/embeddings")
    finally:
        app.dependency_overrides.pop(
            get_source_chunk_embedding_service,
            None,
        )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "La source ne contient aucun chunk à vectoriser."
    }