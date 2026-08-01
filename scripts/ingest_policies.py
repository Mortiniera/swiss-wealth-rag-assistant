#!/usr/bin/env python3
"""Ingest Helvetia policy Markdown into Postgres (pgvector chunks).

Requires a reachable PostgreSQL instance with migrations applied and
OPENAI_API_KEY set (unless you call the library with a custom embed_fn).

Docker Compose (preferred):
  docker compose exec api python scripts/ingest_policies.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from app.database.session import SessionLocal
from app.rag.policy_ingest import ingest_policies
from app.rag.policy_registry import policies_dir


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest data/policies into knowledge_documents / knowledge_chunks."
    )
    parser.add_argument(
        "--policies-dir",
        type=Path,
        default=None,
        help="Override policies directory (default: data/policies).",
    )
    args = parser.parse_args()

    if not settings.openai_api_key:
        print(
            "OPENAI_API_KEY is required for policy embeddings.",
            file=sys.stderr,
        )
        return 1

    directory = args.policies_dir or policies_dir()
    session = SessionLocal()
    try:
        print(f"Ingesting policies from {directory} ...")
        result = ingest_policies(session, directory=directory)
        print("Ingest complete:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        return 0
    except Exception as exc:
        session.rollback()
        print(f"Policy ingest failed: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
