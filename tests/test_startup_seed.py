"""Startup auto-seed behaviour for empty structured domain."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.main import maybe_startup_seed


def test_startup_seed_skipped_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_seed", False)
    with patch("app.main.seed_database") as mock_seed:
        maybe_startup_seed()
    mock_seed.assert_not_called()


def test_startup_seed_skipped_when_employees_exist(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_seed", True)

    session = MagicMock()
    session.scalar.return_value = 12

    with (
        patch("app.main.SessionLocal", return_value=session),
        patch("app.main.seed_database") as mock_seed,
    ):
        maybe_startup_seed()

    mock_seed.assert_not_called()
    session.close.assert_called_once()


def test_startup_seed_runs_when_empty(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_seed", True)
    monkeypatch.setattr("app.main.settings.auto_seed_clients", 50)
    monkeypatch.setattr("app.main.settings.seed_rng_seed", 42)

    session = MagicMock()
    session.scalar.return_value = 0

    with (
        patch("app.main.SessionLocal", return_value=session),
        patch(
            "app.main.seed_database",
            return_value={"employees": 12, "clients": 50},
        ) as mock_seed,
    ):
        maybe_startup_seed()

    mock_seed.assert_called_once_with(
        session, rng_seed=42, client_count=50
    )
    session.close.assert_called_once()
