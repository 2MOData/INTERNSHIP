from typing import Protocol
from uuid import UUID

from .chunk_embedding_repository import ChunkEmbeddingRepository
from .models import SourceChunkEmbeddingModel
from .source_repository import SourceRepository


class EmbeddingClient(Protocol):
    model: str

    def embed_text(self, text: str) -> list[float]:
        pass


class SourceHasNoChunksError(ValueError):
    pass


class SourceChunkEmbeddingService:
    def __init__(
        self,
        *,
        source_repository: SourceRepository,
        embedding_repository: ChunkEmbeddingRepository,
        embedding_client: EmbeddingClient,
    ) -> None:
        self._source_repository = source_repository
        self._embedding_repository = embedding_repository
        self._embedding_client = embedding_client

    def generate_for_source(
        self,
        source_id: UUID,
    ) -> list[SourceChunkEmbeddingModel]:
        chunks = self._source_repository.list_chunks(source_id)

        if not chunks:
            raise SourceHasNoChunksError

        embeddings: list[SourceChunkEmbeddingModel] = []

        for chunk in chunks:
            vector = self._embedding_client.embed_text(chunk.text)

            embedding = self._embedding_repository.upsert_for_chunk(
                chunk_id=chunk.id,
                embedding_model=self._embedding_client.model,
                embedding=vector,
            )

            embeddings.append(embedding)

        return embeddings