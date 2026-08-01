"""Read-only policy catalog routes for the operations workspace."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.policies import PolicyDetailOut, PolicySummaryOut
from app.services.policy_read import (
    build_policy_detail,
    build_policy_summary,
    get_policy_by_document_id,
    list_policies,
)

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=list[PolicySummaryOut])
def get_policies(
    active_only: bool = Query(
        True,
        description="When true, return only policies with status=active.",
    ),
    session: Session = Depends(get_db),
) -> list[PolicySummaryOut]:
    """Return Helvetia policy catalog metadata for the Policies workspace."""
    docs = list_policies(session, active_only=active_only)
    return [build_policy_summary(doc) for doc in docs]


@router.get("/{document_id}", response_model=PolicyDetailOut)
def get_policy(
    document_id: str, session: Session = Depends(get_db)
) -> PolicyDetailOut:
    """Return one policy including markdown body.

    ``document_id`` is the stable policy code (e.g. ``POL-KYC-001``).
    """
    doc = get_policy_by_document_id(session, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return build_policy_detail(doc)
