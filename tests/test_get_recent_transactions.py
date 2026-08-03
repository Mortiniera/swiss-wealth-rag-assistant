"""Unit tests for get_recent_transactions tool."""

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.tools.base import ToolError, ToolResult
from app.tools.get_recent_transactions import (
    GetRecentTransactionsInput,
    get_recent_transactions,
)


def _txn(**overrides):
    base = dict(
        transaction_code="TXN-1",
        account_code="ACC-1",
        txn_type="transfer_out",
        amount=Decimal("1000.00"),
        currency="CHF",
        status="booked",
        booked_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        value_date=None,
        counterparty_name="Counterparty",
        delay_reason_code=None,
        is_unusual=False,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_get_recent_transactions_empty_book():
    session = MagicMock()
    with patch(
        "app.tools.get_recent_transactions.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_recent_transactions.list_client_transactions",
        return_value=[],
    ):
        result = get_recent_transactions(
            session,
            GetRecentTransactionsInput(client_ref="CLI-EMPTY"),
        )

    assert result.ok is True
    assert result.data["transaction_count"] == 0
    assert result.data["transactions"] == []
    assert result.data["pending_or_unusual"] == []


def test_get_recent_transactions_flags_pending():
    session = MagicMock()
    rows = [
        _txn(transaction_code="TXN-P", status="pending", delay_reason_code="kyc_expired"),
        _txn(transaction_code="TXN-B", status="booked"),
    ]
    with patch(
        "app.tools.get_recent_transactions.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_recent_transactions.list_client_transactions",
        return_value=rows,
    ):
        result = get_recent_transactions(
            session,
            GetRecentTransactionsInput(client_ref="CLI-SCEN-01"),
        )

    assert result.ok is True
    assert result.data["transaction_count"] == 2
    assert result.data["pending_or_unusual_count"] == 1
    assert result.data["pending_or_unusual"][0]["transaction_code"] == "TXN-P"
    assert result.data["pending_or_unusual"][0]["delay_reason_code"] == "kyc_expired"


def test_get_recent_transactions_forbidden():
    session = MagicMock()
    with patch(
        "app.tools.get_recent_transactions.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_recent_transactions.get_employee_by_code",
        return_value=object(),
    ), patch(
        "app.tools.get_recent_transactions.actor_can_access_client",
        return_value=False,
    ):
        result = get_recent_transactions(
            session,
            GetRecentTransactionsInput(
                client_ref="CLI-SCEN-01",
                actor_employee_code="EMP-0099",
            ),
        )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "forbidden"


def test_get_recent_transactions_timeout():
    session = MagicMock()
    with patch(
        "app.tools.get_recent_transactions.run_with_timeout",
        side_effect=TimeoutError("Tool timed out after 0.1s"),
    ):
        result = get_recent_transactions(
            session,
            GetRecentTransactionsInput(client_ref="CLI-SCEN-01"),
            timeout_seconds=0.1,
        )

    assert isinstance(result, ToolResult)
    assert result.ok is False
    assert isinstance(result.error, ToolError)
    assert result.error.code == "timeout"
