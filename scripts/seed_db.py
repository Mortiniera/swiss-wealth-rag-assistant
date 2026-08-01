#!/usr/bin/env python3
"""CLI entry point for truncating and reseeding the Helvetia domain database.

Requires a reachable PostgreSQL instance with migrations applied.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from app.database.seed import reset_database, seed_database
from app.database.session import SessionLocal


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Truncate and reseed synthetic Helvetia banking data."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=settings.seed_rng_seed,
        help="RNG seed for deterministic generation (default: SEED_RNG_SEED).",
    )
    parser.add_argument(
        "--clients",
        type=int,
        default=500,
        help="Number of synthetic clients to generate.",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Skip truncate; intended for an empty database only.",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        if not args.no_reset:
            print("Resetting database tables...")
            reset_database(session)
        print(
            f"Seeding database (rng_seed={args.seed}, clients={args.clients})..."
        )
        stats = seed_database(
            session, rng_seed=args.seed, client_count=args.clients
        )
        print("Seed complete:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return 0
    except Exception as exc:
        session.rollback()
        print(f"Seed failed: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
