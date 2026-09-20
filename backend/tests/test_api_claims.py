from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.claims import get_claim_extraction_service
from app.main import app
from app.schemas.claim import Claim, ClaimSource

client = TestClient(app)


def test_extract_claims_success():
    mock_service = MagicMock()
    mock_service.extract_claims.return_value = [
        Claim(
            id="c1",
            verification_id="ver-1",
            field="supplier_name",
            value="Test Corp",
            source=ClaimSource.DOCUMENT,
        )
    ]

    app.dependency_overrides[get_claim_extraction_service] = lambda: mock_service

    payload = {"verification_id": "ver-1", "text": "Invoice from Test Corp"}

    response = client.post("/api/v1/claims/extract", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["field"] == "supplier_name"
    assert data[0]["value"] == "Test Corp"

    mock_service.extract_claims.assert_called_once_with(
        text="Invoice from Test Corp", verification_id="ver-1"
    )

    app.dependency_overrides.clear()


def test_extract_claims_validation_failure():
    app.dependency_overrides[get_claim_extraction_service] = lambda: MagicMock()
    # Missing verification_id
    payload = {"text": "Invoice"}
    response = client.post("/api/v1/claims/extract", json=payload)
    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_extract_claims_service_exception():
    mock_service = MagicMock()
    mock_service.extract_claims.side_effect = Exception("LLM failure")

    app.dependency_overrides[get_claim_extraction_service] = lambda: mock_service

    payload = {"verification_id": "ver-1", "text": "Invoice"}

    response = client.post("/api/v1/claims/extract", json=payload)
    assert response.status_code == 500
    assert "internal service error" in response.json()["detail"]

    app.dependency_overrides.clear()
