from datetime import date, datetime, timezone
from uuid import uuid4

import app.api.policies as policies_api


def test_list_policies_returns_summaries(client, monkeypatch):
    fake_id = uuid4()
    monkeypatch.setattr(
        policies_api,
        "list_policies",
        lambda *_args, **_kwargs: [object()],
    )
    monkeypatch.setattr(
        policies_api,
        "build_policy_summary",
        lambda _: {
            "id": str(fake_id),
            "document_id": "POL-KYC-001",
            "title": "KYC Refresh Requirements",
            "department": "Compliance",
            "doc_type": "policy",
            "category": "kyc",
            "jurisdiction": "CH",
            "allowed_roles": ["relationship_manager", "compliance_viewer"],
            "effective_date": date(2024, 1, 15).isoformat(),
            "version": "1.0",
            "status": "active",
            "confidentiality": "internal",
            "supersedes_document_id": None,
            "source_path": "data/policies/POL-KYC-001.md",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    response = client.get("/policies")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["document_id"] == "POL-KYC-001"
    assert "body" not in body[0]


def test_get_policy_returns_detail_with_body(client, monkeypatch):
    fake_id = uuid4()
    monkeypatch.setattr(
        policies_api,
        "get_policy_by_document_id",
        lambda *_: object(),
    )
    monkeypatch.setattr(
        policies_api,
        "build_policy_detail",
        lambda _: {
            "id": str(fake_id),
            "document_id": "POL-TRF-001",
            "title": "Outbound Transfer Review",
            "department": "Operations",
            "doc_type": "procedure",
            "category": "transfers",
            "jurisdiction": "CH",
            "allowed_roles": ["relationship_manager"],
            "effective_date": date(2024, 3, 1).isoformat(),
            "version": "1.1",
            "status": "active",
            "confidentiality": "internal",
            "supersedes_document_id": None,
            "source_path": "data/policies/POL-TRF-001.md",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "body": "# Outbound Transfer Review\n\nPending review rules.",
        },
    )

    response = client.get("/policies/POL-TRF-001")
    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == "POL-TRF-001"
    assert "Pending review" in body["body"]


def test_get_policy_not_found_returns_404(client, monkeypatch):
    monkeypatch.setattr(policies_api, "get_policy_by_document_id", lambda *_: None)

    response = client.get("/policies/POL-UNKNOWN")
    assert response.status_code == 404
    assert response.json()["detail"] == "Policy not found"
