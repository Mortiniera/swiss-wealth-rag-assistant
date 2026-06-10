import json
import os
import sys
import time
from pathlib import Path

import httpx

BASE_URL = os.environ.get("EVAL_BASE_URL", "http://localhost:8000")
QUESTIONS_PATH = Path(__file__).parent / "questions.json"
FALLBACK = (
    "I could not find enough information in the indexed sources to answer this confidently."
)


def evaluate_item(client: httpx.Client, item: dict) -> tuple[bool, str, float, dict]:
    start = time.perf_counter()
    response = client.post("/ask", json={"question": item["question"]})
    latency = time.perf_counter() - start
    response.raise_for_status()
    data = response.json()

    if item.get("expect_fallback"):
        ok = data["answer"] == FALLBACK and len(data["sources"]) == 0
        detail = "fallback" if ok else f"answer={data['answer'][:60]}..., sources={len(data['sources'])}"
        return ok, detail, latency, data

    retrieved = {s["source_file"] for s in data["sources"]}
    expected = set(item.get("expected_sources", []))
    hit = bool(retrieved & expected)
    detail = f"retrieved={sorted(retrieved)}, expected={sorted(expected)}"
    return hit, detail, latency, data


def main() -> int:
    items = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    passed = 0

    print(f"Evaluating {len(items)} questions against {BASE_URL}\n")

    with httpx.Client(base_url=BASE_URL, timeout=120.0) as client:
        for i, item in enumerate(items, 1):
            try:
                ok, detail, latency, data = evaluate_item(client, item)
            except httpx.HTTPError as exc:
                print(f"[ERROR] Q{i}: {item['question'][:60]}... | {exc}")
                continue

            status = "PASS" if ok else "FAIL"
            if ok:
                passed += 1

            source_count = len(data.get("sources", []))
            print(
                f"[{status}] Q{i}: {item['question'][:60]}... "
                f"| {latency:.2f}s | sources={source_count} | {detail}"
            )

    print(f"\n{passed}/{len(items)} passed")
    return 0 if passed == len(items) else 1


if __name__ == "__main__":
    sys.exit(main())