from datetime import datetime, timezone
from uuid import uuid4

import app.api.clients as clients_api


def test_list_clients_scenarios_only(client, monkeypatch):
    fake_id = uuid4()
    monkeypatch.setattr(
        clients_api,
        "list_clients",
        lambda *_args, **_kwargs: [object()],
    )
    monkeypatch.setattr(
        clients_api,
        "build_client_out",
        lambda _: {
            "id": str(fake_id),
            "client_code": "CLI-SCEN-01",
            "full_name": "Helena Vogt",
            "email": "scen.01@clients.helvetia.example",
            "residency_country": "CH",
            "status": "active",
            "segment": "hnwi",
            "household_code": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "kyc_profile": {"status": "expired", "document_type": "passport", "document_expiry": "2024-01-01"},
            "suitability_profile": {"status": "complete", "risk_profile": "balanced"},
            "communication_preference": None,
            "primary_assignment": {
                "employee_code": "EMP-0001",
                "full_name": "Ada RM",
                "email": "ada@helvetia.example",
            },
        },
    )

    response = client.get("/clients?scenarios_only=true")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["client_code"] == "CLI-SCEN-01"


def test_get_client_returns_profile(client, monkeypatch):
    fake_client = object()
    fake_id = uuid4()

    monkeypatch.setattr(clients_api, "_require_client", lambda *_: fake_client)
    monkeypatch.setattr(
        clients_api,
        "build_client_out",
        lambda _: {
            "id": str(fake_id),
            "client_code": "CLI-SCEN-01",
            "full_name": "Helena Vogt",
            "email": "scen.01@clients.helvetia.example",
            "residency_country": "CH",
            "status": "active",
            "segment": "hnwi",
            "household_code": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "kyc_profile": None,
            "suitability_profile": None,
            "communication_preference": None,
            "primary_assignment": None,
        },
    )

    response = client.get("/clients/CLI-SCEN-01")
    assert response.status_code == 200
    body = response.json()
    assert body["client_code"] == "CLI-SCEN-01"
    assert body["status"] == "active"


def test_get_client_not_found_returns_404(client, monkeypatch):
    def _raise_not_found(*_args, **_kwargs):
        raise clients_api.HTTPException(status_code=404, detail="Client not found")

    monkeypatch.setattr(clients_api, "_require_client", _raise_not_found)

    response = client.get("/clients/CLI-UNKNOWN")
    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found"


def test_get_client_accounts_returns_list(client, monkeypatch):
    fake_client = object()
    fake_id = str(uuid4())

    monkeypatch.setattr(clients_api, "_require_client", lambda *_: fake_client)
    monkeypatch.setattr(
        clients_api,
        "list_client_accounts",
        lambda *_: [
            {
                "id": fake_id,
                "account_code": "ACC-SCEN-01",
                "account_type": "custody",
                "currency": "CHF",
                "status": "restricted",
                "iban_synthetic": "CH93SCEN000000000001",
                "opened_at": datetime.now(timezone.utc).isoformat(),
                "restrictions": [],
            }
        ],
    )

    response = client.get("/clients/CLI-SCEN-01/accounts")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["account_code"] == "ACC-SCEN-01"


def test_get_client_transactions_returns_list(client, monkeypatch):
    fake_client = object()
    now = datetime.now(timezone.utc).isoformat()

    monkeypatch.setattr(clients_api, "_require_client", lambda *_: fake_client)
    monkeypatch.setattr(
        clients_api,
        "list_client_transactions",
        lambda *_: [
            {
                "id": str(uuid4()),
                "transaction_code": "TXN-SCEN-01",
                "account_code": "ACC-SCEN-01",
                "txn_type": "transfer_out",
                "amount": "85000.00",
                "currency": "CHF",
                "status": "pending",
                "booked_at": None,
                "value_date": None,
                "counterparty_name": "Helvetia Demo Counterparty",
                "description": "Outbound transfer held pending KYC refresh",
                "delay_reason_code": "kyc_expired",
                "is_unusual": False,
                "created_at": now,
            }
        ],
    )

    response = client.get("/clients/CLI-SCEN-01/transactions")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["transaction_code"] == "TXN-SCEN-01"
    assert payload[0]["status"] == "pending"


def test_get_client_interactions_returns_list(client, monkeypatch):
    fake_client = object()

    monkeypatch.setattr(clients_api, "_require_client", lambda *_: fake_client)
    monkeypatch.setattr(
        clients_api,
        "list_client_interactions",
        lambda *_: [
            {
                "id": str(uuid4()),
                "channel": "email",
                "direction": "inbound",
                "subject": "Statement discrepancy question",
                "summary": "Client emailed about a statement line; awaiting bank reply.",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "status": "awaiting_reply",
                "employee_code": None,
                "related_request_code": "SRQ-SCEN-12",
            }
        ],
    )

    response = client.get("/clients/CLI-SCEN-12/interactions")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["status"] == "awaiting_reply"


def test_get_client_service_requests_returns_list(client, monkeypatch):
    fake_client = object()

    monkeypatch.setattr(clients_api, "_require_client", lambda *_: fake_client)
    monkeypatch.setattr(
        clients_api,
        "list_client_service_requests",
        lambda *_: [
            {
                "id": str(uuid4()),
                "request_code": "SRQ-SCEN-15",
                "request_type": "complaint",
                "status": "open",
                "priority": "high",
                "subject": "Escalated fee complaint past SLA",
                "opened_at": datetime.now(timezone.utc).isoformat(),
                "sla_due_at": datetime.now(timezone.utc).isoformat(),
                "resolved_at": None,
                "assigned_employee_code": "EMP-0011",
            }
        ],
    )

    response = client.get("/clients/CLI-SCEN-15/service-requests")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["request_code"] == "SRQ-SCEN-15"
