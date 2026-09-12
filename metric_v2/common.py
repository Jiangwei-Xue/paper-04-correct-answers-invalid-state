"""Shared format-neutral helpers for metric v2."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

OUTPUT_FIELDS = {
    "OUT", "ALW", "ALLOW", "ALLOWED", "ALLOWED_PATH", "ALLOWED_PATHS",
    "ACTIVE", "ACTIVE_SET", "ACTIVE_TOKENS", "REQUIRED", "REQUIRED_TOKENS",
    "VISIBLE_KEEP", "KEEP", "OUTPUT", "OUTPUT_SET", "FINAL", "FINAL_ACTIVE",
    "FINAL_ACTIVE_SET", "FINAL_TOKENS", "FINAL_ACTIVE_TOKENS", "CARRY_ALL",
}
EXCLUSION_FIELDS = {
    "NO", "NO_CAT", "DENY", "DENIED", "EXCLUDED", "EXCLUDE", "FORBIDDEN",
    "PROTECTED", "REVOKED", "STALE", "BLOCKED", "BOUND", "BOUNDARY", "B",
    "NOTE", "NOTES", "CHECK", "CHECKS", "CK", "BOUNDARY_CHECKS", "STATE_LABELS",
    "STATE_TRANSITIONS",
}
ANNOTATION_FIELDS = {
    "CURRENT_GOAL", "GAP", "NEXT_MISTAKE_TO_AVOID", "G", "N", "SUMMARY",
    "VISIBLE_NOTE", "VISIBLE_BOUNDARY", "VISIBLE_ALLOWED_SCOPE", "LOOP",
}
DIAGNOSTIC_FIELDS = {"TRACE", "EVIDENCE", "SEGMENT", "FAMILY", "DEBUG"}
KNOWN_FIELDS = OUTPUT_FIELDS | EXCLUSION_FIELDS | ANNOTATION_FIELDS | DIAGNOSTIC_FIELDS
TOKEN_RE = re.compile(r"\b(?:REQ|CFG|API|MOD|PATH|FEATURE|FLAG|RULE|PATCH|HOOK|JOB|CHECK)_[0-9]{2}_[A-Z0-9]{6}\b")
PATH_RE = re.compile(r"(?<![A-Za-z0-9_])src/[A-Za-z0-9_./-]+\.(?:py|yaml|json|md)(?![A-Za-z0-9_])")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def parse_json_object(value: Any) -> tuple[dict[str, Any] | None, bool, str]:
    if isinstance(value, dict):
        return value, True, "json_object"
    if value is None:
        return None, False, "missing"
    text = str(value).strip()
    if not text:
        return None, False, "empty"
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj, True, "json_object"
        return None, False, "json_non_object"
    except Exception:
        pass
    matches = list(re.finditer(r"\{.*\}", text, flags=re.S))
    if len(matches) == 1:
        try:
            obj = json.loads(matches[0].group(0))
            if isinstance(obj, dict):
                return obj, True, "embedded_json_object"
        except Exception:
            pass
    return None, False, "malformed_or_raw"


def stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def exact_present(text: str, item: str) -> bool:
    return bool(item) and re.search(rf"(?<![A-Za-z0-9_]){re.escape(item)}(?![A-Za-z0-9_])", text) is not None


def answer_object(final_output: Any) -> tuple[dict[str, Any], str, bool, str]:
    obj, parseable, reason = parse_json_object(final_output)
    if obj is None:
        text = stringify(final_output)
        return {}, text, False, reason
    answer = obj.get("final_answer")
    return (answer if isinstance(answer, dict) else obj), stringify(final_output), parseable, reason


def list_values(answer: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for key in keys:
        value = answer.get(key)
        if isinstance(value, list):
            out.extend(str(item) for item in value)
        elif isinstance(value, str) and value.strip():
            out.extend(x.strip() for x in value.split(",") if x.strip())
    return list(dict.fromkeys(out))


def extract_answer_items(answer: dict[str, Any], raw_text: str) -> tuple[list[str], list[str]]:
    tokens = list_values(answer, ("required_tokens", "tokens", "active_tokens", "final_active_set"))
    paths = list_values(answer, ("allowed_paths", "paths", "files"))
    if not tokens:
        tokens = list(dict.fromkeys(TOKEN_RE.findall(raw_text)))
    if not paths:
        paths = list(dict.fromkeys(PATH_RE.findall(raw_text)))
    return tokens, paths


def operational_answer_text(answer: dict[str, Any], raw_text: str) -> str:
    if not answer:
        return raw_text
    return json.dumps({k: v for k, v in answer.items() if k not in {"state_labels", "state_transitions", "boundary_checks"}}, ensure_ascii=False, sort_keys=True)
