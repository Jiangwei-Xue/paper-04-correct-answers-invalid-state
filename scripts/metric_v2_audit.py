#!/usr/bin/env python3
"""Aggregate offline metric-v2 scores and verify independent agreement."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path


FIELDS = [
    "state_parseable_v2", "output_bearing_present_v2", "exclusion_safety_v2",
    "required_state_completeness_v2", "answer_state_consistency_v2",
    "intrinsic_state_validity_v2", "carried_state_validity_v2",
    "joint_answer_state_success_v2", "answer_success_v2",
]
COMPARE = FIELDS + ["state_reason_codes_v2"]


def load(path: Path):
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def summary(path: Path, family_by_task: dict[str, str]) -> dict:
    rows = load(path)
    result = {"rows": len(rows), "file_sha256": sha256(path), "counts": {}, "rates": {}}
    for field in FIELDS:
        count = sum(bool(row.get(field)) for row in rows)
        result["counts"][field] = count
        result["rates"][field] = count / len(rows) if rows else None
    result["reason_code_counts"] = dict(collections.Counter(code for row in rows for code in row.get("state_reason_codes_v2", [])))
    result["family_counts"] = dict(collections.Counter(family_by_task.get(row.get("task_id", ""), "unknown") for row in rows))
    result["model_counts"] = dict(collections.Counter(row.get("model", "") for row in rows))
    return result


def differential(prod: Path, ref: Path) -> dict:
    a, b = load(prod), load(ref)
    by_a = {row["row_id"]: row for row in a}
    by_b = {row["row_id"]: row for row in b}
    missing = sorted(set(by_a) ^ set(by_b))
    mismatches = []
    for row_id in sorted(set(by_a) & set(by_b)):
        x, y = by_a[row_id], by_b[row_id]
        delta = {field: {"production": x.get(field), "reference": y.get(field)} for field in COMPARE if x.get(field) != y.get(field)}
        if delta: mismatches.append({"row_id": row_id, "fields": delta})
    return {"production": str(prod), "reference": str(ref), "production_rows": len(a), "reference_rows": len(b), "missing_or_extra_row_ids": missing, "mismatch_count": len(mismatches), "mismatches_sample": mismatches[:10], "binary_component_agreement": len(mismatches) == 0 and not missing, "reason_code_set_agreement": len(mismatches) == 0 and not missing}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=Path("reports/metric_v2"))
    args = ap.parse_args()
    score_dir = Path("results/metric_v2/scores_v2")
    sidecars = {row["source_task_id"]: row.get("family", "") for row in (json.loads(line) for line in Path("results/metric_v2/oracles_v2/main_matrix_v1.sidecar.jsonl").open(encoding="utf-8") if line.strip())}
    tiers = ["primary", "primary_budget300", "qwen", "qwen_budget300", "deepseek_sanity", "deterministic_validity_suite"]
    summaries = {tier: summary(score_dir / f"{tier}.production.jsonl", sidecars) for tier in tiers}
    diffs = {tier: differential(score_dir / f"{tier}.production.jsonl", score_dir / f"{tier}.reference.jsonl") for tier in tiers}
    report = {
        "schema": "metric_v2_rescore_audit.v1",
        "network_calls_performed": 0,
        "tiers": summaries,
        "differential": diffs,
        "all_binary_components_agree": all(x["binary_component_agreement"] for x in diffs.values()),
        "all_reason_code_sets_agree": all(x["reason_code_set_agreement"] for x in diffs.values()),
        "tier_row_counts": {tier: data["rows"] for tier, data in summaries.items()},
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "rescore_summary.json").write_text(json.dumps({"schema": report["schema"], "network_calls_performed": 0, "tiers": summaries}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.out_dir / "differential_report.json").write_text(json.dumps({"schema": "metric_v2_differential_report.v1", "network_calls_performed": 0, "tiers": diffs, "all_binary_components_agree": report["all_binary_components_agree"], "all_reason_code_sets_agree": report["all_reason_code_sets_agree"]}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.out_dir / "metric_v2_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = ["# Metric v2 offline rescore audit", "", "Network calls performed: 0", "", "| Tier | Rows | Parseable | Output-bearing | Intrinsic | Carried | Joint | Answer |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for tier, data in summaries.items():
        c = data["counts"]
        md.append(f"| {tier} | {data['rows']} | {c['state_parseable_v2']} | {c['output_bearing_present_v2']} | {c['intrinsic_state_validity_v2']} | {c['carried_state_validity_v2']} | {c['joint_answer_state_success_v2']} | {c['answer_success_v2']} |")
    md += ["", f"Binary component agreement: {report['all_binary_components_agree']}", f"Reason-code set agreement: {report['all_reason_code_sets_agree']}"]
    (args.out_dir / "metric_v2_rescore_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"all_binary_components_agree": report["all_binary_components_agree"], "all_reason_code_sets_agree": report["all_reason_code_sets_agree"], "tier_row_counts": report["tier_row_counts"]}, sort_keys=True))
    return 0 if report["all_binary_components_agree"] and report["all_reason_code_sets_agree"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
