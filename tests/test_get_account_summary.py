"""Unit tests for get_account_summary tool."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.schemas.clients import AccountSummaryOut, HoldingOut
from app.tools.base import ToolError, ToolResult
from app.tools.get_account_summary import (
    GetAccountSummaryInput,
    get_account_summary,
)


def test_get_account_summary_happy_path():
    session = MagicMock()
    fake_client = object()
    accounts = [
        AccountSummaryOut(
            account_code="ACC-SCEN-10",
            account_type="custody",
            currency="CHF",
            status="active",
            portfolio_name="Portfolio ACC-SCEN-10",
            portfolio_as_of=datetime(2025, 1, 1, tzinfo=timezone.utc),
            base_currency="CHF",
            holdings=[
                HoldingOut(
                    asset_symbol="NESN.SW",
                    asset_name="Nestle SA",
                    quantity=Decimal("200.0"),
                    market_value=Decimal("210000.00"),
                    currency="CHF",
                ),
                HoldingOut(
                    asset_symbol="ROG.SW",
                    asset_name="Roche Holding",
                    quantity=Decimal("30.0"),
                    market_value=Decimal("88000.00"),
                    currency="CHF",
                ),
            ],
        )
    ]
    with patch(
        "app.tools.get_account_summary.get_client_by_ref",
        return_value=fake_client,
    ), patch(
        "app.tools.get_account_summary.list_client_account_summaries",
        return_value=accounts,
    ):
        result = get_account_summary(
            session,
            GetAccountSummaryInput(client_ref="CLI-SCEN-10"),
        )

    assert result.ok is True
    assert result.data["account_count"] == 1
    assert result.data["holding_count"] == 2
    assert result.data["accounts"][0]["account_code"] == "ACC-SCEN-10"
    assert result.data["accounts"][0]["holdings_market_value_total"] == "298000.00"
    assert result.data["accounts"][0]["holdings"][0]["asset_symbol"] == "NESN.SW"


def test_get_account_summary_empty_book():
    session = MagicMock()
    with patch(
        "app.tools.get_account_summary.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_account_summary.list_client_account_summaries",
        return_value=[],
    ):
        result = get_account_summary(
            session,
            GetAccountSummaryInput(client_ref="CLI-EMPTY"),
        )

    assert result.ok is True
    assert result.data["account_count"] == 0
    assert result.data["holding_count"] == 0
    assert result.data["accounts"] == []


def test_get_account_summary_forbidden():
    session = MagicMock()
    with patch(
        "app.tools.get_account_summary.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_account_summary.get_employee_by_code",
        return_value=object(),
    ), patch(
        "app.tools.get_account_summary.actor_can_access_client",
        return_value=False,
    ):
        result = get_account_summary(
            session,
            GetAccountSummaryInput(
                client_ref="CLI-SCEN-10",
                actor_employee_code="EMP-0099",
            ),
        )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "forbidden"


def test_get_account_summary_timeout():
    session = MagicMock()
    with patch(
        "app.tools.get_account_summary.run_with_timeout",
        side_effect=TimeoutError("Tool timed out after 0.1s"),
    ):
        result = get_account_summary(
            session,
            GetAccountSummaryInput(client_ref="CLI-SCEN-10"),
            timeout_seconds=0.1,
        )

    assert isinstance(result, ToolResult)
    assert result.ok is False
    assert isinstance(result.error, ToolError)
    assert result.error.code == "timeout"


def test_get_account_summary_not_found():
    session = MagicMock()
    with patch(
        "app.tools.get_account_summary.get_client_by_ref",
        return_value=None,
    ):
        result = get_account_summary(
            session,
            GetAccountSummaryInput(client_ref="CLI-MISSING"),
        )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "not_found"
