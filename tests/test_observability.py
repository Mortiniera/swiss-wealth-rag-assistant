"""Observability facade: opt-in Langfuse init, no-op without keys."""

from unittest.mock import MagicMock, patch

import pytest

from app.config import settings
from app.observability import get_client, init_observability, is_enabled, reset_observability


@pytest.fixture(autouse=True)
def _reset_observability_state():
    reset_observability()
    yield
    reset_observability()


def test_init_noop_without_keys(monkeypatch):
    monkeypatch.setattr(settings, "langfuse_public_key", "")
    monkeypatch.setattr(settings, "langfuse_secret_key", "")
    monkeypatch.setattr(settings, "langfuse_base_url", "")

    assert init_observability() is False
    assert is_enabled() is False
    assert get_client() is None


def test_init_noop_with_placeholder_keys(monkeypatch):
    monkeypatch.setattr(settings, "langfuse_public_key", "YOUR_LANGFUSE_PUBLIC_KEY")
    monkeypatch.setattr(settings, "langfuse_secret_key", "YOUR_LANGFUSE_SECRET_KEY")

    assert init_observability() is False
    assert is_enabled() is False
    assert get_client() is None


def test_init_enabled_with_mocked_client(monkeypatch):
    mock_client = MagicMock(name="LangfuseClient")
    monkeypatch.setattr(settings, "langfuse_public_key", "pk-lf-test")
    monkeypatch.setattr(settings, "langfuse_secret_key", "sk-lf-test")
    monkeypatch.setattr(settings, "langfuse_base_url", "https://cloud.langfuse.com")

    with patch(
        "langfuse.Langfuse",
        return_value=mock_client,
    ) as mock_ctor:
        assert init_observability() is True

    mock_ctor.assert_called_once_with(
        public_key="pk-lf-test",
        secret_key="sk-lf-test",
        base_url="https://cloud.langfuse.com",
    )
    assert is_enabled() is True
    assert get_client() is mock_client


def test_init_enabled_without_base_url_omits_arg(monkeypatch):
    mock_client = MagicMock(name="LangfuseClient")
    monkeypatch.setattr(settings, "langfuse_public_key", "pk-lf-test")
    monkeypatch.setattr(settings, "langfuse_secret_key", "sk-lf-test")
    monkeypatch.setattr(settings, "langfuse_base_url", "")

    with patch("langfuse.Langfuse", return_value=mock_client) as mock_ctor:
        assert init_observability() is True

    mock_ctor.assert_called_once_with(
        public_key="pk-lf-test",
        secret_key="sk-lf-test",
    )
    assert is_enabled() is True


def test_init_failure_stays_disabled(monkeypatch):
    monkeypatch.setattr(settings, "langfuse_public_key", "pk-lf-test")
    monkeypatch.setattr(settings, "langfuse_secret_key", "sk-lf-test")

    with patch("langfuse.Langfuse", side_effect=RuntimeError("boom")):
        assert init_observability() is False

    assert is_enabled() is False
    assert get_client() is None
