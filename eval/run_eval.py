"""Helvetia policy retrieval and /ask evaluation runner."""

from __future__ import annotations

import json
import os
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

# Allow `python eval/run_eval.py` from the repo root.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import httpx

CASES_PATH = Path(__file__).parent / "cases.json"
BASE_URL = os.environ.get("EVAL_BASE_URL", "http://localhost:8000")
SUITES = {
    s.strip()
    for s in os.environ.get("EVAL_SUITES", "retrieval,ask").split(",")
    if s.strip()
}

INSUFFICIENT = (
    "I could not find enough information in the indexed sources to answer this confidently."
)
OUT_OF_SCOPE_PREFIX = "I can only answer questions about Helvetia Private Bank"
META_PREFIX = "I am Helvetia's internal operations assistant"

MIN_RECALL_AT_K = float(os.environ.get("EVAL_MIN_RECALL", "0.85"))
STRICT_CATEGORIES = {"superseded_trap", "draft_trap", "filter"}


def load_cases() -> list[dict[str, Any]]:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("cases.json must be a JSON array")
    return [c for c in cases if c.get("suite") in SUITES]


def _doc_ids_from_hits(hits: list[Any]) -> list[str]:
    return [h.document_id for h in hits]


def score_retrieval_case(case: dict[str, Any], retrieved_ids: list[str]) -> dict[str, Any]:
    expected = list(case.get("expected_document_ids") or [])
    forbidden = set(case.get("forbidden_document_ids") or [])
    expect_empty = bool(case.get("expect_empty"))
    retrieved_set = set(retrieved_ids)

    if expect_empty:
        ok = len(retrieved_ids) == 0 and not (retrieved_set & forbidden)
        recall = 1.0 if ok else 0.0
        mrr = 1.0 if ok else 0.0
    elif not expected:
        ok = not (retrieved_set & forbidden)
        recall = 1.0 if ok else 0.0
        mrr = 1.0 if ok else 0.0
    else:
        hits = [doc for doc in expected if doc in retrieved_set]
        recall = len(hits) / len(expected)
        mrr = 0.0
        for rank, doc_id in enumerate(retrieved_ids, start=1):
            if doc_id in expected:
                mrr = 1.0 / rank
                break
        ok = recall > 0 and not (retrieved_set & forbidden)

    if retrieved_set & forbidden:
        ok = False

    return {
        "ok": ok,
        "recall": recall,
        "mrr": mrr,
        "retrieved": retrieved_ids,
        "active_doc_ok": not bool(retrieved_set & forbidden),
    }


def run_retrieval_suite(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from app.database.session import SessionLocal
    from app.retrieval import RetrievalFilters, retrieve

    results: list[dict[str, Any]] = []
    session = SessionLocal()
    try:
        for case in cases:
            filters_raw = case.get("filters") or {"status": "active"}
            filters = RetrievalFilters(
                status=filters_raw.get("status", "active"),
                role=filters_raw.get("role"),
                jurisdiction=filters_raw.get("jurisdiction"),
                category=filters_raw.get("category"),
            )
            k = int(case.get("k", 5))
            start = time.perf_counter()
            hits = retrieve(
                session,
                case["query"],
                top_k=k,
                filters=filters,
            )
            latency = time.perf_counter() - start
            retrieved_ids = _doc_ids_from_hits(hits)
            scored = score_retrieval_case(case, retrieved_ids)
            results.append(
                {
                    "id": case["id"],
                    "suite": "retrieval",
                    "category": case.get("category", ""),
                    "latency": latency,
                    **scored,
                }
            )
            status = "PASS" if scored["ok"] else "FAIL"
            print(
                f"[{status}] retrieval/{case['id']} "
                f"| {latency:.2f}s | retrieved={retrieved_ids}"
            )
    finally:
        session.close()
    return results


def _classify_ask_response(data: dict[str, Any]) -> str:
    answer = (data.get("answer") or "").strip()
    sources = data.get("sources") or []
    if answer.startswith(META_PREFIX) and not sources:
        return "meta"
    if answer.startswith(OUT_OF_SCOPE_PREFIX) and not sources:
        return "out_of_scope"
    if answer == INSUFFICIENT and not sources:
        return "abstain"
    if sources:
        return "rag"
    return "other"


def run_ask_suite(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    with httpx.Client(base_url=BASE_URL, timeout=120.0) as client:
        for case in cases:
            start = time.perf_counter()
            try:
                response = client.post("/ask", json={"question": case["question"]})
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError as exc:
                print(f"[ERROR] ask/{case['id']}: {exc}")
                results.append(
                    {
                        "id": case["id"],
                        "suite": "ask",
                        "category": case.get("category", ""),
                        "ok": False,
                        "recall": 0.0,
                        "mrr": 0.0,
                        "latency": time.perf_counter() - start,
                        "active_doc_ok": False,
                        "citation_precision": None,
                        "retrieved": [],
                    }
                )
                continue

            latency = time.perf_counter() - start
            kind = _classify_ask_response(data)
            expect = case.get("expect")
            sources = data.get("sources") or []
            retrieved_ids = []
            for source in sources:
                stem = Path(source.get("source_file") or "").stem
                if stem.startswith("POL-"):
                    retrieved_ids.append(stem)

            ok = False
            recall = 0.0
            mrr = 0.0
            citation_precision = None
            active_doc_ok = True
            forbidden = set(case.get("forbidden_document_ids") or [])
            expected = list(case.get("expected_document_ids") or [])

            if expect == "meta":
                ok = kind == "meta"
            elif expect == "out_of_scope":
                ok = kind == "out_of_scope"
            elif expect == "out_of_scope_or_abstain":
                ok = kind in {"out_of_scope", "abstain"}
            elif expect == "safe_refusal":
                # Injection / jailbreak: any non-RAG refusal path is acceptable.
                ok = kind in {"out_of_scope", "abstain", "meta"}
            elif expect == "abstain":
                ok = kind == "abstain"
            elif expect == "rag":
                ok = kind == "rag"
                if expected:
                    retrieved_set = set(retrieved_ids)
                    hits = [doc for doc in expected if doc in retrieved_set]
                    recall = len(hits) / len(expected)
                    for rank, doc_id in enumerate(retrieved_ids, start=1):
                        if doc_id in expected:
                            mrr = 1.0 / rank
                            break
                    ok = ok and recall > 0
                    if retrieved_ids:
                        citation_precision = len([d for d in retrieved_ids if d in expected]) / len(
                            retrieved_ids
                        )
                    if retrieved_set & forbidden:
                        ok = False
                        active_doc_ok = False
                else:
                    recall = 1.0 if ok else 0.0
            else:
                ok = False

            results.append(
                {
                    "id": case["id"],
                    "suite": "ask",
                    "category": case.get("category", ""),
                    "ok": ok,
                    "recall": recall,
                    "mrr": mrr,
                    "latency": latency,
                    "active_doc_ok": active_doc_ok,
                    "citation_precision": citation_precision,
                    "retrieved": retrieved_ids,
                    "kind": kind,
                }
            )
            status = "PASS" if ok else "FAIL"
            print(
                f"[{status}] ask/{case['id']} "
                f"| {latency:.2f}s | kind={kind} | sources={retrieved_ids}"
            )
    return results


def summarise(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        by_category[row["category"]].append(row)

    retrieval_ranked = [r for r in results if r["suite"] == "retrieval"]
    mean_recall = (
        statistics.mean(r["recall"] for r in retrieval_ranked) if retrieval_ranked else None
    )
    mean_mrr = (
        statistics.mean(r["mrr"] for r in retrieval_ranked) if retrieval_ranked else None
    )
    latencies = [r["latency"] for r in results]
    citation_vals = [
        r["citation_precision"]
        for r in results
        if r.get("citation_precision") is not None
    ]

    category_pass = {
        cat: sum(1 for r in rows if r["ok"]) / len(rows)
        for cat, rows in by_category.items()
        if rows
    }

    passed = sum(1 for r in results if r["ok"])
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "mean_recall_at_k": mean_recall,
        "mean_mrr": mean_mrr,
        "active_doc_accuracy": (
            sum(1 for r in results if r.get("active_doc_ok", True)) / len(results)
            if results
            else None
        ),
        "mean_citation_precision": (
            statistics.mean(citation_vals) if citation_vals else None
        ),
        "latency_p50": statistics.median(latencies) if latencies else None,
        "latency_p95": (
            statistics.quantiles(latencies, n=20)[18]
            if len(latencies) >= 20
            else (max(latencies) if latencies else None)
        ),
        "category_pass_rate": category_pass,
    }


def gates_ok(results: list[dict[str, Any]], summary: dict[str, Any]) -> bool:
    if not results:
        return False
    if any(not r["ok"] for r in results if r["category"] in STRICT_CATEGORIES):
        return False
    if any(not r["ok"] for r in results):
        return False
    retrieval = [r for r in results if r["suite"] == "retrieval"]
    if retrieval and summary["mean_recall_at_k"] is not None:
        if summary["mean_recall_at_k"] < MIN_RECALL_AT_K:
            return False
    return True


def main() -> int:
    cases = load_cases()
    if len(cases) < 1:
        print("No cases selected. Check EVAL_SUITES and eval/cases.json.")
        return 1

    print(f"Evaluating {len(cases)} cases (suites={sorted(SUITES)})\n")

    retrieval_cases = [c for c in cases if c["suite"] == "retrieval"]
    ask_cases = [c for c in cases if c["suite"] == "ask"]

    results: list[dict[str, Any]] = []
    if retrieval_cases:
        results.extend(run_retrieval_suite(retrieval_cases))
    if ask_cases:
        print(f"\nAsk suite against {BASE_URL}\n")
        results.extend(run_ask_suite(ask_cases))

    summary = summarise(results)
    print("\n=== Summary ===")
    print(f"passed: {summary['passed']}/{summary['total']}")
    if summary["mean_recall_at_k"] is not None:
        print(f"mean Recall@k: {summary['mean_recall_at_k']:.3f}")
    if summary["mean_mrr"] is not None:
        print(f"mean MRR:      {summary['mean_mrr']:.3f}")
    if summary["active_doc_accuracy"] is not None:
        print(f"active-doc accuracy: {summary['active_doc_accuracy']:.3f}")
    if summary["mean_citation_precision"] is not None:
        print(f"mean citation precision: {summary['mean_citation_precision']:.3f}")
    if summary["latency_p50"] is not None:
        print(
            f"latency p50/p95: {summary['latency_p50']:.2f}s / {summary['latency_p95']:.2f}s"
        )
    print("category pass rates:")
    for cat, rate in sorted(summary["category_pass_rate"].items()):
        print(f"  {cat}: {rate:.0%}")

    if not gates_ok(results, summary):
        print("\nEvaluation gates failed.")
        return 1
    print("\nEvaluation gates passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
