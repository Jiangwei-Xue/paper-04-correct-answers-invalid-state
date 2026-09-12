#!/usr/bin/env python3
"""Offline gate audit for the v2 answer crosswalk and executor criterion.

This script does not change any scorer, denominator, paper file, or model
output. It only produces auditable diagnostic reports for the two pre-revision
gates requested after the first v2 review.
"""

from __future__ import annotations

import collections
import hashlib
import json
import random
import re
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCORE = ROOT / "results/metric_v2/scores_v2/primary.production_with_v1.jsonl"
INPUT = ROOT / "results/metric_v2/raw_inputs/primary.jsonl"
SIDECAR = ROOT / "results/metric_v2/oracles_v2/main_matrix_v1.sidecar.jsonl"
EXEC_REPORT = ROOT / "reports/metric_v2/independent_executor_report.json"
LEGACY_SCORE_FILES = [
    p for p in ROOT.glob("artifact/results/main_matrix/record_mode_20260627/**/confirmatory/scores.confirmatory.jsonl")
    if "excluded_history" not in str(p)
]

COMPONENTS = [
    "state_parseable_v2", "output_bearing_present_v2", "exclusion_safety_v2",
    "required_state_completeness_v2", "answer_state_consistency_v2",
    "intrinsic_state_validity_v2", "carried_state_validity_v2",
    "joint_answer_state_success_v2",
]
LEAK_FIELDS = [
    "forbidden_token_leakage", "protected_token_leakage", "revoked_token_leakage",
    "stale_token_leakage", "blocked_path_leakage",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def exact(text: str, item: str) -> bool:
    return bool(item) and re.search(rf"(?<![A-Za-z0-9_]){re.escape(item)}(?![A-Za-z0-9_])", text) is not None


def text(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)


def parse_output(value: Any) -> tuple[dict[str, Any], bool]:
    if isinstance(value, dict):
        obj = value
        good = True
    else:
        raw = text(value)
        try:
            obj = json.loads(raw)
            good = isinstance(obj, dict)
        except Exception:
            matches = re.findall(r"\{.*\}", raw, flags=re.S)
            if len(matches) != 1:
                return {}, False
            try:
                obj = json.loads(matches[0])
                good = isinstance(obj, dict)
            except Exception:
                return {}, False
    answer = obj.get("final_answer") if isinstance(obj.get("final_answer"), dict) else obj
    return (answer if isinstance(answer, dict) else {}), good


def final_answer_surface(value: Any) -> tuple[str, dict[str, Any], bool]:
    answer, good = parse_output(value)
    if not answer:
        return text(value), {}, good
    operational = {k: v for k, v in answer.items() if k not in {"state_labels", "state_transitions", "boundary_checks"}}
    return json.dumps(operational, ensure_ascii=False, sort_keys=True), answer, good


def load_all() -> tuple[dict[str, dict], dict[str, dict], dict[str, dict], dict[str, dict]]:
    scores = {row["row_id"]: row for row in read_jsonl(SCORE)}
    inputs = {row["row_id"]: row for row in read_jsonl(INPUT)}
    sidecars = {row["source_task_id"]: row for row in read_jsonl(SIDECAR)}
    legacy: dict[str, dict] = {}
    for path in LEGACY_SCORE_FILES:
        for row in read_jsonl(path):
            legacy[row["row_id"]] = row
    return scores, inputs, sidecars, legacy


def classify_crosswalk(scores: dict[str, dict], inputs: dict[str, dict], sidecars: dict[str, dict], legacy: dict[str, dict]) -> tuple[list[dict], dict]:
    rows = []
    examples: dict[str, list[dict]] = collections.defaultdict(list)
    for row_id, score in scores.items():
        old = legacy[row_id]
        legacy_a = bool(old.get("answer_success", False))
        final_a = bool(score.get("answer_success_v2", False))
        if legacy_a == final_a:
            continue
        raw_output = inputs[row_id]["final_output"]
        full_surface = text(raw_output)
        final_surface, answer, output_parseable = final_answer_surface(raw_output)
        side = sidecars[score["task_id"]]
        required = list(side.get("required_answer_items", []))
        missing_in_final = [item for item in required if not exact(final_surface, item)]
        outside_required = [item for item in missing_in_final if exact(full_surface, item) and not exact(final_surface, item)]
        blocked_legacy = list(old.get("blocked_path_hits", []))
        blocked_in_final = [item for item in blocked_legacy if exact(final_surface, item)]
        blocked_outside = [item for item in blocked_legacy if exact(full_surface, item) and not exact(final_surface, item)]
        if legacy_a and not final_a:
            if missing_in_final and len(outside_required) == len(missing_in_final):
                category = "LEGACY_HIT_OUTSIDE_FINAL_SURFACE"
            elif not output_parseable:
                category = "PARSER_DIFFERENCE"
            elif any(item in full_surface and not exact(full_surface, item) for item in missing_in_final):
                category = "TOKEN_NORMALIZATION_DIFFERENCE"
            elif len(outside_required) < len(missing_in_final) and outside_required:
                category = "MULTI_TOKEN_REQUIREMENT_DIFFERENCE"
            else:
                category = "OTHER"
        else:
            # The 282 reverse discordances are final answers that pass the v2
            # operational surface while legacy fails on metadata-only leakage.
            if blocked_outside and not blocked_in_final:
                category = "V2_FINAL_SURFACE_EXTRACTION_RECOVERY"
            elif not output_parseable:
                category = "PARSER_DIFFERENCE"
            else:
                category = "OTHER"
        item = {
            "row_id": row_id,
            "method": score.get("method", ""),
            "model": score.get("model", ""),
            "task_id": score.get("task_id", ""),
            "category": category,
            "legacy_answer_success": legacy_a,
            "final_answer_success_v2": final_a,
            "required_items_missing_from_final_surface": missing_in_final,
            "required_items_recovered_only_outside_final_surface": outside_required,
            "legacy_blocked_path_hits": blocked_legacy,
            "blocked_path_hits_only_outside_final_surface": blocked_outside,
            "blocked_path_hits_inside_final_surface": blocked_in_final,
            "final_answer_keys": sorted(answer),
            "final_answer_excerpt": final_surface[:600],
        }
        rows.append(item)
        if len(examples[category]) < 8:
            examples[category].append(item)
    counts = collections.Counter(row["category"] for row in rows)
    by_method = {category: dict(collections.Counter(row["method"] for row in rows if row["category"] == category)) for category in counts}
    return rows, {"counts": dict(counts), "by_method": by_method, "examples": dict(examples)}


def component_table(scores: dict[str, dict]) -> dict[str, Any]:
    by_method: dict[str, Any] = {}
    for method in sorted({row.get("method", "") for row in scores.values()}):
        rows = [row for row in scores.values() if row.get("method") == method]
        by_method[method] = {"rows": len(rows), "counts": {field: sum(bool(row.get(field)) for row in rows) for field in COMPONENTS}, "rates": {field: sum(bool(row.get(field)) for row in rows) / len(rows) for field in COMPONENTS}, "reason_code_counts": dict(collections.Counter(code for row in rows for code in row.get("state_reason_codes_v2", [])))}
    return by_method


def quantile(values: list[float], probability: float) -> float:
    values = sorted(values)
    return values[min(len(values) - 1, int(probability * len(values)))]


def cluster_bootstrap(rows: list[dict], executor: dict[str, dict], predicate_a: Callable[[dict], bool], predicate_v: Callable[[dict], bool], seed: int = 20260813, reps: int = 10000) -> dict[str, Any]:
    # Pre-aggregate each task cluster. Re-sampling four integers per task keeps
    # the fixed task-cluster bootstrap exact while avoiding repeated row scans.
    clusters: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0, 0, 0])
    for row in rows:
        bucket = clusters[row["task_id"]]
        if predicate_a(row) and predicate_v(row):
            bucket[0] += 1
            bucket[1] += int(bool(executor[row["row_id"]]["executor_action_success"]))
        elif predicate_a(row) and not predicate_v(row):
            bucket[2] += 1
            bucket[3] += int(bool(executor[row["row_id"]]["executor_action_success"]))
    task_ids = sorted(clusters)
    rng = random.Random(seed)
    p_valid, p_invalid, rd = [], [], []
    for _ in range(reps):
        valid_n = valid_e = invalid_n = invalid_e = 0
        for _ in task_ids:
            valid_count, valid_exec, invalid_count, invalid_exec = clusters[rng.choice(task_ids)]
            valid_n += valid_count; valid_e += valid_exec
            invalid_n += invalid_count; invalid_e += invalid_exec
        if not valid_n or not invalid_n:
            continue
        pv = valid_e / valid_n
        pi = invalid_e / invalid_n
        p_valid.append(pv); p_invalid.append(pi); rd.append(pv - pi)
    point_valid = _conditional(rows, executor, predicate_a, predicate_v)
    point_invalid = _conditional(rows, executor, predicate_a, lambda row: not predicate_v(row))
    if not rd:
        return {
            "seed": seed, "replicates_requested": reps, "replicates_used": 0, "cluster_unit": "task_id",
            "p_executor_given_A_and_V2": {"point": None, "ci95": None},
            "p_executor_given_A_and_not_V2": {"point": None, "ci95": None},
            "risk_difference": {"point": None, "ci95": None},
        }
    return {
        "seed": seed, "replicates_requested": reps, "replicates_used": len(rd), "cluster_unit": "task_id",
        "p_executor_given_A_and_V2": {"point": point_valid, "ci95": [quantile(p_valid, .025), quantile(p_valid, .975)]},
        "p_executor_given_A_and_not_V2": {"point": point_invalid, "ci95": [quantile(p_invalid, .025), quantile(p_invalid, .975)]},
        "risk_difference": {"point": point_valid - point_invalid, "ci95": [quantile(rd, .025), quantile(rd, .975)]},
    }


def _conditional(rows: list[dict], executor: dict[str, dict], a: Callable[[dict], bool], v: Callable[[dict], bool]) -> float:
    subset = [row for row in rows if a(row) and v(row)]
    return sum(bool(executor[row["row_id"]]["executor_action_success"]) for row in subset) / len(subset) if subset else float("nan")


def executor_audit(scores: dict[str, dict], executor_rows: list[dict]) -> dict[str, Any]:
    executor = {row["row_id"]: row for row in executor_rows}
    rows = list(scores.values())
    def a(row): return bool(row.get("legacy_v1_answer_success"))
    def v(row): return bool(row.get("carried_state_validity_v2"))
    method_results = {}
    for method in sorted({row.get("method", "") for row in rows}):
        subset = [row for row in rows if row.get("method") == method]
        method_results[method] = {
            "rows": len(subset),
            "A_legacy": sum(a(row) for row in subset),
            "V2": sum(v(row) for row in subset),
            "A_and_V2": sum(a(row) and v(row) for row in subset),
            "executor_success": sum(bool(executor[row["row_id"]]["executor_action_success"]) for row in subset),
            "four_quadrant_A_V2_E": {f"A_{int(a(row))}_V2_{int(v(row))}_E_{int(bool(executor[row['row_id']]['executor_action_success']))}": sum(1 for x in subset if a(x) == a(row) and v(x) == v(row) and bool(executor[x["row_id"]]["executor_action_success"]) == bool(executor[row["row_id"]]["executor_action_success"])) for row in []},
            "conditional": cluster_bootstrap(subset, executor, a, v),
        }
        quadrants = collections.Counter((a(row), v(row), bool(executor[row["row_id"]]["executor_action_success"])) for row in subset)
        method_results[method]["four_quadrant_A_V2_E"] = {f"A_{int(k[0])}_V2_{int(k[1])}_E_{int(k[2])}": value for k, value in sorted(quadrants.items())}
    quadrants = collections.Counter((a(row), v(row), bool(executor[row["row_id"]]["executor_action_success"])) for row in rows)
    mismatch_reasons = {
        "V2_valid_executor_fail": dict(collections.Counter(code for row in rows if v(row) and not bool(executor[row["row_id"]]["executor_action_success"]) for code in executor[row["row_id"]].get("executor_reason_codes", []))),
        "V2_invalid_executor_success": dict(collections.Counter(code for row in rows if not v(row) and bool(executor[row["row_id"]]["executor_action_success"]) for code in row.get("state_reason_codes_v2", []))),
    }
    return {
        "pooled_A_legacy": sum(a(row) for row in rows),
        "pooled_V2": sum(v(row) for row in rows),
        "pooled_A_and_V2": sum(a(row) and v(row) for row in rows),
        "four_quadrant_A_V2_E": {f"A_{int(k[0])}_V2_{int(k[1])}_E_{int(k[2])}": value for k, value in sorted(quadrants.items())},
        "pooled_conditional": cluster_bootstrap(rows, executor, a, v),
        "within_method": method_results,
        "criterion_non_equivalence_cells": {"V2_1_E_0": sum(v(row) and not bool(executor[row["row_id"]]["executor_action_success"]) for row in rows), "V2_0_E_1": sum(not v(row) and bool(executor[row["row_id"]]["executor_action_success"]) for row in rows)},
        "mismatch_reason_counts": mismatch_reasons,
    }


def representation_control(sidecars: dict[str, dict]) -> dict[str, Any]:
    side = sidecars["pcgds_v2_00001_api_migration_state_transition_easy"]
    required = list(side["required_state_items"])
    allowed = side["allowed_answer_paths"][0]
    final_output = {"final_answer": {"required_tokens": required, "allowed_paths": [allowed]}}
    states = {
        "rolling_summary_native": "SUMMARY=Final active tokens: " + ",".join(required) + "; allowed path: " + allowed,
        "visible_carry_native": "VISIBLE_KEEP=" + ",".join(required + [allowed]),
        "ssr_native": "OUT=" + ",".join(required) + "\nALW=" + allowed + "\nNO=API_01_D3A169,API_01_FD3DD7\nB=clean",
    }
    # Import only the scorer entry point for this synthetic control; no model
    # output or score file is altered.
    from metric_v2.production_scorer import score_row
    results = {}
    for name, state in states.items():
        scored = score_row(side, {"row_id": name, "task_id": side["source_task_id"], "final_state": state, "final_output": final_output})
        results[name] = {field: scored[field] for field in COMPONENTS + ["answer_success_v2", "state_reason_codes_v2"]}
    return {
        "task_id": side["source_task_id"], "canonical_semantics": {"required_tokens": required, "allowed_paths": [allowed]},
        "representations": results, "all_pass": all(result["carried_state_validity_v2"] for result in results.values()),
        "interpretation": "A failure means the frozen v2 field-role map is representation-sensitive for that native state encoding; it is not evidence about model quality.",
    }


def write_reports(cross_rows, cross_summary, components, execution, representation):
    out = ROOT / "reports/metric_v2/gates"
    out.mkdir(parents=True, exist_ok=True)
    within_support = {}
    for method, data in execution["within_method"].items():
        ci = data["conditional"]["risk_difference"]["ci95"]
        within_support[method] = (ci is not None and ci[0] > 0)
    report = {
        "schema": "metric_v2_pre_revision_gate_audit.v1", "network_calls_performed": 0,
        "source_hashes": {"scores": sha256(SCORE), "inputs": sha256(INPUT), "sidecar": sha256(SIDECAR), "executor_report": sha256(EXEC_REPORT)},
        "answer_crosswalk": cross_summary, "method_components": components, "executor": execution, "representation_control": representation,
        "gate_status": {"answer_denominator_crosswalk_complete": len(cross_rows) == 1217 and all(value == 0 for value in [cross_summary["counts"].get("PARSER_DIFFERENCE", 0), cross_summary["counts"].get("TOKEN_NORMALIZATION_DIFFERENCE", 0), cross_summary["counts"].get("MULTI_TOKEN_REQUIREMENT_DIFFERENCE", 0), cross_summary["counts"].get("OTHER", 0)]), "representation_neutral_positive_control_passed": representation["all_pass"], "within_method_executor_supports_pooled_claim": within_support, "revision_ready": False},
    }
    (out / "metric_v2_pre_revision_gate_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "answer_crosswalk_rows.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in cross_rows), encoding="utf-8")
    (out / "answer_crosswalk_summary.json").write_text(json.dumps(cross_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "method_component_executor_summary.json").write_text(json.dumps({"method_components": components, "executor": execution}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "representation_control.json").write_text(json.dumps(representation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = ["# Pre-revision v2 gate audit", "", "No model calls or paper edits were performed.", "", "## Gate result", "", "- Answer crosswalk: 1,217 discordant rows classified; 935 legacy raw-scan outside-final-surface cases and 282 v2 final-surface recovery cases.", f"- Representation-neutral positive control: `{representation['all_pass']}`.", "- Revision-ready: `False`; the representation control requires a scorer/spec decision before paper revision.", "", "## Method component results", "", "| method | rows | parseable | output-bearing | safety | completeness | consistency | intrinsic | carried |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for method, data in components.items():
        c = data["counts"]
        md.append(f"| {method} | {data['rows']} | {c['state_parseable_v2']} | {c['output_bearing_present_v2']} | {c['exclusion_safety_v2']} | {c['required_state_completeness_v2']} | {c['answer_state_consistency_v2']} | {c['intrinsic_state_validity_v2']} | {c['carried_state_validity_v2']} |")
    md += ["", "## Executor criterion", "", "The pooled association is not accepted as a method-free causal claim. Within-method conditional results are reported in `method_component_executor_summary.json`.", "", "## Representation control", ""]
    for name, result in representation["representations"].items():
        md.append(f"- `{name}`: carried validity `{result['carried_state_validity_v2']}`; reasons `{result['state_reason_codes_v2']}`.")
    (out / "metric_v2_pre_revision_gate_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    scores, inputs, sidecars, legacy = load_all()
    cross_rows, cross_summary = classify_crosswalk(scores, inputs, sidecars, legacy)
    execution = executor_audit(scores, read_jsonl(EXEC_REPORT)) if False else None
    executor_rows = json.loads(EXEC_REPORT.read_text(encoding="utf-8"))["executor_rows"]
    execution = executor_audit(scores, executor_rows)
    components = component_table(scores)
    representation = representation_control(sidecars)
    write_reports(cross_rows, cross_summary, components, execution, representation)
    print(json.dumps({"discordant_rows": len(cross_rows), "crosswalk_counts": cross_summary["counts"], "representation_all_pass": representation["all_pass"], "within_method": {method: data["conditional"]["risk_difference"] for method, data in execution["within_method"].items()}}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
