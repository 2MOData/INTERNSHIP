from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

from app.pdf_extractor import (
    EmptyPdfTextError,
    InvalidPdfDocumentError,
    extract_pdf_text,
)


def create_pdf(path: Path, pages: list[str]) -> None:
    document = fitz.open()

    for page_text in pages:
        page = document.new_page()

        if page_text:
            page.insert_text((72, 72), page_text)

    document.save(path)
    document.close()


def test_extract_pdf_text_returns_text_by_page(tmp_path: Path) -> None:
    pdf_path = tmp_path / "policy.pdf"
    create_pdf(
        pdf_path,
        [
            "Conditions bagages cabine",
            "Conditions bagages en soute",
        ],
    )

    pages = extract_pdf_text(pdf_path)

    assert [page.page_number for page in pages] == [1, 2]
    assert pages[0].text == "Conditions bagages cabine"
    assert pages[1].text == "Conditions bagages en soute"


def test_extract_pdf_text_rejects_invalid_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "invalid.pdf"
    pdf_path.write_bytes(b"not a real pdf")

    with pytest.raises(InvalidPdfDocumentError):
        extract_pdf_text(pdf_path)


def test_extract_pdf_text_rejects_pdf_without_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "empty.pdf"
    create_pdf(pdf_path, [""])

    with pytest.raises(EmptyPdfTextError):
        extract_pdf_text(pdf_path)
