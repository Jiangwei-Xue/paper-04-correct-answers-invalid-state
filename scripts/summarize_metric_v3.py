#!/usr/bin/env python3
"""Create compact, machine-readable V3 replay and transition summaries."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


METRICS = ("final_answer_success_v2", "representation_parseable_v3", "positive_operational_state_present_v3",
           "exclusion_safety_v3", "operational_state_sufficiency_v3", "answer_state_consistency_v3",
           "intrinsic_state_validity_v3", "carried_state_validity_v3", "joint_final_answer_state_success_v3")


def summarize(path: Path) -> dict:
    count = Counter()
    methods = defaultdict(Counter)
    rows = 0
    for row in read_jsonl(path):
        rows += 1
        for key in METRICS:
            count[key] += int(bool(row.get(key)))
        for key in METRICS:
            methods[row.get("method", "")][key] += int(bool(row.get(key)))
    return {"rows": rows, "counts": dict(count), "method_counts": {method: dict(values) for method, values in sorted(methods.items())}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True, action="append", type=Path)
    ap.add_argument("--primary-v2-scores", required=True, type=Path)
    ap.add_argument("--executor-report", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    tiers = {path.stem.replace(".production", ""): summarize(path) for path in args.scores}
    v2_by_id = {row["row_id"]: row for row in read_jsonl(args.primary_v2_scores)}
    transition = Counter()
    for row in read_jsonl(next(path for path in args.scores if path.name == "primary.production.jsonl")):
        transition[(bool(v2_by_id[row["row_id"]].get("carried_state_validity_v2")), bool(row.get("carried_state_validity_v3")))] += 1
    primary = tiers["primary"]
    answer_n = primary["counts"]["final_answer_success_v2"]
    joint_n = primary["counts"]["joint_final_answer_state_success_v3"]
    report = {"schema": "carried_state_validity_v3.replay_summary.v1", "network_calls_performed": 0,
              "tiers": tiers, "primary_conditionals": {
                  "P_V3_given_A_final_v2": {"numerator": joint_n, "denominator": answer_n, "rate": joint_n / answer_n if answer_n else None},
                  "P_invalid_V3_given_A_final_v2": {"numerator": answer_n - joint_n, "denominator": answer_n, "rate": (answer_n - joint_n) / answer_n if answer_n else None}},
              "primary_v2_to_v3_carried_transition": {f"v2_{old}_v3_{new}": n for (old, new), n in sorted(transition.items())},
              "executor_report": str(args.executor_report),
              "method_blocking_primary": True, "pooled_executor_rd_primary": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"primary_rows": primary["rows"], "primary_A_final_v2": answer_n, "primary_joint_v3": joint_n,
                      "tier_count": len(tiers), "network_calls_performed": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
