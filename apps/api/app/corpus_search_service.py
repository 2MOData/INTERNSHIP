from typing import Protocol
from uuid import UUID

from .vector_search_repository import VectorSearchMatch, VectorSearchRepository


class QueryEmbeddingClient(Protocol):
    def embed_text(self, text: str) -> list[float]:
        pass


class CorpusSearchService:
    def __init__(
        self,
        *,
        vector_search_repository: VectorSearchRepository,
        embedding_client: QueryEmbeddingClient,
    ) -> None:
        self._vector_search_repository = vector_search_repository
        self._embedding_client = embedding_client

    def search(
        self,
        *,
        corpus_id: UUID,
        query: str,
        limit: int,
    ) -> list[VectorSearchMatch]:
        query_embedding = self._embedding_client.embed_text(query)

        return self._vector_search_repository.search_corpus_chunks(
            corpus_id=corpus_id,
            query_embedding=query_embedding,
            limit=limit,
        )