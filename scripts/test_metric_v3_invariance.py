#!/usr/bin/env python3
"""Representation-invariance and adapter access gate for V3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metric_v3.evaluator import score_row_v3  # noqa: E402
from metric_v3.serialize import serialize  # noqa: E402


REPS = ("rolling_summary", "visible_carry", "ssr")
SIGNATURE = (
    "representation_parseable_v3",
    "positive_operational_state_present_v3",
    "exclusion_safety_v3",
    "operational_state_sufficiency_v3",
    "answer_state_consistency_v3",
    "intrinsic_state_validity_v3",
    "carried_state_validity_v3",
)


def answer(tokens: list[str], paths: list[str]) -> str:
    return json.dumps({"final_answer": {"required_tokens": tokens, "allowed_paths": paths}})


def representation(rep: str, positive: list[str], negative: list[str], ambiguous: list[str] | None = None,
                   extra: str = "") -> str:
    raw = serialize(rep, positive, negative, ambiguous)
    return raw + extra


def cases() -> list[dict]:
    base = {"task_id": "synthetic_v3_gate", "method": "synthetic", "model": "fixture", "budget": "test",
            "task_relevant_item_universe": ["A", "B", "P", "Q", "R", "A_EXTRA", "ORACLE_SECRET_01"],
            "mandatory_current_facts": ["A", "B"], "admissible_action_options": ["P", "Q"],
            "disallowed_output_items": ["R"], "globally_secret_or_oracle_only_items": ["ORACLE_SECRET_01"]}
    return [
        {"name": "valid", "positive": ["A", "B", "P"], "negative": ["R"], "answer": answer(["A", "B"], ["P"]), "expected": True},
        {"name": "missing_required_fact", "positive": ["A", "P"], "negative": ["R"], "answer": answer(["A"], ["P"]), "expected": False},
        {"name": "revoked_positive", "positive": ["A", "B", "P", "R"], "negative": [], "answer": answer(["A", "B"], ["P"]), "expected": False},
        {"name": "revoked_correctly_excluded", "positive": ["A", "B", "P"], "negative": ["R"], "answer": answer(["A", "B"], ["P"]), "expected": True},
        {"name": "allowed_alternative", "positive": ["A", "B", "Q"], "negative": ["R"], "answer": answer(["A", "B"], ["Q"]), "expected": True},
        {"name": "answer_selected_path_unsupported", "positive": ["A", "B", "Q"], "negative": ["R"], "answer": answer(["A", "B"], ["P"]), "expected": False},
        {"name": "conflicting_polarity", "positive": ["A", "B", "P"], "negative": ["R"], "ambiguous": ["B"], "answer": answer(["A", "B"], ["P"]), "expected": False},
        {"name": "same_prefix_distractor", "positive": ["A_EXTRA", "B", "P"], "negative": ["R"], "answer": answer(["A"], ["P"]), "expected": False},
        {"name": "empty_non_bearing", "positive": [], "negative": [], "answer": answer([], []), "expected": False, "empty": True},
        {"name": "protected_oracle_leak", "positive": ["A", "B", "P"], "negative": ["R"], "answer": answer(["A", "B"], ["P"]), "expected": False,
         "extra": "\nNOTE=ORACLE_SECRET_01 is protected"},
    ]


def run_case(case: dict, rep: str) -> tuple[dict, str]:
    if case.get("empty"):
        raw = {"rolling_summary": "SUMMARY=No active state",
               "visible_carry": "VISIBLE_KEEP=\nNOTE=No active state",
               "ssr": "OUT=\nNOTE=No active state"}[rep]
    else:
        raw = representation(rep, case["positive"], case["negative"], case.get("ambiguous"), case.get("extra", ""))
    task = dict({"task_relevant_item_universe": ["A", "B", "P", "Q", "R", "A_EXTRA", "ORACLE_SECRET_01"],
                 "mandatory_current_facts": ["A", "B"], "admissible_action_options": ["P", "Q"],
                 "disallowed_output_items": ["R"], "globally_secret_or_oracle_only_items": ["ORACLE_SECRET_01"]})
    row = {"row_id": f"{case['name']}::{rep}", "task_id": "synthetic_v3_gate", "method": "synthetic",
           "final_state": raw, "final_output": case["answer"], "final_answer_success_v2": True}
    score = score_row_v3(task, row)
    signature = tuple(bool(score[key]) for key in SIGNATURE)
    return score, json.dumps({"signature": signature, "raw": raw}, ensure_ascii=False, sort_keys=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()
    failures: list[dict] = []
    results: list[dict] = []
    for case in cases():
        by_rep: dict[str, dict] = {}
        details: dict[str, str] = {}
        for rep in REPS:
            score, detail = run_case(case, rep)
            by_rep[rep] = {key: score[key] for key in SIGNATURE}
            details[rep] = detail
            canonical = score["canonical_state_v3"]
            if any(canonical.get(flag) is not False for flag in ("adapter_oracle_status_access", "adapter_answer_access", "adapter_executor_access")):
                failures.append({"case": case["name"], "rep": rep, "reason": "adapter_hidden_access_flag"})
        signatures = {rep: tuple(bool(by_rep[rep][key]) for key in SIGNATURE) for rep in REPS}
        if len(set(signatures.values())) != 1:
            failures.append({"case": case["name"], "reason": "representation_signature_mismatch", "signatures": signatures})
        if signatures[REPS[0]][-1] != case["expected"]:
            failures.append({"case": case["name"], "reason": "unexpected_expected_class", "signature": signatures[REPS[0]], "expected": case["expected"]})
        results.append({"case": case["name"], "expected_carried_state_validity": case["expected"],
                        "signatures": {rep: list(signatures[rep]) for rep in REPS}, "details": details})
    report = {"schema": "carried_state_validity_v3.representation_invariance_report.v1",
              "case_count": len(cases()), "representation_count": len(REPS), "tested_representations": list(REPS),
              "signature_fields": list(SIGNATURE), "adapter_hidden_status_gate_passed": not failures,
              "representation_invariance_passed": not failures, "failures": failures, "results": results,
              "network_calls_performed": 0}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"representation_invariance_passed": not failures, "case_count": len(cases()), "failure_count": len(failures)}, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
