from uuid import UUID

from .models import SourceChunkModel
from .source_repository import SourceRepository
from .text_chunker import SourcePageText, chunk_source_pages


class SourceHasNoExtractedPagesError(ValueError):
    pass


class SourceChunkService:
    def __init__(
        self,
        repository: SourceRepository,
        *,
        max_chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> None:
        self._repository = repository
        self._max_chunk_size = max_chunk_size
        self._chunk_overlap = chunk_overlap

    def generate_for_source(self, source_id: UUID) -> list[SourceChunkModel]:
        pages = self._repository.list_pages(source_id)

        if not pages:
            raise SourceHasNoExtractedPagesError

        chunks = chunk_source_pages(
            [
                SourcePageText(
                    page_number=page.page_number,
                    text=page.text,
                )
                for page in pages
            ],
            max_chunk_size=self._max_chunk_size,
            chunk_overlap=self._chunk_overlap,
        )

        return self._repository.replace_chunks(
            source_id=source_id,
            chunks=chunks,
        )