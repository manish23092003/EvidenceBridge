from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.comparison import get_evidence_comparison_service
from app.main import app
from app.schemas.finding import Finding, FindingStatus

client = TestClient(app)


def test_compare_evidence_success():
    mock_service = MagicMock()
    mock_service.generate_findings.return_value = [
        Finding(
            id="f1",
            verification_id="ver-1",
            field="website",
            status=FindingStatus.CONSISTENT,
            explanation="Matches well",
            evidence_ids=["e1"],
        )
    ]

    app.dependency_overrides[get_evidence_comparison_service] = lambda: mock_service

    payload = {"claims": [], "evidence": []}

    response = client.post("/api/v1/evidence/compare", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "CONSISTENT"
    assert data[0]["explanation"] == "Matches well"

    mock_service.generate_findings.assert_called_once()
    app.dependency_overrides.clear()


def test_compare_evidence_validation_failure():
    app.dependency_overrides[get_evidence_comparison_service] = lambda: MagicMock()
    # Missing fields
    payload = {}
    response = client.post("/api/v1/evidence/compare", json=payload)
    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_compare_evidence_service_exception():
    mock_service = MagicMock()
    mock_service.generate_findings.side_effect = Exception("Service error")

    app.dependency_overrides[get_evidence_comparison_service] = lambda: mock_service

    payload = {"claims": [], "evidence": []}

    response = client.post("/api/v1/evidence/compare", json=payload)
    assert response.status_code == 500
    assert "internal service error" in response.json()["detail"]

    app.dependency_overrides.clear()
