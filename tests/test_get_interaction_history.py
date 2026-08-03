"""Unit tests for get_interaction_history tool."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.tools.base import ToolError, ToolResult
from app.tools.get_interaction_history import (
    GetInteractionHistoryInput,
    get_interaction_history,
)


def _ix(**overrides):
    base = dict(
        channel="email",
        direction="inbound",
        subject="Still waiting",
        summary="Client asks for an update",
        status="awaiting_reply",
        occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        employee_code=None,
        related_request_code="SRQ-SCEN-06",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_get_interaction_history_caps_and_flags_salient():
    session = MagicMock()
    rows = [
        _ix(subject="Newest inbound", status="awaiting_reply"),
        _ix(
            direction="outbound",
            status="closed",
            subject="Prior reply",
            related_request_code=None,
        ),
        _ix(subject="Older inbound", status="open"),
    ]
    with patch(
        "app.tools.get_interaction_history.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_interaction_history.list_client_interactions",
        return_value=rows,
    ):
        result = get_interaction_history(
            session,
            GetInteractionHistoryInput(client_ref="CLI-SCEN-06", limit=2),
        )

    assert result.ok is True
    assert result.data["interaction_count"] == 3
    assert result.data["returned_count"] == 2
    assert result.data["salient_count"] == 1
    assert result.data["interactions"][0]["subject"] == "Newest inbound"
    assert result.data["salient_interactions"][0]["related_request_code"] == (
        "SRQ-SCEN-06"
    )


def test_get_interaction_history_empty():
    session = MagicMock()
    with patch(
        "app.tools.get_interaction_history.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_interaction_history.list_client_interactions",
        return_value=[],
    ):
        result = get_interaction_history(
            session,
            GetInteractionHistoryInput(client_ref="CLI-EMPTY"),
        )

    assert result.ok is True
    assert result.data["interaction_count"] == 0
    assert result.data["interactions"] == []
    assert result.data["salient_interactions"] == []


def test_get_interaction_history_forbidden():
    session = MagicMock()
    with patch(
        "app.tools.get_interaction_history.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_interaction_history.get_employee_by_code",
        return_value=object(),
    ), patch(
        "app.tools.get_interaction_history.actor_can_access_client",
        return_value=False,
    ):
        result = get_interaction_history(
            session,
            GetInteractionHistoryInput(
                client_ref="CLI-SCEN-06",
                actor_employee_code="EMP-0099",
            ),
        )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "forbidden"


def test_get_interaction_history_timeout():
    session = MagicMock()
    with patch(
        "app.tools.get_interaction_history.run_with_timeout",
        side_effect=TimeoutError("Tool timed out after 0.1s"),
    ):
        result = get_interaction_history(
            session,
            GetInteractionHistoryInput(client_ref="CLI-SCEN-06"),
            timeout_seconds=0.1,
        )

    assert isinstance(result, ToolResult)
    assert result.ok is False
    assert isinstance(result.error, ToolError)
    assert result.error.code == "timeout"
