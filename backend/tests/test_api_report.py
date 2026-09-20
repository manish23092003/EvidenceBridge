from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_report_success():
    payload = {
        "verification_id": "ver-123",
        "supplier": {"name": "ABC Corp", "email": "test@abc.com"},
        "purchase_amount": 5000,
        "currency": "USD",
        "findings": [
            {
                "id": "f1",
                "verification_id": "ver-123",
                "field": "supplier_name",
                "status": "CONSISTENT",
                "explanation": "Matches website.",
                "evidence_ids": ["e1"],
            }
        ],
        "evidence": [
            {
                "id": "e1",
                "verification_id": "ver-123",
                "field": "supplier_name",
                "value": "ABC Corp",
                "source_url": "http://abc.com",
                "source_title": "ABC Corp Home",
                "source_type": "WEB",
                "claim_ids": ["c1"],
            }
        ],
    }

    response = client.post("/api/v1/report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total"] == 1
    assert data["summary"]["consistent"] == 1
    assert len(data["findings"][0]["sources"]) == 1
    assert data["findings"][0]["sources"][0]["source_url"] == "http://abc.com"
    assert data["supplier_name"] == "ABC Corp"


def test_api_report_validation_failure():
    payload = {
        "verification_id": "ver-123",
        # Missing supplier
        "findings": [],
        "evidence": [],
    }

    response = client.post("/api/v1/report", json=payload)
    assert response.status_code == 422
