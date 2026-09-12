#!/usr/bin/env python3
"""Combinatorial, metamorphic, and mutation checks for metric v2."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metric_v2.production_scorer import score_row  # noqa: E402


SIDE = {
    "source_task_id": "synthetic_01",
    "required_state_items": ["API_01_AAAAAA", "API_01_BBBBBB"],
    "required_answer_items": ["API_01_AAAAAA", "API_01_BBBBBB"],
    "optional_allowed_items": ["src/api/ok.py"],
    "allowed_answer_paths": ["src/api/ok.py"],
    "disallowed_output_items": ["API_01_CCCCCC", "src/api/blocked.py"],
    "globally_secret_or_oracle_only_items": ["ORACLE_SECRET_01"],
    "final_item_statuses": {"API_01_AAAAAA": "active", "API_01_BBBBBB": "active", "API_01_CCCCCC": "forbidden"},
    "forbidden_exact_tokens": ["API_01_CCCCCC"], "protected_exact_tokens": [],
    "revoked_exact_tokens": [], "stale_exact_tokens": [], "blocked_paths": ["src/api/blocked.py"],
}


def base(state=None, output=None):
    return {
        "row_id": "synthetic_01::r1", "task_id": "synthetic_01", "model": "test", "method": "test",
        "final_state": state if state is not None else {"OUT": ["API_01_AAAAAA", "API_01_BBBBBB"], "ALW": ["src/api/ok.py"]},
        "final_output": output if output is not None else {"final_answer": {"required_tokens": ["API_01_AAAAAA", "API_01_BBBBBB"], "allowed_paths": ["src/api/ok.py"]}},
    }


def check(name, condition, detail=""):
    return {"name": name, "passed": bool(condition), "detail": detail}


def main():
    p = []
    good = score_row(SIDE, base())
    p.append(check("P01_perfect_is_valid", good["carried_state_validity_v2"] and good["joint_answer_state_success_v2"]))
    p.append(check("P02_missing_required_is_invalid", not score_row(SIDE, base({"OUT": ["API_01_AAAAAA"]}))["required_state_completeness_v2"]))
    p.append(check("P03_required_in_exclusion_is_invalid", not score_row(SIDE, base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB"], "NO": ["API_01_BBBBBB"]}))["required_state_completeness_v2"]))
    p.append(check("P04_disallowed_positive_state_breaks_safety", not score_row(SIDE, base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB", "API_01_CCCCCC"]}))["exclusion_safety_v2"]))
    p.append(check("P05_blocked_path_answer_breaks_joint", not score_row(SIDE, base(output={"final_answer": {"required_tokens": ["API_01_AAAAAA", "API_01_BBBBBB"], "allowed_paths": ["src/api/blocked.py"]}}))["joint_answer_state_success_v2"]))
    p.append(check("P06_same_prefix_does_not_satisfy", not score_row(SIDE, base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB_EXTRA"], "ALW": ["src/api/ok.py"]}))["required_state_completeness_v2"]))
    p.append(check("P07_unknown_only_field_not_output", not score_row(SIDE, base({"CURRENT_GOAL": "API_01_AAAAAA API_01_BBBBBB"}))["output_bearing_present_v2"]))
    p.append(check("P08_raw_fallback_not_parseable", not score_row(SIDE, base("unstructured API_01_AAAAAA API_01_BBBBBB"))["state_parseable_v2"]))
    json_state = base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB"], "ALW": ["src/api/ok.py"]})
    assignment_state = base("ALW=src/api/ok.py\nOUT=API_01_AAAAAA, API_01_BBBBBB")
    p.append(check("P09_json_and_assignment_agree", score_row(SIDE, json_state)["carried_state_validity_v2"] == score_row(SIDE, assignment_state)["carried_state_validity_v2"]))
    p.append(check("P10_field_order_invariant", score_row(SIDE, assignment_state)["joint_answer_state_success_v2"] == score_row(SIDE, base("OUT=API_01_AAAAAA,API_01_BBBBBB\nALW=src/api/ok.py"))["joint_answer_state_success_v2"]))
    annotated = base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB"], "ALW": ["src/api/ok.py"], "NOTE": "API_01_CCCCCC remains forbidden"})
    p.append(check("P11_governance_label_does_not_leak_operational_answer", score_row(SIDE, annotated)["answer_success_v2"]))
    p.append(check("P12_validity_is_monotone_under_disallowed_addition", good["carried_state_validity_v2"] and not score_row(SIDE, base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB", "API_01_CCCCCC"], "ALW": ["src/api/ok.py"]}))["carried_state_validity_v2"]))

    mutations = [
        ("M01_omit_required", base({"OUT": ["API_01_AAAAAA"], "ALW": ["src/api/ok.py"]})),
        ("M02_move_required_to_NO", base({"OUT": ["API_01_AAAAAA"], "NO": ["API_01_BBBBBB"], "ALW": ["src/api/ok.py"]})),
        ("M03_insert_disallowed_OUT", base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB", "API_01_CCCCCC"], "ALW": ["src/api/ok.py"]})),
        ("M04_blocked_answer_path", base(output={"final_answer": {"required_tokens": ["API_01_AAAAAA", "API_01_BBBBBB"], "allowed_paths": ["src/api/blocked.py"]}})),
        ("M05_same_prefix_decoy", base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB_EXTRA"], "ALW": ["src/api/ok.py"]})),
        ("M06_raw_state", base("RAW=API_01_AAAAAA,API_01_BBBBBB")),
        ("M07_oracle_only_exposure", base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB"], "NOTE": "ORACLE_SECRET_01"})),
        ("M08_unsupported_answer", base(output={"final_answer": {"required_tokens": ["API_01_AAAAAA", "API_01_BBBBBB", "API_01_CCCCCC"], "allowed_paths": ["src/api/ok.py"]}})),
        ("M09_disallowed_answer", base(output={"final_answer": {"required_tokens": ["API_01_AAAAAA", "API_01_BBBBBB"], "allowed_paths": ["src/api/blocked.py"]}})),
        ("M10_malformed_state", base("{not json")),
        ("M11_remove_output_surface", base({"NOTE": "all required items are remembered"})),
        ("M12_negate_required", base({"OUT": ["API_01_AAAAAA", "API_01_BBBBBB"], "NOTE": "API_01_BBBBBB is forbidden and must not be carried"})),
    ]
    m = []
    for name, row in mutations:
        result = score_row(SIDE, row)
        m.append({"name": name, "killed": not result["carried_state_validity_v2"], "joint_after_mutation": result["joint_answer_state_success_v2"], "reason_codes": result["state_reason_codes_v2"]})
    report = {"schema": "metric_v2_property_mutation_report.v1", "properties": p, "mutations": m, "property_pass_rate": sum(x["passed"] for x in p) / len(p), "mutation_kill_rate": sum(x["killed"] for x in m) / len(m), "passed": all(x["passed"] for x in p) and all(x["killed"] for x in m), "network_calls_performed": 0}
    out = Path("reports/metric_v2/property_mutation_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("property_pass_rate", "mutation_kill_rate", "passed")}, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
