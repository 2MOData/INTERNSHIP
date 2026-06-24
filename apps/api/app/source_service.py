from collections.abc import Callable
from pathlib import Path
from uuid import UUID, uuid4

from .document_storage import LocalDocumentStorage
from .models import SourceModel
from .pdf_extractor import (
    EmptyPdfTextError,
    ExtractedPdfPage,
    InvalidPdfDocumentError,
    extract_pdf_text,
)
from .source_repository import SourceRepository


class InvalidPdfError(ValueError):
    pass


class EmptyFileError(ValueError):
    pass


class FileTooLargeError(ValueError):
    pass


PdfExtractor = Callable[[str | Path], list[ExtractedPdfPage]]


class PdfSourceService:
    def __init__(
        self,
        repository: SourceRepository,
        storage: LocalDocumentStorage,
        max_upload_size_bytes: int,
        pdf_extractor: PdfExtractor = extract_pdf_text,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._max_upload_size_bytes = max_upload_size_bytes
        self._pdf_extractor = pdf_extractor

    def upload(
        self,
        *,
        corpus_id: UUID,
        original_filename: str,
        content_type: str,
        content: bytes,
    ) -> SourceModel:
        self._validate(
            original_filename=original_filename,
            content_type=content_type,
            content=content,
        )

        storage_key = f"{corpus_id}/{uuid4()}.pdf"

        self._storage.save(storage_key, content)

        try:
            source = self._repository.create_pdf(
                corpus_id=corpus_id,
                original_filename=Path(original_filename).name,
                content_type=content_type,
                size_bytes=len(content),
                storage_key=storage_key,
            )
        except Exception:
            self._storage.delete(storage_key)
            raise

        try:
            pages = self._pdf_extractor(self._storage.path_for(storage_key))
            return self._repository.save_pages(
                source_id=source.id,
                pages=pages,
            )
        except (EmptyPdfTextError, InvalidPdfDocumentError):
            return self._repository.mark_error(source.id)

    def _validate(
        self,
        *,
        original_filename: str,
        content_type: str,
        content: bytes,
    ) -> None:
        if not content:
            raise EmptyFileError

        if len(content) > self._max_upload_size_bytes:
            raise FileTooLargeError

        if (
            content_type != "application/pdf"
            or not original_filename.lower().endswith(".pdf")
            or not content.startswith(b"%PDF-")
        ):
            raise InvalidPdfError
