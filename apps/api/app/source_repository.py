from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import CorpusModel, SourceChunkModel, SourceModel, SourcePageModel
from .pdf_extractor import ExtractedPdfPage
from .text_chunker import TextChunk


class SourceNotFoundError(LookupError):
    pass


class CorpusNotFoundForSourceError(LookupError):
    pass


class SourceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_corpus(self, corpus_id: UUID) -> list[SourceModel]:
        self._ensure_corpus_exists(corpus_id)

        statement = (
            select(SourceModel)
            .where(SourceModel.corpus_id == corpus_id)
            .order_by(SourceModel.created_at.desc())
        )

        return list(self._session.scalars(statement))

    def create_pdf(
        self,
        *,
        corpus_id: UUID,
        original_filename: str,
        content_type: str,
        size_bytes: int,
        storage_key: str,
    ) -> SourceModel:
        self._ensure_corpus_exists(corpus_id)

        source = SourceModel(
            corpus_id=corpus_id,
            source_type="pdf",
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            storage_key=storage_key,
            status="uploaded",
        )

        self._session.add(source)
        self._session.commit()
        self._session.refresh(source)

        return source

    def get(self, source_id: UUID) -> SourceModel:
        source = self._session.get(SourceModel, source_id)

        if source is None:
            raise SourceNotFoundError

        return source

    def save_pages(
        self,
        *,
        source_id: UUID,
        pages: list[ExtractedPdfPage],
    ) -> SourceModel:
        source = self.get(source_id)

        for page in pages:
            self._session.add(
                SourcePageModel(
                    source_id=source.id,
                    page_number=page.page_number,
                    text=page.text,
                )
            )

        source.status = "ready"
        self._session.commit()
        self._session.refresh(source)

        return source


    def mark_error(self, source_id: UUID) -> SourceModel:
        source = self.get(source_id)
        source.status = "error"

        self._session.commit()
        self._session.refresh(source)

        return source


    def list_pages(self, source_id: UUID) -> list[SourcePageModel]:
        self.get(source_id)

        statement = (
            select(SourcePageModel)
            .where(SourcePageModel.source_id == source_id)
            .order_by(SourcePageModel.page_number.asc())
        )

        return list(self._session.scalars(statement))

    def _ensure_corpus_exists(self, corpus_id: UUID) -> None:
        if self._session.get(CorpusModel, corpus_id) is None:
            raise CorpusNotFoundForSourceError

    def replace_chunks(
        self,
        *,
        source_id: UUID,
        chunks: list[TextChunk],
    ) -> list[SourceChunkModel]:
        self.get(source_id)

        self._session.execute(
            delete(SourceChunkModel).where(SourceChunkModel.source_id == source_id)
        )

        chunk_models = [
            SourceChunkModel(
                source_id=source_id,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
            )
            for chunk in chunks
        ]

        self._session.add_all(chunk_models)
        self._session.commit()

        for chunk_model in chunk_models:
            self._session.refresh(chunk_model)

        return chunk_models

    def list_chunks(self, source_id: UUID) -> list[SourceChunkModel]:
        self.get(source_id)

        statement = (
            select(SourceChunkModel)
            .where(SourceChunkModel.source_id == source_id)
            .order_by(
                SourceChunkModel.page_number.asc(),
                SourceChunkModel.chunk_index.asc(),
            )
        )

        return list(self._session.scalars(statement))