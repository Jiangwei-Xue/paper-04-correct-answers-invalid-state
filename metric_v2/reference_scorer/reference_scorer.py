#!/usr/bin/env python3
"""Independent reference scorer for differential validation.

This file intentionally contains its own parser, matching logic, and metric
derivation. It does not import the production scorer or its parser.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


OUT_FIELDS = {
    "OUT", "ALW", "ALLOW", "ALLOWED", "ALLOWED_PATH", "ALLOWED_PATHS", "ACTIVE",
    "ACTIVE_SET", "ACTIVE_TOKENS", "REQUIRED", "REQUIRED_TOKENS", "VISIBLE_KEEP",
    "KEEP", "OUTPUT", "OUTPUT_SET", "FINAL", "FINAL_ACTIVE", "FINAL_ACTIVE_SET",
    "FINAL_TOKENS", "FINAL_ACTIVE_TOKENS", "CARRY_ALL",
}
EX_FIELDS = {
    "NO", "NO_CAT", "DENY", "DENIED", "EXCLUDED", "EXCLUDE", "FORBIDDEN", "PROTECTED",
    "REVOKED", "STALE", "BLOCKED", "BOUND", "BOUNDARY", "B", "NOTE", "NOTES", "CHECK",
    "CHECKS", "CK", "BOUNDARY_CHECKS", "STATE_LABELS", "STATE_TRANSITIONS",
}
ASSIGNMENT = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*=\s*", flags=re.I)
TOKEN = re.compile(r"(?<![A-Za-z0-9_])(?:REQ|CFG|API|MOD|PATH|FEATURE|FLAG|RULE|PATCH|HOOK|JOB|CHECK)_[0-9]{2}_[A-Z0-9]{6}(?![A-Za-z0-9_])")
PATH = re.compile(r"(?<![A-Za-z0-9_])src/[A-Za-z0-9_./-]+\.(?:py|yaml|json|md)(?![A-Za-z0-9_])")


def textify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def exact(text: str, value: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(value)}(?![A-Za-z0-9_])", text) is not None


def parse_state(value: Any) -> tuple[dict[str, list[str]], bool, str]:
    if isinstance(value, dict):
        fields = {str(k).upper(): [textify(v)] for k, v in value.items()}
        return fields, "RAW" not in fields, "json_object"
    s = str(value or "").strip()
    if not s:
        return {}, False, "missing"
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            fields = {str(k).upper(): [textify(v)] for k, v in obj.items()}
            return fields, "RAW" not in fields, "json_object"
    except Exception:
        pass
    ms = list(ASSIGNMENT.finditer(s))
    if not ms:
        return {"RAW": [s]}, False, "raw_fallback"
    fields: dict[str, list[str]] = {}
    for i, m in enumerate(ms):
        stop = ms[i + 1].start() if i + 1 < len(ms) else len(s)
        fields.setdefault(m.group(1).upper(), []).append(s[m.end():stop].strip(" ;\n\t"))
    return fields, "RAW" not in fields, "assignments"


def surface(fields: dict[str, list[str]], role: set[str]) -> str:
    return "\n".join(v for k, vs in fields.items() if k in role for v in vs)


def object_answer(value: Any) -> tuple[dict[str, Any], str, bool]:
    if isinstance(value, dict):
        obj = value; good = True; raw = textify(value)
    else:
        raw = textify(value)
        try:
            obj = json.loads(raw); good = isinstance(obj, dict)
        except Exception:
            m = re.search(r"\{.*\}", raw, flags=re.S)
            try:
                obj = json.loads(m.group(0)) if m else {}
                good = isinstance(obj, dict)
            except Exception:
                obj = {}; good = False
    ans = obj.get("final_answer") if isinstance(obj.get("final_answer"), dict) else obj
    return ans if isinstance(ans, dict) else {}, raw, good


def values(ans: dict[str, Any], names: tuple[str, ...]) -> list[str]:
    result: list[str] = []
    for name in names:
        val = ans.get(name)
        if isinstance(val, list): result.extend(str(x) for x in val)
        elif isinstance(val, str): result.extend(x.strip() for x in val.split(",") if x.strip())
    return list(dict.fromkeys(result))


def negated(text: str, item: str) -> bool:
    if not exact(text, item): return False
    x = re.escape(item)
    n = r"superseded|obsolete|stale|deprecated|revoked|forbidden|blocked|protected|invalid|archive[- ]only|rollback[- ]only|must not|do not use|do not output|not outputtable"
    return bool(
        re.search(rf"{x}.{{0,80}}(?:is|are|was|were|remains|remain|marked|listed|treated|labeled|labelled).{{0,60}}(?:{n})", text, re.I | re.S)
        or re.search(rf"(?:{n}).{{0,40}}[:=].{{0,100}}{x}", text, re.I | re.S)
        or re.search(rf"{x}.{{0,40}}(?:must not|do not|should not).{{0,40}}(?:carry|use|output)", text, re.I | re.S)
    )


def score(side: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    ans, raw, ans_good = object_answer(row.get("final_output", row.get("output", "")))
    tokens = values(ans, ("required_tokens", "tokens", "active_tokens", "final_active_set")) or list(dict.fromkeys(TOKEN.findall(raw)))
    paths = values(ans, ("allowed_paths", "paths", "files")) or list(dict.fromkeys(PATH.findall(raw)))
    op = json.dumps({k: v for k, v in ans.items() if k not in {"state_labels", "state_transitions", "boundary_checks"}}, ensure_ascii=False, sort_keys=True) if ans else raw
    fields, parsed, parse_reason = parse_state(row.get("final_state", ""))
    positive = surface(fields, OUT_FIELDS)
    negative = surface(fields, EX_FIELDS)
    whole = "\n".join(x for values_ in fields.values() for x in values_)
    required = list(side.get("required_state_items", []))
    disallowed = list(side.get("disallowed_output_items", []))
    oracle_only = list(side.get("globally_secret_or_oracle_only_items", []))
    missing = [x for x in required if not exact(positive, x)]
    neg_req = [x for x in required if exact(negative, x) or negated(whole, x)]
    state_bad = [x for x in disallowed if exact(positive, x)]
    secret_bad = [x for x in oracle_only if exact(whole, x)]
    complete = parsed and not missing and not neg_req
    present = parsed and bool(positive.strip())
    safe = not state_bad and not secret_bad
    consistency = []
    for x in tokens + paths:
        if x in disallowed: consistency.append("ANSWER_DISALLOWED:" + x)
        elif not exact(positive, x): consistency.append("ANSWER_UNSUPPORTED:" + x)
        elif exact(negative, x) or negated(whole, x): consistency.append("ANSWER_NEGATED:" + x)
    consistent = parsed and present and not consistency
    req_answer = list(side.get("required_answer_items", required))
    miss_answer = [x for x in req_answer if not exact(op, x)]
    labels = side.get("final_item_statuses", {})
    forbidden = list(side.get("forbidden_exact_tokens", [])) or [x for x, v in labels.items() if v == "forbidden"]
    protected = list(side.get("protected_exact_tokens", [])) or [x for x, v in labels.items() if v == "protected"]
    revoked = list(side.get("revoked_exact_tokens", [])) or [x for x, v in labels.items() if v == "revoked"]
    stale = list(side.get("stale_exact_tokens", [])) or [x for x, v in labels.items() if v == "stale"]
    blocked = list(side.get("blocked_paths", []))
    leaks = [x for x in forbidden + protected + revoked + stale + blocked if exact(op, x)]
    answer_ok = not miss_answer and not leaks
    intrinsic = parsed and present and safe and complete
    carried = intrinsic and consistent
    joint = answer_ok and carried
    reasons = []
    if not parsed: reasons.append("PARSE_" + parse_reason.upper())
    if not present: reasons.append("NO_OUTPUT_BEARING_STATE")
    if missing: reasons.append("MISSING_REQUIRED_STATE")
    if neg_req: reasons.append("REQUIRED_STATE_NEGATED")
    if state_bad: reasons.append("DISALLOWED_STATE_OUTPUT")
    if secret_bad: reasons.append("ORACLE_ONLY_LITERAL_EXPOSURE")
    reasons.extend(consistency)
    if miss_answer: reasons.append("ANSWER_REQUIRED_MISSING")
    if leaks: reasons.append("ANSWER_BOUNDARY_LEAK")
    legacy_conflict = bool(neg_req or state_bad)
    return {
        "row_id": row.get("row_id") or row.get("baseline_row_id") or row.get("task_id", ""),
        "task_id": row.get("task_id", ""),
        "method": row.get("method", ""), "model": row.get("model", ""),
        "budget": row.get("budget", row.get("state_budget", "")),
        "run_id": row.get("run_id", row.get("run_index", "")),
        "state_parseable_v2": bool(parsed), "output_bearing_present_v2": bool(present),
        "exclusion_safety_v2": bool(safe), "required_state_completeness_v2": bool(complete),
        "answer_state_consistency_v2": bool(consistent), "intrinsic_state_validity_v2": bool(intrinsic),
        "carried_state_validity_v2": bool(carried), "joint_answer_state_success_v2": bool(joint),
        "answer_success_v2": bool(answer_ok), "answer_success": bool(answer_ok),
        "state_governance_success_v1": not legacy_conflict,
        "reliable_composite_success_v1": bool(answer_ok and not legacy_conflict),
        "required_state_missing_items_v2": missing, "required_state_negated_items_v2": neg_req,
        "state_disallowed_hits_v2": state_bad, "oracle_only_literal_hits_v2": secret_bad,
        "answer_consistency_failures_v2": consistency, "answer_missing_items_v2": miss_answer,
        "forbidden_token_hits": [x for x in forbidden if exact(op, x)],
        "protected_token_hits": [x for x in protected if exact(op, x)],
        "revoked_token_hits": [x for x in revoked if exact(op, x)],
        "stale_token_hits": [x for x in stale if exact(op, x)],
        "blocked_path_hits": [x for x in blocked if exact(op, x)],
        "state_reason_codes_v2": sorted(set(reasons)),
        "answer_parseable_v2": bool(ans_good),
        "answer_parse_reason_v2": "json_object" if ans_good else "raw_or_malformed",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sidecar", required=True, type=Path)
    ap.add_argument("--outputs", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    sides = {x["source_task_id"]: x for x in (json.loads(line) for line in args.sidecar.open(encoding="utf-8") if line.strip())}
    rows = [score(sides[row["task_id"]], row) for row in (json.loads(line) for line in args.outputs.open(encoding="utf-8") if line.strip())]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows: handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
