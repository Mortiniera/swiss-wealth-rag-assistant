"""Orchestrate curated Helvetia demo scenario overrides."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import AuditEvent, Employee
from app.database.seed_scenario_cases import (
    SCENARIO_COUNT,
    SCENARIO_SEEDERS,
    ScenarioContext,
)


def apply_scenario_overrides(
    session: Session,
    *,
    rms: list[Employee],
    client_service: Employee,
    now: datetime,
) -> dict[str, int]:
    """Insert all curated demo scenarios and return insertion counts.

    Builds ``CLI-SCEN-01`` .. ``CLI-SCEN-15`` via :mod:`seed_scenario_cases`
    after the bulk synthetic population. See ``docs/demo-scenarios/scenarios.md``.
    """
    ctx = ScenarioContext(
        session=session,
        rm=rms[0],
        client_service=client_service,
        now=now,
    )
    for seeder in SCENARIO_SEEDERS:
        seeder(ctx)

    session.add(
        AuditEvent(
            id=uuid.uuid4(),
            event_type="scenario_seed",
            actor_employee_id=ctx.rm.id,
            entity_type="scenarios",
            entity_id=None,
            payload_json={"scenario_count": SCENARIO_COUNT, "phase": "overrides"},
            created_at=now,
        )
    )

    return {
        "scenario_clients": SCENARIO_COUNT,
        "scenario_accounts": SCENARIO_COUNT,
    }
