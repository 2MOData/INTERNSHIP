from uuid import uuid4

from app.corpus_search_service import CorpusSearchService
from app.vector_search_repository import VectorSearchMatch


class FakeEmbeddingClient:
    def __init__(self) -> None:
        self.received_texts: list[str] = []

    def embed_text(self, text: str) -> list[float]:
        self.received_texts.append(text)

        return [0.1] * 1536


class FakeVectorSearchRepository:
    def __init__(self) -> None:
        self.received_query_embedding: list[float] | None = None
        self.received_limit: int | None = None
        self.received_corpus_id = None

    def search_corpus_chunks(
        self,
        *,
        corpus_id,
        query_embedding: list[float],
        limit: int,
    ) -> list[VectorSearchMatch]:
        self.received_corpus_id = corpus_id
        self.received_query_embedding = query_embedding
        self.received_limit = limit

        return [
            VectorSearchMatch(
                chunk_id=uuid4(),
                source_id=uuid4(),
                page_number=1,
                chunk_index=0,
                text="Chunk trouvé.",
                score=0.12,
            )
        ]


def test_search_embeds_query_and_searches_chunks() -> None:
    corpus_id = uuid4()
    embedding_client = FakeEmbeddingClient()
    vector_search_repository = FakeVectorSearchRepository()

    service = CorpusSearchService(
        vector_search_repository=vector_search_repository,
        embedding_client=embedding_client,
    )

    results = service.search(
        corpus_id=corpus_id,
        query="Question utilisateur",
        limit=3,
    )

    assert embedding_client.received_texts == ["Question utilisateur"]
    assert vector_search_repository.received_corpus_id == corpus_id
    assert vector_search_repository.received_query_embedding == [0.1] * 1536
    assert vector_search_repository.received_limit == 3

    assert len(results) == 1
    assert results[0].text == "Chunk trouvé."
    assert results[0].score == 0.12