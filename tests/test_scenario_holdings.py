"""Scenario holdings packs should be curated and distinct."""

from app.database.scenario_builders import (
    DEFAULT_HOLDINGS,
    SCENARIO_HOLDINGS,
    holdings_for_scenario,
)


def test_all_fifteen_scenarios_have_holdings_packs():
    assert set(SCENARIO_HOLDINGS) == set(range(1, 16))


def test_scenario_holdings_packs_are_not_clones():
    fingerprints = [
        tuple(holdings_for_scenario(n)) for n in range(1, 16)
    ]
    assert len(set(fingerprints)) == 15


def test_default_holdings_not_used_as_scenario_clone():
    """Curated packs must not all equal the historical default clone."""
    default_fp = tuple(DEFAULT_HOLDINGS)
    matching = [
        n for n in range(1, 16) if tuple(holdings_for_scenario(n)) == default_fp
    ]
    assert matching == []
