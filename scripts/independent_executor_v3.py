#!/usr/bin/env python3
"""Independent V3 action executor.

This process receives only saved carried-state text and the derived task
contract. It does not read final answers, scorer labels, or scorer modules.
Its parser is deliberately separate from metric_v3.adapters.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


POSITIVE_FIELDS = {"OUT", "ALW", "ALLOW", "ALLOWED", "ALLOWED_PATH", "ALLOWED_PATHS", "ACTIVE", "ACTIVE_SET",
                   "ACTIVE_TOKENS", "REQUIRED", "REQUIRED_TOKENS", "VISIBLE_KEEP", "KEEP", "OUTPUT", "OUTPUT_SET",
                   "FINAL", "FINAL_ACTIVE", "FINAL_ACTIVE_SET", "FINAL_TOKENS", "FINAL_ACTIVE_TOKENS", "CARRY_ALL"}
NEGATIVE_FIELDS = {"NO", "NO_CAT", "DENY", "DENIED", "EXCLUDED", "EXCLUDE", "FORBIDDEN", "PROTECTED", "REVOKED",
                   "STALE", "BLOCKED", "BOUND", "BOUNDARY"}
ASSIGN = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*=\s*")
NEGATIVE_WORDS = re.compile(r"revoked|stale|forbidden|blocked|protected|excluded|inactive|invalid|redacted|deprecated|not active|must not|do not output", re.I)
POSITIVE_WORDS = re.compile(r"active|allowed|valid|outputtable|retained|preserved|carry", re.I)


def exact(text: str, item: str) -> bool:
    return bool(item) and re.search(rf"(?<![A-Za-z0-9_]){re.escape(item)}(?![A-Za-z0-9_])", text) is not None


def fields(value: object) -> tuple[dict[str, list[str]], bool]:
    if isinstance(value, dict):
        return {str(key).upper(): [json.dumps(val, ensure_ascii=False, sort_keys=True)] for key, val in value.items()}, True
    text = str(value or "").strip()
    if not text:
        return {}, False
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return {str(key).upper(): [json.dumps(val, ensure_ascii=False, sort_keys=True)] for key, val in obj.items()}, True
    except Exception:
        pass
    matches = list(ASSIGN.finditer(text))
    if not matches:
        return {}, False
    parsed: dict[str, list[str]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        parsed.setdefault(match.group(1).upper(), []).append(text[match.end():end].strip(" ;\n\t"))
    return parsed, "RAW" not in parsed


def items_in(text: str, universe: list[str]) -> list[str]:
    return [item for item in sorted(universe, key=len, reverse=True) if exact(text, item)]


def semantic_positive(text: str, item: str) -> bool:
    positions = [match.start() for match in re.finditer(rf"(?<![A-Za-z0-9_]){re.escape(item)}(?![A-Za-z0-9_])", text)]
    for position in positions:
        left = max(text.rfind(mark, 0, position) for mark in (";", "\n", "|", ".")) + 1
        ends = [text.find(mark, position + len(item)) for mark in (";", "\n", "|", ".") if text.find(mark, position + len(item)) >= 0]
        clause = text[left:min(ends) if ends else len(text)]
        if POSITIVE_WORDS.search(clause) and not NEGATIVE_WORDS.search(clause):
            return True
    return False


def run_row(row: dict, env: dict) -> dict:
    parsed, parseable = fields(row.get("final_state", ""))
    universe = list(env.get("task_relevant_item_universe", []))
    positive: set[str] = set()
    negative: set[str] = set()
    raw_state = str(row.get("final_state", ""))
    for field, values in parsed.items():
        for value in values:
            found = items_in(value, universe)
            if field in POSITIVE_FIELDS:
                positive.update(found)
            elif field in NEGATIVE_FIELDS:
                negative.update(found)
            elif field in {"SUMMARY", "NOTE", "NOTES", "CHECK", "CHECKS", "STATE_LABELS", "STATE_TRANSITIONS", "VISIBLE_NOTE", "VISIBLE_BOUNDARY"}:
                for item in found:
                    if semantic_positive(value, item):
                        positive.add(item)
                    elif NEGATIVE_WORDS.search(value):
                        negative.add(item)
    conflict = sorted(positive & negative)
    mandatory = list(env.get("mandatory_current_facts", []))
    options = list(env.get("admissible_action_options", []))
    disallowed = set(env.get("disallowed_output_items", []))
    oracle_only = set(env.get("globally_secret_or_oracle_only_items", []))
    missing = sorted(set(mandatory) - positive)
    supported = sorted(set(options) & positive)
    disallowed_hits = sorted(disallowed & positive)
    oracle_hits = sorted(oracle_only & set(items_in(raw_state, universe)))
    success = bool(parseable and not conflict and not missing and supported and not disallowed_hits and not oracle_hits)
    reasons = []
    if not parseable: reasons.append("EXECUTOR_V3_STATE_NOT_PARSEABLE")
    if conflict: reasons.append("EXECUTOR_V3_CONFLICTING_POLARITY")
    if missing: reasons.append("EXECUTOR_V3_REQUIRED_MISSING")
    if not supported: reasons.append("EXECUTOR_V3_NO_ADMISSIBLE_ACTION_OPTION")
    if disallowed_hits: reasons.append("EXECUTOR_V3_DISALLOWED_ACTION")
    if oracle_hits: reasons.append("EXECUTOR_V3_ORACLE_ONLY_EXPOSURE")
    return {"row_id": row.get("row_id", ""), "task_id": row.get("task_id", ""), "method": row.get("method", ""),
            "model": row.get("model", ""), "budget": row.get("budget", ""), "run_id": row.get("run_id", ""),
            "executor_action_success_v3": success, "executor_parseable_v3": bool(parseable),
            "executor_positive_items_v3": sorted(positive), "executor_negative_items_v3": sorted(negative),
            "executor_conflicts_v3": conflict, "executor_required_missing_v3": missing,
            "executor_supported_options_v3": supported, "executor_disallowed_hits_v3": disallowed_hits,
            "executor_oracle_only_hits_v3": oracle_hits, "executor_reason_codes_v3": sorted(set(reasons))}


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, type=Path)
    ap.add_argument("--sidecar", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    env = {row["source_task_id"]: row for row in read_jsonl(args.sidecar)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.out.open("w", encoding="utf-8") as handle:
        for row in read_jsonl(args.inputs):
            task = env.get(row.get("task_id"))
            if task is None:
                raise SystemExit(f"missing V3 task contract: {row.get('task_id')}")
            handle.write(json.dumps(run_row(row, task), ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    print(json.dumps({"rows": count, "out": str(args.out), "network_calls_performed": 0,
                      "final_answer_read": False, "scorer_labels_read": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
