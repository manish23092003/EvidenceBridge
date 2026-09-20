import fitz  # type: ignore
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)


def create_test_pdf(text_pages: list[str], encrypt: bool = False) -> bytes:
    doc = fitz.open()
    for text in text_pages:
        page = doc.new_page()
        if text:
            page.insert_text(fitz.Point(50, 50), text)
    if encrypt:
        return doc.write(
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw="123",
            user_pw="123",
        )
    return doc.write()


def test_extract_valid_pdf():
    pdf_bytes = create_test_pdf(["Test Supplier Quotation"])
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("quote.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "quote.pdf"
    assert data["page_count"] == 1
    assert data["has_text"] is True
    assert "Test Supplier Quotation" in data["text"]


def test_extract_multi_page_pdf():
    pdf_bytes = create_test_pdf(["Page 1 Content", "Page 2 Content"])
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("multi.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page_count"] == 2
    assert "--- Page 1 ---" in data["text"]
    assert "Page 1 Content" in data["text"]
    assert "--- Page 2 ---" in data["text"]
    assert "Page 2 Content" in data["text"]


def test_extract_missing_file():
    # Sending no file at all
    response = client.post("/api/v1/documents/extract")
    assert response.status_code == 422


def test_extract_invalid_pdf():
    # Sending random text bytes disguised as PDF
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("fake.pdf", b"This is not a real PDF file", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Failed to open PDF" in response.json()["detail"]


def test_extract_oversized_document(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "pdf_max_size_mb", 0)
    pdf_bytes = create_test_pdf(["Text"])

    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("large.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 413
    assert "maximum size" in response.json()["detail"]


def test_extract_page_limit_exceeded(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "pdf_max_pages", 1)
    pdf_bytes = create_test_pdf(["Page 1", "Page 2"])

    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("long.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 413
    assert "maximum page limit" in response.json()["detail"]


def test_extract_encrypted_pdf():
    pdf_bytes = create_test_pdf(["Secret"], encrypt=True)
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("secret.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 422
    assert "encrypted" in response.json()["detail"]


def test_extract_image_only_pdf():
    pdf_bytes = create_test_pdf(["", ""])  # No text
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("image.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 422
    assert "no extractable text" in response.json()["detail"]


def test_content_type_independence():
    pdf_bytes = create_test_pdf(["Real PDF content"])
    # Send with a totally wrong MIME type, relying on safe byte checking
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("test.txt", pdf_bytes, "text/plain")},
    )
    assert response.status_code == 200
    assert "Real PDF content" in response.json()["text"]


def test_obvious_non_pdf():
    # Send something that isn't a PDF at all
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("image.png", b"fake png bytes", "image/png")},
    )
    assert response.status_code == 400
