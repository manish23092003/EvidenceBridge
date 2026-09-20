import fitz  # type: ignore
import pytest

from app.config import get_settings
from app.services.pdf_service import (
    InvalidPdfError,
    PdfNoTextError,
    PdfPageLimitError,
    PdfService,
    PdfTooLargeError,
)


def create_pdf(text_pages: list[str]) -> bytes:
    """Helper to create a simple PDF in memory from a list of strings (one per page)."""
    doc = fitz.open()
    for text in text_pages:
        page = doc.new_page()
        if text:
            page.insert_text(fitz.Point(50, 50), text)
    return doc.write()


def test_valid_single_page_pdf():
    pdf_bytes = create_pdf(["Hello World 123"])
    result = PdfService.extract(pdf_bytes, filename="test.pdf")

    assert result.filename == "test.pdf"
    assert result.page_count == 1
    assert result.has_text is True
    assert "Hello World 123" in result.text
    assert result.character_count > 0


def test_multi_page_pdf():
    pdf_bytes = create_pdf(["Page one content", "Page two content"])
    result = PdfService.extract(pdf_bytes)

    assert result.page_count == 2
    assert "--- Page 1 ---" in result.text
    assert "Page one content" in result.text
    assert "--- Page 2 ---" in result.text
    assert "Page two content" in result.text


def test_empty_bytes():
    with pytest.raises(InvalidPdfError, match="cannot be empty"):
        PdfService.extract(b"")


def test_invalid_pdf_bytes():
    with pytest.raises(InvalidPdfError, match="Failed to open PDF"):
        PdfService.extract(b"Not a PDF file")


def test_oversized_input(monkeypatch):
    settings = get_settings()
    # Temporarily set max size to 0 to trigger the error with a normal PDF
    monkeypatch.setattr(settings, "pdf_max_size_mb", 0)
    pdf_bytes = create_pdf(["Small text"])
    with pytest.raises(PdfTooLargeError, match="exceeds the maximum size"):
        PdfService.extract(pdf_bytes)


def test_page_limit_exceeded(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "pdf_max_pages", 2)
    pdf_bytes = create_pdf(["Page 1", "Page 2", "Page 3"])
    with pytest.raises(PdfPageLimitError, match="exceeds the maximum page limit"):
        PdfService.extract(pdf_bytes)


def test_no_extractable_text():
    # PDF with pages but no text
    pdf_bytes = create_pdf(["", ""])
    with pytest.raises(PdfNoTextError, match="no extractable text"):
        PdfService.extract(pdf_bytes)


def test_text_normalization():
    # Testing CRLF, repeated blank lines, trailing whitespace, numbers
    raw_text = "Line 1\r\n\r\n\r\nLine 2 \t \nLine 3 \n$500.00 - Test Unicode\n12345"
    pdf_bytes = create_pdf([raw_text])
    result = PdfService.extract(pdf_bytes)

    # Expected transformations:
    # \r\n -> \n
    # \n\n\n -> \n\n
    # ' \t \n' -> '\n'
    assert "Line 1\n\nLine 2\nLine 3\n$500.00 - Test Unicode\n12345" in result.text


def test_filename_preservation():
    pdf_bytes = create_pdf(["Content"])
    result = PdfService.extract(pdf_bytes, filename="invoice_2026.pdf")
    assert result.filename == "invoice_2026.pdf"
