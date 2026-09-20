from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.evidence import get_evidence_service
from app.main import app
from app.schemas.evidence import Evidence, EvidenceSourceType

client = TestClient(app)


def test_normalize_evidence_success():
    mock_service = MagicMock()
    mock_service.normalize_research_results.return_value = [
        Evidence(
            id="e1",
            verification_id="ver-1",
            field="website",
            value="Found it",
            source_url="http://test.com",
            source_type=EvidenceSourceType.WEB,
            claim_ids=["c1"],
        )
    ]

    app.dependency_overrides[get_evidence_service] = lambda: mock_service

    payload = {
        "execution_result": {"results": []},
        "original_claims": [
            {
                "id": "c1",
                "verification_id": "ver-1",
                "field": "website",
                "value": "http://test.com",
                "source": "DOCUMENT",
            }
        ],
    }

    response = client.post("/api/v1/evidence/normalize", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "e1"
    assert data[0]["source_url"] == "http://test.com"
    assert data[0]["claim_ids"] == ["c1"]

    mock_service.normalize_research_results.assert_called_once()
    app.dependency_overrides.clear()


def test_normalize_evidence_validation_failure():
    payload = {
        "execution_result": {}
        # Missing original_claims
    }
    response = client.post("/api/v1/evidence/normalize", json=payload)
    assert response.status_code == 422


def test_normalize_evidence_service_exception():
    mock_service = MagicMock()
    mock_service.normalize_research_results.side_effect = Exception("Service error")

    app.dependency_overrides[get_evidence_service] = lambda: mock_service

    payload = {"execution_result": {"results": []}, "original_claims": []}

    response = client.post("/api/v1/evidence/normalize", json=payload)
    assert response.status_code == 500
    assert "internal service error" in response.json()["detail"]

    app.dependency_overrides.clear()
