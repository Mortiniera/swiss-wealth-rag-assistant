"""Integration checks for seed ↔ API ↔ tool coherence on restrictions."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models import Account
from app.database.session import SessionLocal


def test_restricted_accounts_have_active_restriction_rows():
    """
    Every account flagged ``restricted`` must have at least one active
    restriction row (bulk seed + CLI-SCEN overrides).

    Re-run ``scripts/seed_db.py`` after seed changes so this matches production data.
    """
    session = SessionLocal()
    try:
        restricted_accounts = session.scalars(
            select(Account)
            .where(Account.status == "restricted")
            .options(selectinload(Account.restrictions))
        ).all()
        if not restricted_accounts:
            return

        missing: list[str] = []
        for account in restricted_accounts:
            active = [
                row
                for row in account.restrictions
                if (row.status or "").lower() == "active"
            ]
            if not active:
                missing.append(account.account_code)

        assert not missing, (
            "Restricted accounts without active restriction rows: "
            f"{', '.join(missing)}. Re-seed the database."
        )
    finally:
        session.close()
