"""Load and validate Helvetia internal policy documents from data/policies/."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

import yaml

PolicyStatus = Literal["active", "superseded", "draft"]
Confidentiality = Literal["internal", "confidential", "restricted"]

REQUIRED_FIELDS = (
    "document_id",
    "title",
    "department",
    "type",
    "category",
    "jurisdiction",
    "allowed_roles",
    "effective_date",
    "version",
    "status",
    "confidentiality",
)

ALLOWED_STATUSES = frozenset({"active", "superseded", "draft"})
ALLOWED_CONFIDENTIALITY = frozenset({"internal", "confidential", "restricted"})
KNOWN_ROLES = frozenset(
    {"relationship_manager", "client_service", "compliance_viewer"}
)

DEFAULT_POLICIES_DIR = Path(__file__).resolve().parents[2] / "data" / "policies"


@dataclass(frozen=True)
class PolicyDocument:
    """One versioned policy or procedure on disk."""

    document_id: str
    title: str
    department: str
    type: str
    category: str
    jurisdiction: str
    allowed_roles: tuple[str, ...]
    effective_date: date
    version: str
    status: PolicyStatus
    confidentiality: Confidentiality
    source_path: Path
    body: str
    supersedes: str | None = None


class PolicyRegistryError(ValueError):
    """Invalid policy file or corpus inconsistency."""


def policies_dir() -> Path:
    """Resolve the on-disk policy corpus directory."""
    return DEFAULT_POLICIES_DIR


def _parse_frontmatter(raw: str, path: Path) -> tuple[dict, str]:
    text = raw.lstrip("\ufeff")
    if not text.startswith("---"):
        raise PolicyRegistryError(f"{path.name}: missing YAML frontmatter")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise PolicyRegistryError(f"{path.name}: malformed YAML frontmatter")

    meta = yaml.safe_load(parts[1])
    if not isinstance(meta, dict):
        raise PolicyRegistryError(f"{path.name}: frontmatter must be a mapping")

    body = parts[2].lstrip("\n")
    if not body.strip():
        raise PolicyRegistryError(f"{path.name}: empty policy body")
    return meta, body


def _require_fields(meta: dict, path: Path) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in meta or meta[f] in (None, "")]
    if missing:
        raise PolicyRegistryError(
            f"{path.name}: missing required metadata: {', '.join(missing)}"
        )


def _parse_document(path: Path) -> PolicyDocument:
    meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"), path)
    _require_fields(meta, path)

    status = str(meta["status"]).strip().lower()
    if status not in ALLOWED_STATUSES:
        raise PolicyRegistryError(
            f"{path.name}: status must be one of {sorted(ALLOWED_STATUSES)}"
        )

    confidentiality = str(meta["confidentiality"]).strip().lower()
    if confidentiality not in ALLOWED_CONFIDENTIALITY:
        raise PolicyRegistryError(
            f"{path.name}: confidentiality must be one of "
            f"{sorted(ALLOWED_CONFIDENTIALITY)}"
        )

    roles_raw = meta["allowed_roles"]
    if not isinstance(roles_raw, list) or not roles_raw:
        raise PolicyRegistryError(f"{path.name}: allowed_roles must be a non-empty list")
    roles = tuple(str(r).strip() for r in roles_raw)
    unknown = [r for r in roles if r not in KNOWN_ROLES]
    if unknown:
        raise PolicyRegistryError(
            f"{path.name}: unknown roles {unknown}; expected subset of "
            f"{sorted(KNOWN_ROLES)}"
        )

    effective = meta["effective_date"]
    if isinstance(effective, date):
        effective_date = effective
    else:
        try:
            effective_date = date.fromisoformat(str(effective))
        except ValueError as exc:
            raise PolicyRegistryError(
                f"{path.name}: effective_date must be ISO YYYY-MM-DD"
            ) from exc

    supersedes = meta.get("supersedes")
    if supersedes is not None:
        supersedes = str(supersedes).strip() or None

    return PolicyDocument(
        document_id=str(meta["document_id"]).strip(),
        title=str(meta["title"]).strip(),
        department=str(meta["department"]).strip(),
        type=str(meta["type"]).strip(),
        category=str(meta["category"]).strip(),
        jurisdiction=str(meta["jurisdiction"]).strip(),
        allowed_roles=roles,
        effective_date=effective_date,
        version=str(meta["version"]).strip(),
        status=status,  # type: ignore[arg-type]
        confidentiality=confidentiality,  # type: ignore[arg-type]
        source_path=path,
        body=body,
        supersedes=supersedes,
    )


def load_policies(
    directory: Path | None = None,
    *,
    status: PolicyStatus | None = None,
) -> list[PolicyDocument]:
    """Load policy markdown files; optionally filter by status (default: all)."""
    root = directory or policies_dir()
    if not root.is_dir():
        raise PolicyRegistryError(f"Policies directory not found: {root}")

    docs: list[PolicyDocument] = []
    for path in sorted(root.glob("*.md")):
        if path.name.upper() == "README.MD":
            continue
        docs.append(_parse_document(path))

    if not docs:
        raise PolicyRegistryError(f"No policy documents found in {root}")

    ids = [d.document_id for d in docs]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise PolicyRegistryError(f"Duplicate document_id values: {sorted(duplicates)}")

    id_set = set(ids)
    for doc in docs:
        if doc.supersedes and doc.supersedes not in id_set:
            raise PolicyRegistryError(
                f"{doc.document_id}: supersedes unknown id {doc.supersedes!r}"
            )

    if status is not None:
        docs = [d for d in docs if d.status == status]
    return docs


def active_policies(directory: Path | None = None) -> list[PolicyDocument]:
    """Default retrieval set: active documents only."""
    return load_policies(directory, status="active")
