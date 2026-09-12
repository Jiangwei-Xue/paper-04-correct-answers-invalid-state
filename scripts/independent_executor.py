#!/usr/bin/env python3
"""Independent action executor using only carried state and environment.

No final answer, v1 label, v2 label, or scorer/parser module is imported or
read here. The executor reconstructs the action surface from carried state,
then checks whether that action is sufficient for the frozen environment.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path


OUT = {"OUT", "ALW", "ALLOW", "ALLOWED", "ALLOWED_PATH", "ALLOWED_PATHS", "ACTIVE", "ACTIVE_SET", "ACTIVE_TOKENS", "REQUIRED", "REQUIRED_TOKENS", "VISIBLE_KEEP", "KEEP", "OUTPUT", "OUTPUT_SET", "FINAL", "FINAL_ACTIVE", "FINAL_ACTIVE_SET", "FINAL_TOKENS", "FINAL_ACTIVE_TOKENS", "CARRY_ALL"}
ASSIGN = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*=\s*")


def exact(text, item):
    return bool(item) and re.search(rf"(?<![A-Za-z0-9_]){re.escape(item)}(?![A-Za-z0-9_])", text) is not None


def as_text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)


def parse_state(value):
    if isinstance(value, dict):
        return {str(k).upper(): [as_text(v)] for k, v in value.items()}, True, "json_object"
    text = str(value or "").strip()
    if not text: return {}, False, "missing"
    try:
        obj = json.loads(text)
        if isinstance(obj, dict): return {str(k).upper(): [as_text(v)] for k, v in obj.items()}, True, "json_object"
    except Exception:
        pass
    matches = list(ASSIGN.finditer(text))
    if not matches: return {}, False, "raw_fallback"
    fields = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        fields.setdefault(m.group(1).upper(), []).append(text[m.end():end].strip(" ;\n\t"))
    return fields, "RAW" not in fields, "assignments"


def run_row(row, env):
    fields, parseable, parse_reason = parse_state(row.get("final_state", ""))
    positive = "\n".join(value for key, values in fields.items() if key in OUT for value in values)
    required = list(env.get("required_state_items", []))
    allowed_paths = list(env.get("allowed_answer_paths", []))
    disallowed = set(env.get("disallowed_output_items", []))
    required_missing = [x for x in required if not exact(positive, x)]
    path_missing = [x for x in allowed_paths if not exact(positive, x)]
    disallowed_hits = [x for x in disallowed if exact(positive, x)]
    action_success = parseable and bool(positive.strip()) and not required_missing and not path_missing and not disallowed_hits
    reasons = []
    if not parseable: reasons.append("EXECUTOR_STATE_NOT_PARSEABLE")
    if not positive.strip(): reasons.append("EXECUTOR_NO_ACTION_SURFACE")
    if required_missing: reasons.append("EXECUTOR_REQUIRED_MISSING")
    if path_missing: reasons.append("EXECUTOR_ALLOWED_PATH_MISSING")
    if disallowed_hits: reasons.append("EXECUTOR_DISALLOWED_ACTION")
    return {
        "row_id": row.get("row_id", ""), "task_id": row.get("task_id", ""),
        "family": env.get("family", ""), "model": row.get("model", ""), "method": row.get("method", ""),
        "budget": row.get("budget", ""), "run_id": row.get("run_id", ""),
        "executor_action_success": bool(action_success), "executor_parseable": bool(parseable),
        "executor_reason_codes": sorted(set(reasons)), "executor_required_missing": required_missing,
        "executor_path_missing": path_missing, "executor_disallowed_hits": sorted(disallowed_hits),
    }


def load_jsonl(path):
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def bootstrap(rows, score_by_id, seed=20260813, reps=10000):
    task_ids = sorted({row["task_id"] for row in rows})
    by_task = defaultdict(list)
    for row in rows: by_task[row["task_id"]].append(row)
    rng = random.Random(seed)
    exec_rates, answer_exec_gaps = [], []
    for _ in range(reps):
        sampled = [rng.choice(task_ids) for _ in task_ids]
        sample = [row for task in sampled for row in by_task[task]]
        exec_rates.append(sum(row["executor_action_success"] for row in sample) / len(sample))
        answer_exec_gaps.append(sum(bool(score_by_id[row["row_id"]].get("answer_success_v2")) - int(row["executor_action_success"]) for row in sample) / len(sample))
    def ci(values):
        values = sorted(values)
        return {"mean": sum(values) / len(values), "ci95": [values[int(0.025 * len(values))], values[int(0.975 * len(values)) - 1]], "replicates": len(values), "seed": seed}
    return {"executor_rate": ci(exec_rates), "answer_minus_executor_rate": ci(answer_exec_gaps), "cluster_unit": "task_id", "task_count": len(task_ids)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, type=Path)
    ap.add_argument("--sidecar", required=True, type=Path)
    ap.add_argument("--scores", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    env = {row["source_task_id"]: row for row in load_jsonl(args.sidecar)}
    inputs = load_jsonl(args.inputs)
    scores = {row["row_id"]: row for row in load_jsonl(args.scores)}
    executor_rows = []
    for row in inputs:
        if row["task_id"] not in env: raise SystemExit(f"missing environment task: {row['task_id']}")
        executor_rows.append(run_row(row, env[row["task_id"]]))
    quadrants = Counter()
    for row in executor_rows:
        quadrants[(bool(scores[row["row_id"]].get("answer_success_v2")), bool(row["executor_action_success"]))] += 1
    family_table = defaultdict(lambda: Counter())
    for row in executor_rows:
        family_table[row["family"]]["rows"] += 1
        family_table[row["family"]]["executor_success"] += int(row["executor_action_success"])
        family_table[row["family"]]["answer_success_v2"] += int(bool(scores[row["row_id"]].get("answer_success_v2")))
    report = {
        "schema": "metric_v2_independent_executor_report.v1", "network_calls_performed": 0,
        "executor_independence": {"source_surface": "final_state_plus_derived_environment_only", "final_answer_read": False, "scorer_labels_read_by_executor": False, "production_scorer_imported": False, "reference_scorer_imported": False},
        "rows": len(executor_rows), "task_count": len({x["task_id"] for x in executor_rows}),
        "family_counts": {k: dict(v) for k, v in sorted(family_table.items())},
        "four_quadrant_answer_success_v2_by_executor": {"answer_yes_executor_yes": quadrants[(True, True)], "answer_yes_executor_no": quadrants[(True, False)], "answer_no_executor_yes": quadrants[(False, True)], "answer_no_executor_no": quadrants[(False, False)]},
        "task_cluster_bootstrap": bootstrap(executor_rows, scores),
        "executor_rows": executor_rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": report["rows"], "task_count": report["task_count"], "four_quadrant": report["four_quadrant_answer_success_v2_by_executor"], "bootstrap_replicates": report["task_cluster_bootstrap"]["executor_rate"]["replicates"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
