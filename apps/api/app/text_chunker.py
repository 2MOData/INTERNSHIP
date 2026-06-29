from dataclasses import dataclass


@dataclass(frozen=True)
class SourcePageText:
    page_number: int
    text: str


@dataclass(frozen=True)
class TextChunk:
    page_number: int
    chunk_index: int
    text: str


class InvalidChunkingConfigError(ValueError):
    pass


def chunk_source_pages(
    pages: list[SourcePageText],
    *,
    max_chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[TextChunk]:
    validate_chunking_config(
        max_chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks: list[TextChunk] = []

    for page in pages:
        page_chunks = split_text_into_chunks(
            page.text,
            max_chunk_size=max_chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for chunk_index, chunk_text in enumerate(page_chunks):
            chunks.append(
                TextChunk(
                    page_number=page.page_number,
                    chunk_index=chunk_index,
                    text=chunk_text,
                )
            )

    return chunks


def split_text_into_chunks(
    text: str,
    *,
    max_chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[str]:
    validate_chunking_config(
        max_chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
    )

    normalized_text = " ".join(text.split())

    if not normalized_text:
        return []

    if len(normalized_text) <= max_chunk_size:
        return [normalized_text]

    chunks: list[str] = []
    start = 0

    while start < len(normalized_text):
        end = min(start + max_chunk_size, len(normalized_text))
        chunk = normalized_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(normalized_text):
            break

        start = end - chunk_overlap

    return chunks


def validate_chunking_config(
    *,
    max_chunk_size: int,
    chunk_overlap: int,
) -> None:
    if max_chunk_size <= 0:
        raise InvalidChunkingConfigError(
            "La taille maximale d’un chunk doit être positive."
        )

    if chunk_overlap < 0:
        raise InvalidChunkingConfigError(
            "Le chevauchement des chunks ne peut pas être négatif."
        )

    if chunk_overlap >= max_chunk_size:
        raise InvalidChunkingConfigError(
            "Le chevauchement doit être inférieur à la taille maximale d’un chunk."
        )