from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import CorpusModel, SourceModel, SourcePageModel
from .pdf_extractor import ExtractedPdfPage


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