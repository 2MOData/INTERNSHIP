import pytest

from app.text_chunker import (
    InvalidChunkingConfigError,
    SourcePageText,
    chunk_source_pages,
    split_text_into_chunks,
)


def test_split_text_shorter_than_max_size_returns_single_chunk() -> None:
    chunks = split_text_into_chunks(
        "Une petite phrase.",
        max_chunk_size=100,
        chunk_overlap=20,
    )

    assert chunks == ["Une petite phrase."]


def test_split_text_normalizes_whitespace() -> None:
    chunks = split_text_into_chunks(
        "Une   phrase\navec\tplusieurs     espaces.",
        max_chunk_size=100,
        chunk_overlap=20,
    )

    assert chunks == ["Une phrase avec plusieurs espaces."]


def test_split_text_long_text_returns_overlapping_chunks() -> None:
    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = split_text_into_chunks(
        text,
        max_chunk_size=10,
        chunk_overlap=3,
    )

    assert chunks == [
        "abcdefghij",
        "hijklmnopq",
        "opqrstuvwx",
        "vwxyz",
    ]


def test_split_text_empty_text_returns_no_chunks() -> None:
    chunks = split_text_into_chunks(
        "   \n\t   ",
        max_chunk_size=100,
        chunk_overlap=20,
    )

    assert chunks == []


def test_chunk_source_pages_preserves_page_numbers_and_chunk_indexes() -> None:
    chunks = chunk_source_pages(
        [
            SourcePageText(
                page_number=1,
                text="abcdefghijklmnopqrstuvwxyz",
            ),
            SourcePageText(
                page_number=2,
                text="Courte.",
            ),
        ],
        max_chunk_size=10,
        chunk_overlap=3,
    )

    assert chunks[0].page_number == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == "abcdefghij"

    assert chunks[1].page_number == 1
    assert chunks[1].chunk_index == 1
    assert chunks[1].text == "hijklmnopq"

    assert chunks[-1].page_number == 2
    assert chunks[-1].chunk_index == 0
    assert chunks[-1].text == "Courte."


@pytest.mark.parametrize(
    ("max_chunk_size", "chunk_overlap"),
    [
        (0, 0),
        (-1, 0),
        (100, -1),
        (100, 100),
        (100, 120),
    ],
)
def test_invalid_chunking_config_is_rejected(
    max_chunk_size: int,
    chunk_overlap: int,
) -> None:
    with pytest.raises(InvalidChunkingConfigError):
        split_text_into_chunks(
            "Texte de test",
            max_chunk_size=max_chunk_size,
            chunk_overlap=chunk_overlap,
        )