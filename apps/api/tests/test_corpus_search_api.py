from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app, get_corpus_search_service
from app.vector_search_repository import CorpusNotFoundForSearchError, VectorSearchMatch
from tests.test_sources import create_agent, create_corpus


class FakeCorpusSearchService:
    def __init__(self) -> None:
        self.received_corpus_id: UUID | None = None
        self.received_query: str | None = None
        self.received_limit: int | None = None

    def search(
        self,
        *,
        corpus_id: UUID,
        query: str,
        limit: int,
    ) -> list[VectorSearchMatch]:
        self.received_corpus_id = corpus_id
        self.received_query = query
        self.received_limit = limit

        return [
            VectorSearchMatch(
                chunk_id=uuid4(),
                source_id=uuid4(),
                page_number=2,
                chunk_index=1,
                text="Résultat de recherche.",
                score=0.25,
            )
        ]


class FakeMissingCorpusSearchService:
    def search(
        self,
        *,
        corpus_id: UUID,
        query: str,
        limit: int,
    ) -> list[VectorSearchMatch]:
        raise CorpusNotFoundForSearchError


def test_search_corpus_chunks_returns_matches(client: TestClient) -> None:
    agent = create_agent(client)
    corpus = create_corpus(client, str(agent["id"]))

    fake_service = FakeCorpusSearchService()

    def override_corpus_search_service() -> FakeCorpusSearchService:
        return fake_service

    app.dependency_overrides[get_corpus_search_service] = (
        override_corpus_search_service
    )

    try:
        response = client.post(
            f"/api/corpora/{corpus['id']}/search",
            json={
                "query": "Question utilisateur",
                "limit": 3,
            },
        )
    finally:
        app.dependency_overrides.pop(get_corpus_search_service, None)

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 1
    assert results[0]["page_number"] == 2
    assert results[0]["chunk_index"] == 1
    assert results[0]["text"] == "Résultat de recherche."
    assert results[0]["score"] == 0.25

    assert fake_service.received_corpus_id == UUID(corpus["id"])
    assert fake_service.received_query == "Question utilisateur"
    assert fake_service.received_limit == 3


def test_search_missing_corpus_returns_404(client: TestClient) -> None:
    def override_corpus_search_service() -> FakeMissingCorpusSearchService:
        return FakeMissingCorpusSearchService()

    app.dependency_overrides[get_corpus_search_service] = (
        override_corpus_search_service
    )

    try:
        response = client.post(
            "/api/corpora/00000000-0000-0000-0000-000000000000/search",
            json={
                "query": "Question utilisateur",
                "limit": 3,
            },
        )
    finally:
        app.dependency_overrides.pop(get_corpus_search_service, None)

    assert response.status_code == 404
    assert response.json() == {"detail": "Corpus introuvable."}