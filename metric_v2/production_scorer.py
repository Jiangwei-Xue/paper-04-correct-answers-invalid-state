#!/usr/bin/env python3
"""Production Carried-State Validity v2 scorer.

This module is deliberately separate from the frozen v1 scorer. It is
deterministic and offline; the only task semantics it consumes are the
derived oracle sidecars.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .common import (
    ANNOTATION_FIELDS, EXCLUSION_FIELDS, OUTPUT_FIELDS, answer_object,
    exact_present, extract_answer_items, operational_answer_text, read_jsonl,
    stringify, write_jsonl,
)


FIELD_RE = re.compile(r"(?P<key>[A-Za-z][A-Za-z0-9_]*)\s*=\s*", flags=re.I)


def parse_state(value: Any) -> tuple[dict[str, list[str]], bool, str, str]:
    """Parse JSON-object or assignment state into keyed surfaces."""
    fields: dict[str, list[str]] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            fields.setdefault(str(key).upper(), []).append(stringify(item))
        return fields, "RAW" not in fields, "json_object", ""
    text = str(value or "").strip()
    if not text:
        return {}, False, "missing", "PARSE_MISSING"
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            for key, item in obj.items():
                fields.setdefault(str(key).upper(), []).append(stringify(item))
            if "RAW" in fields:
                return fields, False, "json_raw_fallback", "PARSE_RAW_FALLBACK"
            return fields, True, "json_object", ""
    except Exception:
        pass
    matches = list(FIELD_RE.finditer(text))
    if not matches:
        return {"RAW": [text]}, False, "raw_text", "PARSE_RAW_FALLBACK"
    for index, match in enumerate(matches):
        key = match.group("key").upper()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        fields.setdefault(key, []).append(text[match.end():end].strip(" ;\n\t"))
    if "RAW" in fields:
        return fields, False, "assignment_raw_fallback", "PARSE_RAW_FALLBACK"
    return fields, True, "field_assignments", ""


def field_text(fields: dict[str, list[str]], names: set[str]) -> str:
    return "\n".join(value for key, values in fields.items() if key in names for value in values)


def all_state_text(fields: dict[str, list[str]], original: Any) -> str:
    return "\n".join(value for values in fields.values() for value in values) or stringify(original)


def directly_negated(text: str, item: str) -> bool:
    if not exact_present(text, item):
        return False
    x = re.escape(item)
    neg = r"superseded|obsolete|stale|deprecated|revoked|forbidden|blocked|protected|invalid|archive[- ]only|rollback[- ]only|must not|do not use|do not output|not outputtable"
    patterns = (
        rf"{x}.{{0,80}}(?:is|are|was|were|remains|remain|marked|listed|treated|labeled|labelled).{{0,60}}(?:{neg})",
        rf"(?:{neg}).{{0,40}}[:=].{{0,100}}{x}",
        rf"{x}.{{0,40}}(?:must not|do not|should not).{{0,40}}(?:carry|use|output)",
    )
    return any(re.search(p, text, flags=re.I | re.S) for p in patterns)


def score_row(task: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    sidecar = task
    final_output = row.get("final_output", row.get("output", ""))
    answer, output_raw_text, answer_parseable, answer_parse_reason = answer_object(final_output)
    answer_tokens, answer_paths = extract_answer_items(answer, output_raw_text)
    operation_text = operational_answer_text(answer, output_raw_text)
    final_state = row.get("final_state", "")
    fields, parseable, parse_reason, parse_code = parse_state(final_state)
    output_text = field_text(fields, OUTPUT_FIELDS)
    exclusion_text = field_text(fields, EXCLUSION_FIELDS)
    all_text = all_state_text(fields, final_state)

    required = list(sidecar.get("required_state_items", []))
    disallowed = list(sidecar.get("disallowed_output_items", []))
    oracle_only = list(sidecar.get("globally_secret_or_oracle_only_items", []))
    required_answer = list(sidecar.get("required_answer_items", required))
    forbidden = list(sidecar.get("forbidden_exact_tokens", []))
    protected = list(sidecar.get("protected_exact_tokens", []))
    revoked = list(sidecar.get("revoked_exact_tokens", []))
    stale = list(sidecar.get("stale_exact_tokens", []))
    blocked_paths = list(sidecar.get("blocked_paths", []))
    if not forbidden and not protected and not revoked and not stale:
        labels = sidecar.get("final_item_statuses", {})
        forbidden = [x for x, label in labels.items() if label == "forbidden"]
        protected = [x for x, label in labels.items() if label == "protected"]
        revoked = [x for x, label in labels.items() if label == "revoked"]
        stale = [x for x, label in labels.items() if label == "stale"]

    missing_required = [item for item in required if not exact_present(output_text, item)]
    negated_required = [item for item in required if directly_negated(all_text, item) or exact_present(exclusion_text, item)]
    state_required_complete = bool(parseable and not missing_required and not negated_required)
    output_present = bool(parseable and output_text.strip())
    state_disallowed_hits = [item for item in disallowed if exact_present(output_text, item)]
    oracle_only_hits = [item for item in oracle_only if exact_present(all_text, item)]
    exclusion_safety = not state_disallowed_hits and not oracle_only_hits

    consistency_failures: list[str] = []
    for item in answer_tokens + answer_paths:
        if item in disallowed:
            consistency_failures.append(f"ANSWER_DISALLOWED:{item}")
        elif not exact_present(output_text, item):
            consistency_failures.append(f"ANSWER_UNSUPPORTED:{item}")
        elif exact_present(exclusion_text, item) or directly_negated(all_text, item):
            consistency_failures.append(f"ANSWER_NEGATED:{item}")
    answer_state_consistent = bool(parseable and output_present and not consistency_failures)

    present_required_answer = [x for x in required_answer if exact_present(operation_text, x)]
    missing_answer = [x for x in required_answer if x not in present_required_answer]
    forbidden_hits = [x for x in forbidden if exact_present(operation_text, x)]
    protected_hits = [x for x in protected if exact_present(operation_text, x)]
    revoked_hits = [x for x in revoked if exact_present(operation_text, x)]
    stale_hits = [x for x in stale if exact_present(operation_text, x)]
    blocked_hits = [x for x in blocked_paths if exact_present(operation_text, x)]
    answer_success = not missing_answer and not (forbidden_hits or protected_hits or revoked_hits or stale_hits or blocked_hits)

    intrinsic = parseable and output_present and exclusion_safety and state_required_complete
    carried = intrinsic and answer_state_consistent
    joint = answer_success and carried
    state_conflict = bool(negated_required or state_disallowed_hits)
    reasons: list[str] = []
    if not parseable:
        # A field record containing an explicit RAW field remains a parse
        # failure, but its structural reason is still an assignment record;
        # keep this code aligned with the independent reference scorer.
        if parse_reason in {"field_assignments", "assignment_raw_fallback"}:
            reasons.append("PARSE_ASSIGNMENTS")
        else:
            reasons.append(parse_code or f"PARSE_{parse_reason.upper()}")
    if not output_present: reasons.append("NO_OUTPUT_BEARING_STATE")
    if missing_required: reasons.append("MISSING_REQUIRED_STATE")
    if negated_required: reasons.append("REQUIRED_STATE_NEGATED")
    if state_disallowed_hits: reasons.append("DISALLOWED_STATE_OUTPUT")
    if oracle_only_hits: reasons.append("ORACLE_ONLY_LITERAL_EXPOSURE")
    reasons.extend(consistency_failures)
    if missing_answer: reasons.append("ANSWER_REQUIRED_MISSING")
    if forbidden_hits or protected_hits or revoked_hits or stale_hits or blocked_hits: reasons.append("ANSWER_BOUNDARY_LEAK")

    # Preserve names used by the v1 reports for side-by-side auditing.
    state_governance_v1 = not state_conflict
    reliable_v1 = answer_success and state_governance_v1
    row_id = row.get("row_id") or row.get("baseline_row_id") or row.get("task_id") or ""
    return {
        "row_id": row_id,
        "task_id": row.get("task_id", ""),
        "method": row.get("method", ""),
        "model": row.get("model", ""),
        "budget": row.get("budget", row.get("state_budget", "")),
        "run_id": row.get("run_id", row.get("run_index", "")),
        "state_parseable_v2": bool(parseable),
        "output_bearing_present_v2": bool(output_present),
        "exclusion_safety_v2": bool(exclusion_safety),
        "required_state_completeness_v2": bool(state_required_complete),
        "answer_state_consistency_v2": bool(answer_state_consistent),
        "intrinsic_state_validity_v2": bool(intrinsic),
        "carried_state_validity_v2": bool(carried),
        "joint_answer_state_success_v2": bool(joint),
        "answer_success_v2": bool(answer_success),
        "answer_success": bool(answer_success),
        "state_governance_success_v1": bool(state_governance_v1),
        "reliable_composite_success_v1": bool(reliable_v1),
        "required_state_missing_items_v2": missing_required,
        "required_state_negated_items_v2": negated_required,
        "state_disallowed_hits_v2": state_disallowed_hits,
        "oracle_only_literal_hits_v2": oracle_only_hits,
        "answer_consistency_failures_v2": consistency_failures,
        "answer_missing_items_v2": missing_answer,
        "forbidden_token_hits": forbidden_hits,
        "protected_token_hits": protected_hits,
        "revoked_token_hits": revoked_hits,
        "stale_token_hits": stale_hits,
        "blocked_path_hits": blocked_hits,
        "state_reason_codes_v2": sorted(set(reasons)),
        "answer_parseable_v2": bool(answer_parseable),
        "answer_parse_reason_v2": answer_parse_reason,
    }


def load_sidecars(path: Path) -> dict[str, dict[str, Any]]:
    return {row["source_task_id"]: row for row in read_jsonl(path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sidecar", required=True, type=Path)
    ap.add_argument("--outputs", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    tasks = load_sidecars(args.sidecar)
    scored = []
    for row in read_jsonl(args.outputs):
        task_id = row.get("task_id")
        if task_id not in tasks:
            raise SystemExit(f"unknown task_id: {task_id}")
        scored.append(score_row(tasks[task_id], row))
    write_jsonl(args.out, scored)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
