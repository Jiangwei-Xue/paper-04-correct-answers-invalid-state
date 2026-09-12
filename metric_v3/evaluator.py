"""Common V3 validator over adapter-produced canonical state."""

from __future__ import annotations

import json
from typing import Any

from .adapters import adapt_state


def _answer_items(final_output: Any) -> tuple[list[str], list[str], str, bool]:
    if isinstance(final_output, dict):
        obj = final_output
        good = True
    else:
        raw = str(final_output or "")
        try:
            obj = json.loads(raw)
            good = isinstance(obj, dict)
        except Exception:
            return [], [], raw, False
    answer = obj.get("final_answer") if isinstance(obj.get("final_answer"), dict) else obj
    if not isinstance(answer, dict):
        return [], [], json.dumps(obj, ensure_ascii=False, sort_keys=True), good
    tokens: list[str] = []
    paths: list[str] = []
    for key in ("required_tokens", "tokens", "active_tokens", "final_active_set"):
        value = answer.get(key)
        if isinstance(value, list): tokens.extend(str(item) for item in value)
    for key in ("allowed_paths", "paths", "files"):
        value = answer.get(key)
        if isinstance(value, list): paths.extend(str(item) for item in value)
    operational = {key: value for key, value in answer.items() if key not in {"state_labels", "state_transitions", "boundary_checks"}}
    return list(dict.fromkeys(tokens)), list(dict.fromkeys(paths)), json.dumps(operational, ensure_ascii=False, sort_keys=True), good


def score_row_v3(task: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    visible = list(task.get("task_relevant_item_universe", []))
    canonical = adapt_state(row.get("final_state", ""), visible)
    positive = set(canonical["positive_operational_items"])
    ambiguous = set(canonical["ambiguous_items"])
    negative = set(canonical["negative_or_excluded_items"])
    mandatory = set(task.get("mandatory_current_facts", []))
    options = set(task.get("admissible_action_options", []))
    disallowed = set(task.get("disallowed_output_items", []))
    oracle_only = set(task.get("globally_secret_or_oracle_only_items", []))
    tokens, paths, _, answer_parseable = _answer_items(row.get("final_output", ""))
    answer_items = tokens + paths
    missing_mandatory = sorted(mandatory - positive)
    unsupported_options = sorted(options & positive)
    disallowed_positive = sorted(disallowed & positive)
    oracle_exposure = sorted(oracle_only & set(positive | negative | ambiguous))
    sufficiency = bool(canonical["representation_parseable_v3"] and mandatory <= positive and bool(unsupported_options) and not ambiguous)
    positive_present = bool(canonical["representation_parseable_v3"] and positive)
    safety = not disallowed_positive and not oracle_exposure and not ambiguous
    consistency_failures: list[str] = []
    for item in answer_items:
        if item in disallowed:
            consistency_failures.append(f"ANSWER_DISALLOWED:{item}")
        elif item not in positive:
            consistency_failures.append(f"ANSWER_UNSUPPORTED:{item}")
        elif item in negative or item in ambiguous:
            consistency_failures.append(f"ANSWER_NEGATED:{item}")
    consistency = bool(answer_parseable and not consistency_failures)
    intrinsic = bool(canonical["representation_parseable_v3"] and positive_present and safety and sufficiency)
    carried = bool(intrinsic and consistency)
    reasons: list[str] = []
    if not canonical["representation_parseable_v3"]: reasons.append("V3_PARSE_FAILURE")
    if not positive_present: reasons.append("V3_NO_POSITIVE_OPERATIONAL_STATE")
    if missing_mandatory: reasons.append("V3_MISSING_MANDATORY_FACT")
    if not unsupported_options: reasons.append("V3_NO_ADMISSIBLE_ACTION_OPTION")
    if disallowed_positive: reasons.append("V3_DISALLOWED_POSITIVE_STATE")
    if oracle_exposure: reasons.append("V3_ORACLE_ONLY_EXPOSURE")
    if ambiguous: reasons.append("V3_AMBIGUOUS_POLARITY")
    reasons.extend(consistency_failures)
    return {
        "row_id": row.get("row_id") or row.get("baseline_row_id") or row.get("task_id", ""),
        "task_id": row.get("task_id", ""), "method": row.get("method", ""), "model": row.get("model", ""),
        "budget": row.get("budget", row.get("state_budget", "")), "run_id": row.get("run_id", row.get("run_index", "")),
        "representation_parseable_v3": bool(canonical["representation_parseable_v3"]),
        "positive_operational_state_present_v3": positive_present,
        "exclusion_safety_v3": safety,
        "operational_state_sufficiency_v3": sufficiency,
        "answer_state_consistency_v3": consistency,
        "intrinsic_state_validity_v3": intrinsic,
        "carried_state_validity_v3": carried,
        "final_answer_success_v2": bool(row.get("final_answer_success_v2", row.get("answer_success_v2", False))),
        "joint_final_answer_state_success_v3": bool(row.get("final_answer_success_v2", row.get("answer_success_v2", False)) and carried),
        "v3_missing_mandatory_facts": missing_mandatory,
        "v3_supported_action_options": sorted(unsupported_options),
        "v3_disallowed_positive_items": disallowed_positive,
        "v3_oracle_only_exposure": oracle_exposure,
        "v3_answer_consistency_failures": consistency_failures,
        "v3_reason_codes": sorted(set(reasons)),
        "canonical_state_v3": canonical,
    }
