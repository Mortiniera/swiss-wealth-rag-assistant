"""Validate Helvetia eval case corpus shape and size."""

from __future__ import annotations

import json
from pathlib import Path

CASES_PATH = Path(__file__).resolve().parents[1] / "eval" / "cases.json"

REQUIRED_COMMON = {"id", "suite", "category"}
RETRIEVAL_REQUIRED = {"query"}
ASK_REQUIRED = {"question", "expect"}
VALID_SUITES = {"retrieval", "ask"}
VALID_ASK_EXPECT = {
    "meta",
    "out_of_scope",
    "out_of_scope_or_abstain",
    "safe_refusal",
    "abstain",
    "rag",
}


def test_eval_cases_meet_v04_minimum() -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    assert len(cases) >= 40

    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids)), "duplicate case ids"

    for case in cases:
        missing = REQUIRED_COMMON - set(case)
        assert not missing, f"{case.get('id')}: missing {missing}"
        assert case["suite"] in VALID_SUITES

        if case["suite"] == "retrieval":
            assert RETRIEVAL_REQUIRED <= set(case), case["id"]
            assert "expected_document_ids" in case or case.get("expect_empty")
        else:
            assert ASK_REQUIRED <= set(case), case["id"]
            assert case["expect"] in VALID_ASK_EXPECT

    assert any(c["category"] == "superseded_trap" for c in cases)
    assert any(c["category"] == "draft_trap" for c in cases)
    assert any(c["category"] == "filter" for c in cases)
    assert any(c["suite"] == "ask" for c in cases)
