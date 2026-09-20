import re

import fitz  # type: ignore

from app.config import get_settings
from app.schemas.document import PdfExtractionResult


class PdfServiceError(Exception):
    pass


class InvalidPdfError(PdfServiceError):
    pass


class PdfTooLargeError(PdfServiceError):
    pass


class PdfPageLimitError(PdfServiceError):
    pass


class PdfEncryptedError(PdfServiceError):
    pass


class PdfNoTextError(PdfServiceError):
    pass


class PdfService:
    @staticmethod
    def _normalize_text(text: str) -> str:
        # Normalize CRLF/CR to LF
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse repeated blank lines (3 or more newlines become 2)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove trailing whitespace on each line, but keep the newlines
        text = re.sub(r"[ \t]+\n", "\n", text)
        # Remove overall trailing whitespace
        return text.strip()

    @staticmethod
    def extract(pdf_bytes: bytes, filename: str | None = None) -> PdfExtractionResult:
        if not pdf_bytes:
            raise InvalidPdfError("PDF bytes cannot be empty.")

        settings = get_settings()

        # Check size limit
        max_bytes = settings.pdf_max_size_mb * 1024 * 1024
        if len(pdf_bytes) > max_bytes:
            raise PdfTooLargeError(
                f"PDF exceeds the maximum size of {settings.pdf_max_size_mb} MB."
            )

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise InvalidPdfError(f"Failed to open PDF: {str(e)}") from e

        with doc:
            if doc.is_encrypted:
                raise PdfEncryptedError(
                    "PDF is encrypted or password protected and cannot be processed."
                )

            page_count = doc.page_count
            if page_count > settings.pdf_max_pages:
                raise PdfPageLimitError(
                    f"PDF exceeds the maximum page limit of "
                    f"{settings.pdf_max_pages} pages."
                )

            extracted_text_parts = []

            for i in range(page_count):
                page = doc.load_page(i)
                text = page.get_text("text", sort=True)
                if text.strip():
                    extracted_text_parts.append(f"--- Page {i + 1} ---\n\n{text}")

            if not extracted_text_parts:
                raise PdfNoTextError(
                    "The PDF opened successfully but contains no extractable text. "
                    "OCR is required but not currently supported."
                )

            combined_text = "\n\n".join(extracted_text_parts)
            normalized_text = PdfService._normalize_text(combined_text)

            return PdfExtractionResult(
                filename=filename,
                page_count=page_count,
                text=normalized_text,
                character_count=len(normalized_text),
            )
