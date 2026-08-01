"""Tests for Helvetia policy corpus loading and metadata validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.rag.policy_registry import (
    PolicyRegistryError,
    active_policies,
    load_policies,
    policies_dir,
)

EXPECTED_CATEGORIES = {
    "onboarding",
    "kyc_refresh",
    "aml_escalation",
    "account_restrictions",
    "transfer_review",
    "complaint_handling",
    "suitability",
    "client_communication",
    "cross_border",
    "service_requests_sla",
    "data_access",
    "email_approval",
    "escalation_matrix",
}


def test_policies_dir_exists() -> None:
    assert policies_dir().is_dir()


def test_load_policies_covers_required_categories() -> None:
    docs = load_policies()
    categories = {d.category for d in docs}
    missing = EXPECTED_CATEGORIES - categories
    assert not missing, f"missing categories: {sorted(missing)}"
    assert len(docs) >= 14


def test_active_policies_exclude_superseded_and_draft() -> None:
    all_docs = load_policies()
    active = active_policies()

    assert any(d.status == "superseded" for d in all_docs)
    assert any(d.status == "draft" for d in all_docs)
    assert all(d.status == "active" for d in active)
    assert len(active) < len(all_docs)


def test_kyc_active_supersedes_legacy() -> None:
    docs = {d.document_id: d for d in load_policies()}
    legacy = docs["POL-KYC-001"]
    current = docs["POL-KYC-002"]

    assert legacy.status == "superseded"
    assert current.status == "active"
    assert current.supersedes == "POL-KYC-001"
    assert current.effective_date > legacy.effective_date


def test_required_metadata_present_on_each_doc() -> None:
    for doc in load_policies():
        assert doc.document_id
        assert doc.title
        assert doc.department
        assert doc.type
        assert doc.category
        assert doc.jurisdiction
        assert doc.allowed_roles
        assert doc.version
        assert doc.status in {"active", "superseded", "draft"}
        assert doc.confidentiality in {"internal", "confidential", "restricted"}
        assert doc.body.strip()


def test_invalid_frontmatter_raises(tmp_path: Path) -> None:
    bad = tmp_path / "BAD.md"
    bad.write_text("# no frontmatter\n", encoding="utf-8")
    with pytest.raises(PolicyRegistryError, match="frontmatter"):
        load_policies(tmp_path)
