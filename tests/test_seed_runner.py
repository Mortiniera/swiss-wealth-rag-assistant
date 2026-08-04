"""Tests for version-gated domain reseed helpers."""

from unittest.mock import MagicMock, patch

from app.database.seed_runner import (
    DOMAIN_RESEED_EVENT,
    get_applied_seed_data_version,
    run_full_domain_reseed,
)


def test_get_applied_seed_data_version_reads_latest_audit():
    session = MagicMock()
    row = MagicMock()
    row.payload_json = {"seed_data_version": 7}
    session.scalar.return_value = row
    assert get_applied_seed_data_version(session) == 7


def test_get_applied_seed_data_version_zero_when_missing():
    session = MagicMock()
    session.scalar.return_value = None
    assert get_applied_seed_data_version(session) == 0


def test_run_full_domain_reseed_records_version_marker():
    session = MagicMock()
    with patch("app.database.seed_runner.reset_database") as mock_reset, patch(
        "app.database.seed_runner.seed_database",
        return_value={"clients": 515, "employees": 12},
    ) as mock_seed, patch(
        "app.database.seed_runner.record_domain_reseed"
    ) as mock_marker:
        stats = run_full_domain_reseed(
            session,
            rng_seed=42,
            client_count=500,
            seed_data_version=7,
        )

    mock_reset.assert_called_once_with(session)
    mock_seed.assert_called_once_with(session, rng_seed=42, client_count=500)
    mock_marker.assert_called_once()
    assert mock_marker.call_args.kwargs["seed_data_version"] == 7
    assert stats["clients"] == 515
