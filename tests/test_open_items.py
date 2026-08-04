"""Unit tests for directory open-item signal assembly."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.services.client_read import _kyc_open_items, open_item_signals_by_client_id


def _client(*, kyc_status: str | None = "valid"):
    kyc = None if kyc_status is None else SimpleNamespace(status=kyc_status)
    return SimpleNamespace(id=uuid4(), kyc_profile=kyc)


def test_kyc_open_items_priority_labels():
    assert _kyc_open_items(_client(kyc_status="expired")) == ["KYC expired"]
    assert _kyc_open_items(_client(kyc_status="pending")) == ["KYC pending"]
    assert _kyc_open_items(_client(kyc_status="in_review")) == ["KYC pending"]
    assert _kyc_open_items(_client(kyc_status="valid")) == []
    assert _kyc_open_items(_client(kyc_status=None)) == []


def test_open_item_signals_batch_order():
    client_a = _client(kyc_status="expired")
    client_b = _client(kyc_status="valid")
    client_c = _client(kyc_status="valid")

    class FakeResult:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class FakeScalars:
        def __init__(self, values):
            self._values = values

        def all(self):
            return self._values

    class FakeSession:
        def __init__(self):
            self.scalar_calls = 0
            self.execute_calls = 0

        def scalars(self, _stmt):
            self.scalar_calls += 1
            # 1) restricted accounts  2) pending txns
            if self.scalar_calls == 1:
                return FakeScalars([client_a.id])
            return FakeScalars([client_b.id])

        def execute(self, _stmt):
            self.execute_calls += 1
            # 1) active restriction rows  2) open SRs
            if self.execute_calls == 1:
                return FakeResult([(None, client_a.id)])
            due = datetime.now(timezone.utc) - timedelta(days=1)
            return FakeResult(
                [
                    (client_c.id, due),
                    (client_b.id, datetime.now(timezone.utc) + timedelta(days=5)),
                ]
            )

    signals = open_item_signals_by_client_id(
        FakeSession(), [client_a, client_b, client_c]
    )

    assert signals[client_a.id] == ["KYC expired", "Restriction"]
    assert signals[client_b.id] == ["Pending transfer", "Open SR"]
    assert signals[client_c.id] == ["SLA breach"]
