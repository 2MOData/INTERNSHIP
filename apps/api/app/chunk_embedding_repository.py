from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import SourceChunkEmbeddingModel, SourceChunkModel


class SourceChunkNotFoundError(LookupError):
    pass


class ChunkEmbeddingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_for_chunk(
        self,
        *,
        chunk_id: UUID,
        embedding_model: str,
        embedding: list[float],
    ) -> SourceChunkEmbeddingModel:
        chunk = self._session.get(SourceChunkModel, chunk_id)

        if chunk is None:
            raise SourceChunkNotFoundError

        statement = select(SourceChunkEmbeddingModel).where(
            SourceChunkEmbeddingModel.chunk_id == chunk_id
        )
        existing_embedding = self._session.scalar(statement)

        if existing_embedding is None:
            existing_embedding = SourceChunkEmbeddingModel(
                chunk_id=chunk_id,
                embedding_model=embedding_model,
                embedding_dimensions=len(embedding),
                embedding=embedding,
            )
            self._session.add(existing_embedding)
        else:
            existing_embedding.embedding_model = embedding_model
            existing_embedding.embedding_dimensions = len(embedding)
            existing_embedding.embedding = embedding

        self._session.commit()
        self._session.refresh(existing_embedding)

        return existing_embedding

    def get_for_chunk(self, chunk_id: UUID) -> SourceChunkEmbeddingModel | None:
        chunk = self._session.get(SourceChunkModel, chunk_id)

        if chunk is None:
            raise SourceChunkNotFoundError

        statement = select(SourceChunkEmbeddingModel).where(
            SourceChunkEmbeddingModel.chunk_id == chunk_id
        )

        return self._session.scalar(statement)