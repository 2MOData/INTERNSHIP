from pathlib import Path
from uuid import UUID, uuid4

from .document_storage import LocalDocumentStorage
from .source_repository import SourceRepository
from .models import SourceModel


class InvalidPdfError(ValueError):
    pass


class EmptyFileError(ValueError):
    pass


class FileTooLargeError(ValueError):
    pass


class PdfSourceService:
    def __init__(
        self,
        repository: SourceRepository,
        storage: LocalDocumentStorage,
        max_upload_size_bytes: int,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._max_upload_size_bytes = max_upload_size_bytes

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
            return self._repository.create_pdf(
                corpus_id=corpus_id,
                original_filename=Path(original_filename).name,
                content_type=content_type,
                size_bytes=len(content),
                storage_key=storage_key,
            )
        except Exception:
            self._storage.delete(storage_key)
            raise

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