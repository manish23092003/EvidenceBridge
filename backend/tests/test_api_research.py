from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.research import get_research_service
from app.main import app
from app.schemas.research_execution import (
    ResearchExecutionItem,
    ResearchExecutionResult,
    ResearchExecutionStatus,
)
from app.schemas.research_planning import ResearchPurpose


def mock_successful_service():
    service = MagicMock()
    result = ResearchExecutionResult(
        queries=[
            ResearchExecutionItem(
                query='"ABC"',
                purpose=ResearchPurpose.IDENTITY,
                claim_ids=["c1"],
                status=ResearchExecutionStatus.SUCCESS,
                results=[],
                error=None,
            )
        ]
    )
    service.execute_research.return_value = result
    return service


def test_research_endpoint_success():
    service = mock_successful_service()
    app.dependency_overrides[get_research_service] = lambda: service

    client = TestClient(app)
    payload = {
        "claims": [
            {
                "id": "c1",
                "verification_id": "v1",
                "field": "supplier_name",
                "value": "ABC",
                "source": "DOCUMENT",
                "created_at": "2026-09-01T00:00:00Z",
            }
        ]
    }

    response = client.post("/api/v1/research", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "queries" in data
    assert len(data["queries"]) == 1
    assert data["queries"][0]["status"] == "SUCCESS"
    assert data["queries"][0]["query"] == '"ABC"'


def test_research_endpoint_empty_claims():
    service = MagicMock()
    service.execute_research.return_value = ResearchExecutionResult(queries=[])
    app.dependency_overrides[get_research_service] = lambda: service

    client = TestClient(app)
    response = client.post("/api/v1/research", json={"claims": []})
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["queries"] == []


def test_research_endpoint_failed_query():
    service = MagicMock()
    result = ResearchExecutionResult(
        queries=[
            ResearchExecutionItem(
                query='"ABC"',
                purpose=ResearchPurpose.IDENTITY,
                claim_ids=["c1"],
                status=ResearchExecutionStatus.FAILED,
                results=[],
                error="Safe timeout error",
            )
        ]
    )
    service.execute_research.return_value = result
    app.dependency_overrides[get_research_service] = lambda: service

    client = TestClient(app)
    response = client.post("/api/v1/research", json={"claims": []})
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["queries"][0]["status"] == "FAILED"
    assert response.json()["queries"][0]["error"] == "Safe timeout error"
