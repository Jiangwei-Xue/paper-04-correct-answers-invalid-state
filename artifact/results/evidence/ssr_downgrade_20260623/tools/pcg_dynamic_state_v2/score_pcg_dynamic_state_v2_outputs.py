#!/usr/bin/env python3
"""Score PCG dynamic-state v2 outputs.

This scorer is deterministic and does not call any model or external service.
It scores both the final answer and the final carried state, because v1.11
showed that a final state can contain the right token while nearby language
negates it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


NEGATION_TERMS = [
    "superseded",
    "obsolete",
    "stale",
    "deprecated",
    "revoked",
    "forbidden",
    "blocked",
    "private",
    "protected",
    "must not be carried",
    "do not use",
    "invalid",
    "archive-only",
    "archive only",
    "rollback-only",
    "rollback only",
]

KEEP_TERMS = [
    "keep",
    "output",
    "active",
    "required",
    "allowed",
    "final",
    "preserve",
    "use",
]

DENY_TERMS = [
    "deny",
    "no",
    "not",
    "revoked",
    "stale",
    "forbidden",
    "protected",
    "blocked",
    "archive-only",
    "rollback-only",
    "must not",
]

OUTPUT_BEARING_STATE_FIELDS = {
    "OUT",
    "ALW",
    "ALLOW",
    "ACTIVE",
    "ACTIVE_SET",
    "REQUIRED",
    "REQUIRED_TOKENS",
    "VISIBLE_KEEP",
    "KEEP",
    "OUTPUT",
    "OUTPUT_SET",
    "FINAL",
    "FINAL_ACTIVE",
    "FINAL_ACTIVE_SET",
    "CARRY_ALL",
}

EXCLUSION_STATE_FIELDS = {
    "NO",
    "NO_CAT",
    "DENY",
    "DENIED",
    "EXCLUDED",
    "EXCLUDE",
    "FORBIDDEN",
    "PROTECTED",
    "REVOKED",
    "STALE",
    "BLOCKED",
    "BOUND",
    "BOUNDARY",
    "B",
    "NOTE",
    "NOTES",
    "CHECK",
    "CHECKS",
    "CK",
    "BOUNDARY_CHECKS",
    "STATE_LABELS",
    "STATE_TRANSITIONS",
}

STRICT_EXCLUSION_STATE_FIELDS = {
    "NO",
    "NO_CAT",
    "DENY",
    "DENIED",
    "EXCLUDED",
    "EXCLUDE",
    "FORBIDDEN",
    "PROTECTED",
    "REVOKED",
    "STALE",
    "BLOCKED",
}

STATE_FIELD_RE = re.compile(
    r"(OUT|ALW|ALLOW|ACTIVE_SET|ACTIVE|REQUIRED_TOKENS|REQUIRED|VISIBLE_KEEP|KEEP|OUTPUT_SET|OUTPUT|FINAL_ACTIVE_SET|FINAL_ACTIVE|FINAL|CARRY_ALL|NO_CAT|NO|DENIED|DENY|EXCLUDED|EXCLUDE|FORBIDDEN|PROTECTED|REVOKED|STALE|BLOCKED|BOUNDARY_CHECKS|BOUNDARY|BOUND|B|NOTES|NOTE|CHECKS|CHECK|CK|STATE_LABELS|STATE_TRANSITIONS|LOOP|G|N)\s*=",
    flags=re.I,
)


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


def parse_json_maybe(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, flags=re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return {"raw_text": text}
    return {"raw_text": text}


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def final_answer_obj(output_obj: Any) -> dict[str, Any]:
    if isinstance(output_obj, dict) and isinstance(output_obj.get("final_answer"), dict):
        return output_obj["final_answer"]
    if isinstance(output_obj, dict):
        return output_obj
    return {}


def extract_tokens_from_answer(answer: dict[str, Any], raw_text: str) -> list[str]:
    tokens: list[str] = []
    for key in ("required_tokens", "tokens", "active_tokens", "final_active_set"):
        value = answer.get(key)
        if isinstance(value, list):
            tokens.extend(str(item) for item in value)
    if not tokens:
        tokens.extend(re.findall(r"\b(?:REQ|CFG|API|MOD|PATH|FEATURE|FLAG|RULE|PATCH|HOOK|JOB|CHECK)_[0-9]{2}_[A-Z0-9]{6}\b", raw_text))
    return unique(tokens)


def extract_paths_from_answer(answer: dict[str, Any], raw_text: str) -> list[str]:
    paths: list[str] = []
    for key in ("allowed_paths", "paths", "files"):
        value = answer.get(key)
        if isinstance(value, list):
            paths.extend(str(item) for item in value)
    paths.extend(re.findall(r"\bsrc/[A-Za-z0-9_./-]+(?:\.py|\.yaml|\.json|\.md)\b", raw_text))
    return unique(paths)


def leakage_text_from_answer(answer: dict[str, Any], raw_text: str) -> str:
    """Text surface used for leakage checks.

    State-label and transition fields are governance/evaluation fields. They may
    name excluded candidates to label them as excluded. Leakage checks therefore
    focus on the output-bearing answer surface: required tokens, paths, actions,
    decisions, and free-form raw text when parsing failed.
    """
    if not answer:
        return raw_text
    filtered = {
        key: value
        for key, value in answer.items()
        if key not in {"state_labels", "state_transitions", "boundary_checks"}
    }
    return json.dumps(filtered, ensure_ascii=False, sort_keys=True)


def window_has(text: str, token: str, terms: list[str], radius: int = 100) -> bool:
    low = text.lower()
    start = 0
    token_low = token.lower()
    while True:
        idx = low.find(token_low, start)
        if idx == -1:
            return False
        window = low[max(0, idx - radius) : idx + len(token) + radius]
        if any(term in window for term in terms):
            return True
        start = idx + len(token)


def token_has_direct_negation(text: str, token: str) -> bool:
    """Return true only when the token itself is directly negated.

    A broad window around a required token is too blunt for v2: notes often say
    "X remains forbidden; active tokens unchanged: A, B". The word forbidden
    should not negate A or B unless the syntax ties the negation to that token.
    """
    if token not in text:
        return False
    token_re = re.escape(token)
    neg = (
        r"superseded|obsolete|stale|deprecated|revoked|forbidden|blocked|private|"
        r"protected|invalid|archive[- ]only|rollback[- ]only|must not be carried|"
        r"do not use|do not output|must not output|not outputtable"
    )
    patterns = [
        rf"{token_re}.{{0,80}}(?:is|are|was|were|remains|remain|marked|listed|treated|labeled|labelled).{{0,60}}(?:{neg})",
        rf"(?:{neg}).{{0,30}}[:=].{{0,100}}{token_re}",
        rf"{token_re}.{{0,40}}(?:must not|do not|should not).{{0,40}}(?:carry|use|output)",
    ]
    return any(re.search(pattern, text, flags=re.I | re.S) for pattern in patterns)


def _flatten_state_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def parse_state_fields(final_state: str) -> dict[str, str]:
    """Parse transferred state into coarse field surfaces.

    Output-bearing fields are scored differently from exclusion-only fields.
    This avoids treating an honest `NO=token` or `state_labels[token]=revoked`
    note as a contradiction unless the same token also appears in a keep/output
    field.
    """
    text = str(final_state or "")
    parsed = parse_json_maybe(text)
    fields: dict[str, list[str]] = {}

    if isinstance(parsed, dict) and "raw_text" not in parsed:
        for key, value in parsed.items():
            fields.setdefault(str(key).upper(), []).append(_flatten_state_value(value))
    else:
        matches = list(STATE_FIELD_RE.finditer(text))
        if matches:
            for idx, match in enumerate(matches):
                key = match.group(1).upper()
                start = match.end()
                end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
                value = text[start:end].strip(" ;\n\t")
                fields.setdefault(key, []).append(value)
        elif text:
            fields["RAW"] = [text]

    return {key: "\n".join(values) for key, values in fields.items()}


def state_surface(fields: dict[str, str], names: set[str]) -> str:
    return "\n".join(value for key, value in fields.items() if key.upper() in names)


def state_token_in_fields(fields: dict[str, str], token: str, names: set[str]) -> bool:
    return any(token in value for key, value in fields.items() if key.upper() in names)


def state_conflict(final_state: str, required: list[str], excluded: list[str]) -> tuple[bool, bool, bool, bool, bool, bool, bool]:
    fields = parse_state_fields(final_state)
    output_text = state_surface(fields, OUTPUT_BEARING_STATE_FIELDS)
    exclusion_text = state_surface(fields, EXCLUSION_STATE_FIELDS)
    strict_exclusion_text = state_surface(fields, STRICT_EXCLUSION_STATE_FIELDS)
    all_text = "\n".join(fields.values()) if fields else str(final_state or "")
    raw_fallback = "RAW" in fields

    state_required_token_present = any(token in all_text for token in required)
    state_required_token_negated = any(
        state_token_in_fields(fields, token, STRICT_EXCLUSION_STATE_FIELDS)
        or token_has_direct_negation(all_text, token)
        for token in required
    )
    state_forbidden_token_present = any(token in all_text for token in excluded)
    state_forbidden_token_negated = any(
        state_token_in_fields(fields, token, EXCLUSION_STATE_FIELDS)
        or (token in all_text and window_has(all_text, token, DENY_TERMS))
        for token in excluded
    )

    output_bearing_state_conflict = any(token in output_text for token in excluded)
    exclusion_field_conflict = any(token in strict_exclusion_text for token in required)
    dual_zone_conflict = any(token in output_text and token in strict_exclusion_text for token in set(required + excluded))
    required_negation_conflict = any(token_has_direct_negation(all_text, token) for token in required)

    legacy_raw_conflict = False
    if raw_fallback:
        legacy_raw_conflict = any(
            token in all_text and window_has(all_text, token, KEEP_TERMS) and window_has(all_text, token, DENY_TERMS)
            for token in set(required + excluded)
        )

    state_internal_conflict = bool(
        output_bearing_state_conflict
        or exclusion_field_conflict
        or dual_zone_conflict
        or required_negation_conflict
        or legacy_raw_conflict
    )

    return (
        state_required_token_present,
        state_required_token_negated,
        state_forbidden_token_present,
        state_forbidden_token_negated,
        output_bearing_state_conflict,
        exclusion_field_conflict,
        state_internal_conflict,
    )


def state_label_accuracy(answer: dict[str, Any], expected: dict[str, str]) -> float:
    observed = answer.get("state_labels")
    if not isinstance(observed, dict) or not expected:
        return 0.0
    correct = 0
    for token, label in expected.items():
        if str(observed.get(token, "")).lower().replace("-", "_") == label:
            correct += 1
    return correct / len(expected)


def state_transition_accuracy(answer: dict[str, Any], expected: list[dict[str, Any]]) -> float:
    observed = answer.get("state_transitions")
    if not isinstance(observed, list) or not expected:
        return 0.0
    observed_keys = {
        (str(item.get("token")), str(item.get("from")), str(item.get("to")), int(item.get("step", -1)))
        for item in observed
        if isinstance(item, dict)
    }
    correct = 0
    for item in expected:
        key = (str(item.get("token")), str(item.get("from")), str(item.get("to")), int(item.get("step", -1)))
        if key in observed_keys:
            correct += 1
    return correct / len(expected)


def score_task(task: dict[str, Any], output_row: dict[str, Any]) -> dict[str, Any]:
    oracle = task["oracle"]
    final_output = output_row.get("final_output", output_row.get("output", ""))
    output_obj = parse_json_maybe(final_output)
    raw_text = final_output if isinstance(final_output, str) else json.dumps(final_output, ensure_ascii=False, sort_keys=True)
    answer = final_answer_obj(output_obj)
    output_tokens = extract_tokens_from_answer(answer, raw_text)
    output_paths = extract_paths_from_answer(answer, raw_text)
    leakage_text = leakage_text_from_answer(answer, raw_text)
    final_state = str(output_row.get("final_state", ""))

    required = list(oracle["required_exact_tokens"])
    forbidden = list(oracle["forbidden_exact_tokens"])
    protected = list(oracle["protected_exact_tokens"])
    revoked = list(oracle["revoked_exact_tokens"])
    stale = list(oracle["stale_exact_tokens"])
    blocked_paths = list(oracle["blocked_paths"])
    excluded = unique(forbidden + protected + revoked + stale + list(oracle["final_excluded_set"]))

    present_required = [token for token in required if token in output_tokens or token in raw_text]
    missing_required = [token for token in required if token not in present_required]
    required_token_recall = len(present_required) / len(required) if required else 1.0

    forbidden_hits = [token for token in forbidden if token in output_tokens or token in leakage_text]
    protected_hits = [token for token in protected if token in output_tokens or token in leakage_text]
    revoked_hits = [token for token in revoked if token in output_tokens or token in leakage_text]
    stale_hits = [token for token in stale if token in output_tokens or token in leakage_text]
    blocked_path_hits = [path for path in blocked_paths if path in leakage_text or path in output_paths]
    boundary_violation = bool(blocked_path_hits)

    (
        state_required_token_present,
        state_required_token_negated,
        state_forbidden_token_present,
        state_forbidden_token_negated,
        output_bearing_state_conflict,
        exclusion_field_conflict,
        state_internal_conflict,
    ) = state_conflict(final_state, required, excluded)

    label_acc = state_label_accuracy(answer, oracle.get("expected_state_labels", {}))
    transition_acc = state_transition_accuracy(answer, oracle.get("expected_state_transitions", []))
    no_leakage = not (forbidden_hits or protected_hits or revoked_hits or stale_hits or blocked_path_hits)
    final_exact_success = required_token_recall == 1.0 and no_leakage
    answer_success = final_exact_success and not boundary_violation
    state_governance_success = not state_internal_conflict
    reliable_composite_success = answer_success and state_governance_success
    reliable_success = reliable_composite_success

    return {
        "task_id": task["task_id"],
        "method": output_row.get("method", ""),
        "model": output_row.get("model", ""),
        "budget": output_row.get("budget", output_row.get("state_budget", "")),
        "run_id": output_row.get("run_id", output_row.get("run_index", "")),
        "required_token_recall": round(required_token_recall, 6),
        "required_token_missing_count": len(missing_required),
        "missing_required_tokens": missing_required,
        "forbidden_token_leakage": bool(forbidden_hits),
        "forbidden_token_hits": forbidden_hits,
        "protected_token_leakage": bool(protected_hits),
        "protected_token_hits": protected_hits,
        "revoked_token_leakage": bool(revoked_hits),
        "revoked_token_hits": revoked_hits,
        "stale_token_leakage": bool(stale_hits),
        "stale_token_hits": stale_hits,
        "blocked_path_leakage": bool(blocked_path_hits),
        "blocked_path_hits": blocked_path_hits,
        "boundary_violation": boundary_violation,
        "state_label_accuracy": round(label_acc, 6),
        "state_transition_accuracy": round(transition_acc, 6),
        "final_exact_success": final_exact_success,
        "reliable_success": reliable_success,
        "state_required_token_present": state_required_token_present,
        "state_required_token_negated": state_required_token_negated,
        "state_internal_conflict": state_internal_conflict,
        "output_bearing_state_conflict": output_bearing_state_conflict,
        "exclusion_field_conflict": exclusion_field_conflict,
        "answer_success": answer_success,
        "state_governance_success": state_governance_success,
        "reliable_composite_success": reliable_composite_success,
        "state_forbidden_token_present": state_forbidden_token_present,
        "state_forbidden_token_negated": state_forbidden_token_negated,
        "mechanical_carry_failure_mode_detected": bool(forbidden_hits or protected_hits or revoked_hits or stale_hits or blocked_path_hits or state_internal_conflict),
    }


def perfect_output(task: dict[str, Any]) -> dict[str, Any]:
    oracle = task["oracle"]
    return {
        "final_answer": {
            "required_tokens": oracle["required_exact_tokens"],
            "allowed_paths": oracle["allowed_paths"],
            "state_labels": oracle["expected_state_labels"],
            "state_transitions": oracle["expected_state_transitions"],
            "boundary_checks": {
                "no_forbidden_tokens": True,
                "no_protected_tokens": True,
                "no_revoked_or_stale_tokens": True,
                "no_blocked_paths": True,
            },
        }
    }


def dummy_rows_for_task(task: dict[str, Any]) -> list[dict[str, Any]]:
    oracle = task["oracle"]
    required = list(oracle["required_exact_tokens"])
    candidates = list(oracle["expected_state_labels"].keys())
    excluded = [
        token
        for token, label in oracle["expected_state_labels"].items()
        if label != "active" and label != "allowed"
    ]
    revoked_token = next((token for token, label in oracle["expected_state_labels"].items() if label == "revoked"), None)
    blocked_path = oracle["blocked_paths"][0] if oracle["blocked_paths"] else None
    conflict_token = required[0] if required else ""

    rows = [
        {
            "dummy_case": "perfect_output",
            "task_id": task["task_id"],
            "final_output": perfect_output(task),
            "final_state": "ACTIVE=" + ",".join(required) + "; OUTPUT_SET_COMPLETE=true",
            "expected_reliable_success": True,
        },
        {
            "dummy_case": "carry_all_candidates",
            "task_id": task["task_id"],
            "final_output": {"final_answer": {"required_tokens": candidates, "allowed_paths": oracle["allowed_paths"] + oracle["blocked_paths"]}},
            "final_state": "CARRY_ALL=" + ",".join(candidates),
            "expected_reliable_success": False,
        },
        {
            "dummy_case": "missing_active",
            "task_id": task["task_id"],
            "final_output": {"final_answer": {"required_tokens": required[1:], "allowed_paths": oracle["allowed_paths"]}},
            "final_state": "ACTIVE=" + ",".join(required[1:]),
            "expected_reliable_success": False,
        },
        {
            "dummy_case": "revoked_reactivated",
            "task_id": task["task_id"],
            "final_output": {"final_answer": {"required_tokens": required + ([revoked_token] if revoked_token else excluded[:1])}},
            "final_state": "ACTIVE=" + ",".join(required) + "; LOG_REAPPEARED=" + str(revoked_token or ""),
            "expected_reliable_success": False,
        },
        {
            "dummy_case": "blocked_path_attraction",
            "task_id": task["task_id"],
            "final_output": {
                "final_answer": {
                    "required_tokens": required,
                    "allowed_paths": oracle["allowed_paths"] + ([blocked_path] if blocked_path else []),
                }
            },
            "final_state": "ACTIVE=" + ",".join(required),
            "expected_reliable_success": False,
        },
        {
            "dummy_case": "state_conflict",
            "task_id": task["task_id"],
            "final_output": perfect_output(task),
            "final_state": f"ACTIVE={','.join(required)}; NOTE={conflict_token} is revoked and must not be carried",
            "expected_reliable_success": False,
        },
    ]
    return rows


def run_dummy_tests(tasks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    carry_all_fail_count = 0
    for task in tasks:
        for row in dummy_rows_for_task(task):
            score = score_task(task, row)
            score["dummy_case"] = row["dummy_case"]
            score["expected_reliable_success"] = row["expected_reliable_success"]
            score["dummy_expectation_passed"] = bool(score["reliable_success"]) == bool(row["expected_reliable_success"])
            scored.append(score)
            if row["dummy_case"] == "carry_all_candidates" and not score["reliable_success"]:
                carry_all_fail_count += 1
            if not score["dummy_expectation_passed"]:
                failures.append(score)
    summary = {
        "tasks": len(tasks),
        "dummy_rows": len(scored),
        "expectation_failures": len(failures),
        "carry_all_candidates_fail_count": carry_all_fail_count,
        "carry_all_candidates_fail_rate": carry_all_fail_count / len(tasks) if tasks else 0.0,
        "passed": not failures and (carry_all_fail_count / len(tasks) if tasks else 0.0) >= 0.70,
    }
    return scored, summary


def load_tasks(path: Path) -> dict[str, dict[str, Any]]:
    return {row["task_id"]: row for row in read_jsonl(path)}


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
        print("--outputs is required unless --dummy-tests is used", file=sys.stderr)
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
