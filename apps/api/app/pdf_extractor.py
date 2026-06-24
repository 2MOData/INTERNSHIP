from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExtractedPdfPage:
    page_number: int
    text: str


class PdfExtractionError(ValueError):
    pass


class EmptyPdfTextError(PdfExtractionError):
    pass


class InvalidPdfDocumentError(PdfExtractionError):
    pass


def extract_pdf_text(pdf_path: str | Path) -> list[ExtractedPdfPage]:
    path = Path(pdf_path)

    try:
        import fitz
    except ImportError as error:
        raise RuntimeError(
            "PyMuPDF is required to extract PDF text. "
            "Install dependencies from apps/api/requirements.txt."
        ) from error

    try:
        with fitz.open(path) as document:
            pages = [
                ExtractedPdfPage(
                    page_number=page_index + 1,
                    text=document.load_page(page_index).get_text("text").strip(),
                )
                for page_index in range(document.page_count)
            ]
    except (fitz.FileDataError, fitz.FileNotFoundError, RuntimeError) as error:
        raise InvalidPdfDocumentError(
            "Le document PDF est introuvable, corrompu ou invalide."
        ) from error

    if not any(page.text for page in pages):
        raise EmptyPdfTextError(
            "Le document PDF ne contient pas de texte extractible."
        )

    return pages
