from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_verification_valid_request():
    payload = {
        "supplier_name": "ABC Industrial Solutions",
        "website": "https://example.com",
        "location": "Bengaluru",
        "email": "contact@example.com",
        "phone": "+91-9876543210",
        "product_or_service": "Industrial CNC component",
        "purchase_amount": 180000.0,
        "currency": "INR",
        "document_filename": "abc-quotation.pdf",
    }
    response = client.post("/api/v1/verification-requests", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "verification_id" in data
    assert "supplier_id" in data
    assert data["status"] == "PENDING"
    assert data["purchase_amount"] == 180000.0
    assert data["currency"] == "INR"


def test_create_verification_minimal_valid_request():
    payload = {"supplier_name": "Minimal Supplier", "purchase_amount": 5000.0}
    response = client.post("/api/v1/verification-requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["currency"] == "INR"


def test_create_verification_missing_supplier_name():
    payload = {"purchase_amount": 1000.0}
    response = client.post("/api/v1/verification-requests", json=payload)
    assert response.status_code == 422


def test_create_verification_missing_purchase_amount():
    payload = {"supplier_name": "ABC"}
    response = client.post("/api/v1/verification-requests", json=payload)
    assert response.status_code == 422


def test_create_verification_negative_purchase_amount():
    payload = {"supplier_name": "ABC", "purchase_amount": -100.0}
    response = client.post("/api/v1/verification-requests", json=payload)
    assert response.status_code == 422


def test_create_verification_invalid_email():
    payload = {
        "supplier_name": "ABC",
        "purchase_amount": 100.0,
        "email": "not-an-email",
    }
    response = client.post("/api/v1/verification-requests", json=payload)
    assert response.status_code == 422
