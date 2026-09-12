#!/usr/bin/env python3
"""Combine independent executor outcomes with frozen V3 labels by method."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def estimate(rows: list[dict]) -> dict:
    groups = {flag: [row for row in rows if row["v3"] == flag] for flag in (True, False)}
    result = {}
    for flag in (True, False):
        group = groups[flag]
        result["v3_" + ("yes" if flag else "no")] = {"n": len(group), "executor_success": sum(row["executor"] for row in group),
            "rate": (sum(row["executor"] for row in group) / len(group) if group else None)}
    if not groups[True] or not groups[False]:
        result["risk_difference"] = None
    else:
        result["risk_difference"] = result["v3_yes"]["rate"] - result["v3_no"]["rate"]
    return result


def bootstrap(rows: list[dict], reps: int, seed: int) -> dict:
    tasks = sorted({row["task_id"] for row in rows})
    by_task = defaultdict(list)
    for row in rows:
        by_task[row["task_id"]].append(row)
    rng = random.Random(seed)
    values = []
    for _ in range(reps):
        sampled = [rng.choice(tasks) for _ in tasks]
        sample = [row for task in sampled for row in by_task[task]]
        estimate_row = estimate(sample)
        if estimate_row["risk_difference"] is not None:
            values.append(estimate_row["risk_difference"])
    values.sort()
    return {"risk_difference": {"mean": sum(values) / len(values) if values else None,
            "ci95": [values[int(len(values) * .025)], values[max(0, int(len(values) * .975) - 1)]] if values else None,
            "replicates": len(values), "requested_replicates": reps, "seed": seed}, "cluster_unit": "task_id"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True, type=Path)
    ap.add_argument("--executor", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--bootstrap-replicates", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260813)
    args = ap.parse_args()
    scores = {row["row_id"]: row for row in read_jsonl(args.scores)}
    executor = read_jsonl(args.executor)
    rows = []
    for ex in executor:
        score = scores.get(ex["row_id"])
        if score is None:
            raise SystemExit(f"missing score row: {ex['row_id']}")
        rows.append({"row_id": ex["row_id"], "task_id": ex["task_id"], "method": ex["method"],
                     "a": bool(score.get("final_answer_success_v2")), "v3": bool(score.get("carried_state_validity_v3")),
                     "executor": int(bool(ex.get("executor_action_success_v3")))})
    method_rows = defaultdict(list)
    all_methods = sorted({row["method"] for row in rows})
    for row in rows:
        if row["a"]:
            method_rows[row["method"]].append(row)
    method_report = {}
    for method in all_methods:
        selected = method_rows.get(method, [])
        stats = estimate(selected)
        stats["rows_answer_correct"] = len(selected)
        stats["bootstrap"] = bootstrap(selected, args.bootstrap_replicates, args.seed) if selected else {"risk_difference": None, "cluster_unit": "task_id"}
        method_report[method] = stats
    quadrants = Counter((row["a"], row["v3"], bool(row["executor"])) for row in rows)
    report = {"schema": "carried_state_validity_v3.executor_criterion_report.v1", "rows": len(rows),
              "task_count": len({row["task_id"] for row in rows}), "network_calls_performed": 0,
              "executor_independence": {"source_surface": "final_state_plus_v3_task_contract_only",
                  "final_answer_read_by_executor": False, "scorer_labels_read_by_executor": False,
                  "production_scorer_imported_by_executor": False, "reference_scorer_imported_by_executor": False},
              "method_blocking": True, "pooled_risk_difference_primary": False,
              "answer_v3_executor_quadrants": {"A_yes_V3_yes_E_yes": quadrants[(True, True, True)],
                  "A_yes_V3_yes_E_no": quadrants[(True, True, False)], "A_yes_V3_no_E_yes": quadrants[(True, False, True)],
                  "A_yes_V3_no_E_no": quadrants[(True, False, False)], "other_rows": sum(v for k, v in quadrants.items() if not k[0])},
              "within_method_answer_correct_estimates": method_report,
              "estimand": "Within method, among final_answer_success_v2 rows, executor success risk difference V3-valid minus V3-invalid.",
              "bootstrap_replicates": args.bootstrap_replicates, "bootstrap_seed": args.seed}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "methods": len(method_report), "method_blocking": True,
                      "pooled_risk_difference_primary": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
