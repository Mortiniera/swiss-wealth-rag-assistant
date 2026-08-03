"""Unit tests for get_client_profile tool."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.tools.base import ToolError, ToolResult
from app.tools.get_client_profile import GetClientProfileInput, get_client_profile


def _client_out(**overrides):
    base = {
        "client_code": "CLI-SCEN-01",
        "full_name": "Helena Vogt",
        "status": "active",
        "segment": "hnwi",
        "residency_country": "CH",
        "kyc_profile": SimpleNamespace(
            status="expired",
            document_type="passport",
            document_expiry=date(2024, 1, 1),
        ),
        "primary_assignment": SimpleNamespace(
            employee_code="EMP-0001",
            full_name="Elena Meier",
        ),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_get_client_profile_happy_path():
    session = MagicMock()
    fake_client = object()
    with patch(
        "app.tools.get_client_profile.get_client_by_ref",
        return_value=fake_client,
    ), patch(
        "app.tools.get_client_profile.build_client_out",
        return_value=_client_out(),
    ):
        result = get_client_profile(
            session,
            GetClientProfileInput(client_ref="CLI-SCEN-01"),
        )

    assert result.ok is True
    assert result.tool == "get_client_profile"
    assert result.data["client_code"] == "CLI-SCEN-01"
    assert result.data["kyc_status"] == "expired"
    assert result.data["kyc_document_expiry"] == "2024-01-01"
    assert result.data["primary_rm_code"] == "EMP-0001"


def test_get_client_profile_not_found():
    session = MagicMock()
    with patch("app.tools.get_client_profile.get_client_by_ref", return_value=None):
        result = get_client_profile(
            session,
            {"client_ref": "CLI-MISSING"},
        )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "not_found"


def test_get_client_profile_forbidden_for_rm():
    session = MagicMock()
    fake_client = object()
    fake_actor = object()
    with patch(
        "app.tools.get_client_profile.get_client_by_ref",
        return_value=fake_client,
    ), patch(
        "app.tools.get_client_profile.get_employee_by_code",
        return_value=fake_actor,
    ), patch(
        "app.tools.get_client_profile.actor_can_access_client",
        return_value=False,
    ):
        result = get_client_profile(
            session,
            GetClientProfileInput(
                client_ref="CLI-SCEN-01",
                actor_employee_code="EMP-0099",
            ),
        )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "forbidden"


def test_get_client_profile_timeout():
    session = MagicMock()

    with patch(
        "app.tools.get_client_profile.run_with_timeout",
        side_effect=TimeoutError("Tool timed out after 0.1s"),
    ):
        result = get_client_profile(
            session,
            GetClientProfileInput(client_ref="CLI-SCEN-01"),
            timeout_seconds=0.1,
        )

    assert isinstance(result, ToolResult)
    assert result.ok is False
    assert isinstance(result.error, ToolError)
    assert result.error.code == "timeout"
