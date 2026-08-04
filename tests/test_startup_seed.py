"""Startup auto-seed behaviour for empty structured domain."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.main import maybe_startup_seed


def test_startup_seed_skipped_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_seed", False)
    monkeypatch.setattr("app.main.settings.auto_reseed", False)
    monkeypatch.setattr("app.main.settings.seed_data_version", 0)
    with patch("app.main.run_full_domain_reseed") as mock_reseed, patch(
        "app.main.seed_database"
    ) as mock_seed:
        maybe_startup_seed()
    mock_reseed.assert_not_called()
    mock_seed.assert_not_called()


def test_startup_seed_skipped_when_employees_exist(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_seed", True)
    monkeypatch.setattr("app.main.settings.auto_reseed", False)
    monkeypatch.setattr("app.main.settings.seed_data_version", 0)

    session = MagicMock()
    with (
        patch("app.main.SessionLocal", return_value=session),
        patch("app.main.get_applied_seed_data_version", return_value=0),
        patch("app.main.employee_count", return_value=12),
        patch("app.main.run_full_domain_reseed") as mock_reseed,
        patch("app.main.seed_database") as mock_seed,
    ):
        maybe_startup_seed()

    mock_reseed.assert_not_called()
    mock_seed.assert_not_called()
    session.close.assert_called_once()


def test_startup_seed_runs_when_empty(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_seed", True)
    monkeypatch.setattr("app.main.settings.auto_reseed", False)
    monkeypatch.setattr("app.main.settings.seed_data_version", 0)
    monkeypatch.setattr("app.main.settings.auto_seed_clients", 50)
    monkeypatch.setattr("app.main.settings.seed_rng_seed", 42)

    session = MagicMock()
    with (
        patch("app.main.SessionLocal", return_value=session),
        patch("app.main.get_applied_seed_data_version", return_value=0),
        patch("app.main.employee_count", return_value=0),
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


def test_startup_reseed_when_seed_data_version_bumped(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_seed", True)
    monkeypatch.setattr("app.main.settings.auto_reseed", False)
    monkeypatch.setattr("app.main.settings.seed_data_version", 7)
    monkeypatch.setattr("app.main.settings.auto_seed_clients", 500)
    monkeypatch.setattr("app.main.settings.seed_rng_seed", 42)

    session = MagicMock()
    with (
        patch("app.main.SessionLocal", return_value=session),
        patch("app.main.get_applied_seed_data_version", return_value=0),
        patch(
            "app.main.run_full_domain_reseed",
            return_value={"clients": 515},
        ) as mock_reseed,
        patch("app.main.seed_database") as mock_seed,
    ):
        maybe_startup_seed()

    mock_reseed.assert_called_once_with(
        session,
        rng_seed=42,
        client_count=500,
        seed_data_version=7,
    )
    mock_seed.assert_not_called()


def test_startup_auto_reseed_forces_full_reseed(monkeypatch) -> None:
    monkeypatch.setattr("app.main.settings.auto_seed", False)
    monkeypatch.setattr("app.main.settings.auto_reseed", True)
    monkeypatch.setattr("app.main.settings.seed_data_version", 7)
    monkeypatch.setattr("app.main.settings.auto_seed_clients", 500)
    monkeypatch.setattr("app.main.settings.seed_rng_seed", 42)

    session = MagicMock()
    with (
        patch("app.main.SessionLocal", return_value=session),
        patch("app.main.get_applied_seed_data_version", return_value=7),
        patch(
            "app.main.run_full_domain_reseed",
            return_value={"clients": 515},
        ) as mock_reseed,
    ):
        maybe_startup_seed()

    mock_reseed.assert_called_once()
    assert mock_reseed.call_args.kwargs["seed_data_version"] == 8
