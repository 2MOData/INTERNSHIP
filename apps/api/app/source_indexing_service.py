from uuid import UUID

from .models import SourceModel
from .source_chunk_embedding_service import SourceChunkEmbeddingService
from .source_chunk_service import SourceChunkService
from .source_service import PdfSourceService


class IndexedPdfSourceResult:
    def __init__(
        self,
        *,
        source: SourceModel,
        chunks_created: int,
        embeddings_created: int,
    ) -> None:
        self.source = source
        self.chunks_created = chunks_created
        self.embeddings_created = embeddings_created


class PdfSourceIndexingService:
    def __init__(
        self,
        *,
        pdf_source_service: PdfSourceService,
        source_chunk_service: SourceChunkService,
        source_chunk_embedding_service: SourceChunkEmbeddingService,
    ) -> None:
        self._pdf_source_service = pdf_source_service
        self._source_chunk_service = source_chunk_service
        self._source_chunk_embedding_service = source_chunk_embedding_service

    def upload_and_index(
        self,
        *,
        corpus_id: UUID,
        original_filename: str,
        content_type: str,
        content: bytes,
    ) -> IndexedPdfSourceResult:
        source = self._pdf_source_service.upload(
            corpus_id=corpus_id,
            original_filename=original_filename,
            content_type=content_type,
            content=content,
        )

        chunks = self._source_chunk_service.generate_for_source(source.id)

        embeddings = self._source_chunk_embedding_service.generate_for_source(
            source.id
        )

        return IndexedPdfSourceResult(
            source=source,
            chunks_created=len(chunks),
            embeddings_created=len(embeddings),
        )