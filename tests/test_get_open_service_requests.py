"""Unit tests for get_open_service_requests tool."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.tools.base import ToolError, ToolResult
from app.tools.get_open_service_requests import (
    GetOpenServiceRequestsInput,
    get_open_service_requests,
)


def _sr(**overrides):
    base = dict(
        request_code="SRQ-1",
        request_type="kyc_refresh",
        status="open",
        priority="high",
        subject="KYC refresh",
        opened_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        sla_due_at=None,
        assigned_employee_code="EMP-0001",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_get_open_service_requests_filters_resolved():
    session = MagicMock()
    rows = [
        _sr(request_code="SRQ-OPEN", status="open", request_type="aml_review"),
        _sr(request_code="SRQ-DONE", status="resolved", request_type="enquiry"),
    ]
    with patch(
        "app.tools.get_open_service_requests.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_open_service_requests.list_client_service_requests",
        return_value=rows,
    ):
        result = get_open_service_requests(
            session,
            GetOpenServiceRequestsInput(client_ref="CLI-SCEN-01"),
        )

    assert result.ok is True
    assert result.data["request_count"] == 2
    assert result.data["open_count"] == 1
    assert result.data["open_requests"][0]["request_code"] == "SRQ-OPEN"


def test_get_open_service_requests_empty():
    session = MagicMock()
    with patch(
        "app.tools.get_open_service_requests.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_open_service_requests.list_client_service_requests",
        return_value=[],
    ):
        result = get_open_service_requests(
            session,
            GetOpenServiceRequestsInput(client_ref="CLI-EMPTY"),
        )

    assert result.ok is True
    assert result.data["open_count"] == 0
    assert result.data["open_requests"] == []


def test_get_open_service_requests_forbidden():
    session = MagicMock()
    with patch(
        "app.tools.get_open_service_requests.get_client_by_ref",
        return_value=object(),
    ), patch(
        "app.tools.get_open_service_requests.get_employee_by_code",
        return_value=object(),
    ), patch(
        "app.tools.get_open_service_requests.actor_can_access_client",
        return_value=False,
    ):
        result = get_open_service_requests(
            session,
            GetOpenServiceRequestsInput(
                client_ref="CLI-SCEN-01",
                actor_employee_code="EMP-0099",
            ),
        )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "forbidden"


def test_get_open_service_requests_timeout():
    session = MagicMock()
    with patch(
        "app.tools.get_open_service_requests.run_with_timeout",
        side_effect=TimeoutError("Tool timed out after 0.1s"),
    ):
        result = get_open_service_requests(
            session,
            GetOpenServiceRequestsInput(client_ref="CLI-SCEN-01"),
            timeout_seconds=0.1,
        )

    assert isinstance(result, ToolResult)
    assert result.ok is False
    assert isinstance(result.error, ToolError)
    assert result.error.code == "timeout"
