"""Startup and CLI helpers for domain truncate + seed."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import AuditEvent, Employee
from app.database.seed import reset_database, seed_database

logger = logging.getLogger(__name__)

DOMAIN_RESEED_EVENT = "domain_reseed"


def get_applied_seed_data_version(session: Session) -> int:
    """Return the latest ``seed_data_version`` recorded after a domain reseed."""
    row = session.scalar(
        select(AuditEvent)
        .where(AuditEvent.event_type == DOMAIN_RESEED_EVENT)
        .order_by(AuditEvent.created_at.desc())
        .limit(1)
    )
    if row is None or not row.payload_json:
        return 0
    try:
        return int(row.payload_json.get("seed_data_version") or 0)
    except (TypeError, ValueError):
        return 0


def record_domain_reseed(
    session: Session,
    *,
    seed_data_version: int,
    rng_seed: int,
    stats: dict,
) -> None:
    """Persist a marker so future deploys can skip reseed when the version matches."""
    actor = session.scalar(select(Employee).order_by(Employee.employee_code).limit(1))
    if actor is None:
        logger.warning("Domain reseed marker skipped (no employees after seed)")
        return
    session.add(
        AuditEvent(
            id=uuid.uuid4(),
            event_type=DOMAIN_RESEED_EVENT,
            actor_employee_id=actor.id,
            entity_type="database",
            entity_id=None,
            payload_json={
                "seed_data_version": seed_data_version,
                "rng_seed": rng_seed,
                **stats,
            },
            created_at=datetime.now(timezone.utc),
        )
    )
    session.commit()


def run_full_domain_reseed(
    session: Session,
    *,
    rng_seed: int,
    client_count: int,
    seed_data_version: int,
) -> dict:
    """Truncate domain tables and load synthetic data (same as ``scripts/seed_db.py``)."""
    logger.info(
        "Domain reseed starting (seed_data_version=%d, rng_seed=%d, clients=%d)",
        seed_data_version,
        rng_seed,
        client_count,
    )
    reset_database(session)
    stats = seed_database(session, rng_seed=rng_seed, client_count=client_count)
    record_domain_reseed(
        session,
        seed_data_version=seed_data_version,
        rng_seed=rng_seed,
        stats=stats,
    )
    logger.info("Domain reseed complete: %s", stats)
    return stats


def employee_count(session: Session) -> int:
    return int(session.scalar(select(func.count()).select_from(Employee)) or 0)
