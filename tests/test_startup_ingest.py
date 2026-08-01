"""Startup auto-ingest behaviour."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.main import maybe_startup_ingest


def test_startup_ingest_skipped_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_ingest", False)
    with patch("app.main.ingest_policies") as mock_ingest:
        maybe_startup_ingest()
    mock_ingest.assert_not_called()


def test_startup_ingest_skipped_without_api_key(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_ingest", True)
    monkeypatch.setattr("app.main.settings.openai_api_key", "")
    with patch("app.main.ingest_policies") as mock_ingest:
        maybe_startup_ingest()
    mock_ingest.assert_not_called()


def test_startup_ingest_skipped_when_documents_exist(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_ingest", True)
    monkeypatch.setattr("app.main.settings.openai_api_key", "sk-test")

    session = MagicMock()
    session.scalar.return_value = 15
    session_cm = MagicMock()
    session_cm.__enter__ = MagicMock(return_value=session)
    session_cm.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.main.SessionLocal", return_value=session),
        patch("app.main.ingest_policies") as mock_ingest,
    ):
        maybe_startup_ingest()

    mock_ingest.assert_not_called()
    session.close.assert_called_once()


def test_startup_ingest_runs_when_empty(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_ingest", True)
    monkeypatch.setattr("app.main.settings.openai_api_key", "sk-test")

    session = MagicMock()
    session.scalar.return_value = 0

    with (
        patch("app.main.SessionLocal", return_value=session),
        patch(
            "app.main.ingest_policies",
            return_value={
                "status": "success",
                "documents_indexed": 15,
                "chunks_created": 15,
                "documents_removed": 0,
            },
        ) as mock_ingest,
    ):
        maybe_startup_ingest()

    mock_ingest.assert_called_once()
    session.close.assert_called_once()
