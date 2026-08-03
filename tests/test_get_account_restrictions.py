"""Unit tests for get_account_restrictions tool."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.tools.base import ToolError, ToolResult
from app.tools.get_account_restrictions import (
    GetAccountRestrictionsInput,
    get_account_restrictions,
)


def test_get_account_restrictions_happy_path():
    session = MagicMock()
    fake_client = object()
    accounts = [
        SimpleNamespace(
            account_code="ACC-000602",
            status="restricted",
            restrictions=[
                SimpleNamespace(
                    restriction_type="debit_block",
                    reason_code="manual_review",
                    status="active",
                    effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
                ),
                SimpleNamespace(
                    restriction_type="debit_block",
                    reason_code="old",
                    status="lifted",
                    effective_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
                ),
            ],
        )
    ]
    with patch(
        "app.tools.get_account_restrictions.get_client_by_ref",
        return_value=fake_client,
    ), patch(
        "app.tools.get_account_restrictions.list_client_accounts",
        return_value=accounts,
    ):
        result = get_account_restrictions(
            session,
            GetAccountRestrictionsInput(client_ref="CLI-000238"),
        )

    assert result.ok is True
    assert result.data["restriction_count"] == 1
    assert result.data["restrictions"][0]["account_code"] == "ACC-000602"
    assert result.data["restrictions"][0]["restriction_type"] == "debit_block"


def test_get_account_restrictions_forbidden():
    session = MagicMock()
    with patch(
        "app.tools.get_account_restrictions.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_account_restrictions.get_employee_by_code",
        return_value=object(),
    ), patch(
        "app.tools.get_account_restrictions.actor_can_access_client",
        return_value=False,
    ):
        result = get_account_restrictions(
            session,
            GetAccountRestrictionsInput(
                client_ref="CLI-000238",
                actor_employee_code="EMP-0099",
            ),
        )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "forbidden"


def test_get_account_restrictions_timeout():
    session = MagicMock()
    with patch(
        "app.tools.get_account_restrictions.run_with_timeout",
        side_effect=TimeoutError("Tool timed out after 0.1s"),
    ):
        result = get_account_restrictions(
            session,
            GetAccountRestrictionsInput(client_ref="CLI-000238"),
            timeout_seconds=0.1,
        )

    assert isinstance(result, ToolResult)
    assert result.ok is False
    assert isinstance(result.error, ToolError)
    assert result.error.code == "timeout"
