from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    CorpusModel,
    SourceChunkEmbeddingModel,
    SourceChunkModel,
    SourceModel,
)


class CorpusNotFoundForSearchError(LookupError):
    pass


@dataclass(frozen=True)
class VectorSearchMatch:
    chunk_id: UUID
    source_id: UUID
    page_number: int
    chunk_index: int
    text: str
    score: float


class VectorSearchRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def search_corpus_chunks(
        self,
        *,
        corpus_id: UUID,
        query_embedding: list[float],
        limit: int,
    ) -> list[VectorSearchMatch]:
        self._ensure_corpus_exists(corpus_id)

        score_expression = SourceChunkEmbeddingModel.embedding.cosine_distance(
            query_embedding
        )

        statement = (
            select(
                SourceChunkModel.id.label("chunk_id"),
                SourceChunkModel.source_id,
                SourceChunkModel.page_number,
                SourceChunkModel.chunk_index,
                SourceChunkModel.text,
                score_expression.label("score"),
            )
            .join(
                SourceChunkEmbeddingModel,
                SourceChunkEmbeddingModel.chunk_id == SourceChunkModel.id,
            )
            .join(
                SourceModel,
                SourceModel.id == SourceChunkModel.source_id,
            )
            .where(SourceModel.corpus_id == corpus_id)
            .order_by(score_expression.asc())
            .limit(limit)
        )

        rows = self._session.execute(statement).all()

        return [
            VectorSearchMatch(
                chunk_id=row.chunk_id,
                source_id=row.source_id,
                page_number=row.page_number,
                chunk_index=row.chunk_index,
                text=row.text,
                score=float(row.score),
            )
            for row in rows
        ]

    def _ensure_corpus_exists(self, corpus_id: UUID) -> None:
        if self._session.get(CorpusModel, corpus_id) is None:
            raise CorpusNotFoundForSearchError