#!/usr/bin/env python3
"""Strict scorer wrapper for the PCG dynamic-state v2 main matrix.

This file intentionally leaves the historical v2 scorer untouched.  The main
matrix scorer imports it, keeps its answer/boundary logic, and tightens the
state-governance metric so an empty or non-bearing carried state cannot receive
full governance credit.  This closes the loop-only "empty governance" hole
observed in the 104-row decisive probe.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE_SCORER_PATH = PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_outputs.py"


def load_base_scorer() -> Any:
    spec = importlib.util.spec_from_file_location("pcg_dynamic_state_v2_base_scorer", BASE_SCORER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base scorer: {BASE_SCORER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base_scorer()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_tasks(path: Path) -> dict[str, dict[str, Any]]:
    return {row["task_id"]: row for row in read_jsonl(path)}


def _state_text(final_state: Any) -> str:
    if isinstance(final_state, str):
        return final_state
    return json.dumps(final_state, ensure_ascii=False, sort_keys=True)


def state_carry_surface_present(task: dict[str, Any], output_row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Require non-empty carried state with output-bearing evidence.

    A state is governance-bearing if it carries at least one required active
    token in any parsed state surface, or if it contains an output-bearing state
    field.  This is deliberately stricter than "no contradiction"; an empty
    state is not a governed state.
    """
    final_state = _state_text(output_row.get("final_state", ""))
    fields = BASE.parse_state_fields(final_state)
    all_text = "\n".join(fields.values()) if fields else final_state
    output_bearing_text = BASE.state_surface(fields, BASE.OUTPUT_BEARING_STATE_FIELDS)
    required = list(task["oracle"]["required_exact_tokens"])
    allowed_paths = list(task["oracle"].get("allowed_paths", []))

    required_token_present = any(token in all_text for token in required)
    allowed_path_present = any(path in all_text for path in allowed_paths)
    output_field_present = bool(output_bearing_text.strip())
    non_empty_state = bool(final_state.strip())
    present = non_empty_state and (required_token_present or allowed_path_present or output_field_present)
    audit = {
        "non_empty_state": non_empty_state,
        "required_token_present_in_state": required_token_present,
        "allowed_path_present_in_state": allowed_path_present,
        "output_bearing_state_field_present": output_field_present,
        "parsed_state_fields": sorted(fields.keys()),
    }
    return present, audit


def score_task(task: dict[str, Any], output_row: dict[str, Any]) -> dict[str, Any]:
    score = BASE.score_task(task, output_row)
    carry_present, audit = state_carry_surface_present(task, output_row)
    legacy_governance = bool(score["state_governance_success"])
    strict_governance = legacy_governance and carry_present

    score["state_governance_success_legacy_no_conflict_only"] = legacy_governance
    score["state_carry_surface_present"] = carry_present
    score["state_governance_success"] = strict_governance
    score["reliable_composite_success"] = bool(score["answer_success"]) and strict_governance
    score["reliable_success"] = score["reliable_composite_success"]
    score["state_governance_audit"] = audit
    return score


def strict_dummy_rows_for_task(task: dict[str, Any]) -> list[dict[str, Any]]:
    rows = BASE.dummy_rows_for_task(task)
    rows.append(
        {
            "dummy_case": "perfect_answer_empty_state",
            "task_id": task["task_id"],
            "final_output": BASE.perfect_output(task),
            "final_state": "",
            "expected_reliable_success": False,
        }
    )
    rows.append(
        {
            "dummy_case": "perfect_answer_nonbearing_state",
            "task_id": task["task_id"],
            "final_output": BASE.perfect_output(task),
            "final_state": "No contradictions detected.",
            "expected_reliable_success": False,
        }
    )
    return rows


def run_dummy_tests(tasks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    empty_state_fail_count = 0
    nonbearing_state_fail_count = 0
    for task in tasks:
        for row in strict_dummy_rows_for_task(task):
            score = score_task(task, row)
            score["dummy_case"] = row["dummy_case"]
            score["expected_reliable_success"] = row["expected_reliable_success"]
            score["dummy_expectation_passed"] = bool(score["reliable_success"]) == bool(row["expected_reliable_success"])
            scored.append(score)
            if row["dummy_case"] == "perfect_answer_empty_state" and not score["reliable_success"]:
                empty_state_fail_count += 1
            if row["dummy_case"] == "perfect_answer_nonbearing_state" and not score["reliable_success"]:
                nonbearing_state_fail_count += 1
            if not score["dummy_expectation_passed"]:
                failures.append(score)

    summary = {
        "tasks": len(tasks),
        "dummy_rows": len(scored),
        "expectation_failures": len(failures),
        "empty_state_correctly_fails_count": empty_state_fail_count,
        "empty_state_correctly_fails_rate": empty_state_fail_count / len(tasks) if tasks else 0.0,
        "nonbearing_state_correctly_fails_count": nonbearing_state_fail_count,
        "nonbearing_state_correctly_fails_rate": nonbearing_state_fail_count / len(tasks) if tasks else 0.0,
        "passed": not failures
        and (empty_state_fail_count / len(tasks) if tasks else 0.0) == 1.0
        and (nonbearing_state_fail_count / len(tasks) if tasks else 0.0) == 1.0,
    }
    return scored, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle", required=True, type=Path)
    parser.add_argument("--outputs", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--dummy-tests", action="store_true")
    args = parser.parse_args()

    tasks = load_tasks(args.oracle)
    if args.dummy_tests:
        rows, summary = run_dummy_tests(list(tasks.values()))
        write_jsonl(args.out, rows)
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0 if summary["passed"] else 1

    if not args.outputs:
        print("--outputs is required unless --dummy-tests is used")
        return 2
    output_rows = read_jsonl(args.outputs)
    scored = []
    for row in output_rows:
        task_id = row.get("task_id")
        if task_id not in tasks:
            raise SystemExit(f"Unknown task_id in outputs: {task_id}")
        scored.append(score_task(tasks[task_id], row))
    write_jsonl(args.out, scored)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
