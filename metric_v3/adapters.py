"""Deterministic native-state adapters for V3.

Adapters intentionally receive only native state text and a visible item
universe. They do not import or receive an oracle, answer, executor result, or
any prior score. Polarity comes from field roles and local lexical cues.
"""

from __future__ import annotations

import json
import re
from typing import Any


POSITIVE_FIELDS = {
    "OUT", "ALW", "ALLOW", "ALLOWED", "ALLOWED_PATH", "ALLOWED_PATHS", "ACTIVE",
    "ACTIVE_SET", "ACTIVE_TOKENS", "REQUIRED", "REQUIRED_TOKENS", "VISIBLE_KEEP",
    "KEEP", "OUTPUT", "OUTPUT_SET", "FINAL", "FINAL_ACTIVE", "FINAL_ACTIVE_SET",
    "FINAL_TOKENS", "FINAL_ACTIVE_TOKENS", "CARRY_ALL",
}
NEGATIVE_FIELDS = {
    "NO", "NO_CAT", "DENY", "DENIED", "EXCLUDED", "EXCLUDE", "FORBIDDEN", "PROTECTED",
    "REVOKED", "STALE", "BLOCKED", "BOUND", "BOUNDARY",
}
SEMANTIC_FIELDS = {
    "SUMMARY", "NOTE", "NOTES", "CHECK", "CHECKS", "CK", "BOUNDARY_CHECKS",
    "STATE_LABELS", "STATE_TRANSITIONS", "VISIBLE_NOTE", "VISIBLE_BOUNDARY",
    "VISIBLE_ALLOWED_SCOPE",
}
KNOWN_FIELDS = POSITIVE_FIELDS | NEGATIVE_FIELDS | SEMANTIC_FIELDS | {
    "CURRENT_GOAL", "GAP", "NEXT_MISTAKE_TO_AVOID", "G", "N", "LOOP", "TRACE", "EVIDENCE",
}
ASSIGNMENT_RE = re.compile(r"(?P<key>[A-Za-z][A-Za-z0-9_]*)\s*=\s*", flags=re.I)
NEGATIVE_TERMS = re.compile(
    r"revoked|stale|forbidden|blocked|protected|excluded|exclude|not outputtable|not active|"
    r"inactive|invalid|redacted|deprecated|archive[- ]only|rollback[- ]only|must not|do not output|"
    r"no activation|not valid|remains? (?:outside|forbidden|blocked|revoked|stale)", re.I
)
POSITIVE_TERMS = re.compile(
    r"active|allowed|valid|outputtable|final active|remains active|confirmed active|"
    r"only allowed|currently allowed|retained|preserved|carry", re.I
)


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _exact(text: str, item: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(item)}(?![A-Za-z0-9_])", text) is not None


def _items_in(text: str, visible_items: list[str]) -> list[str]:
    return [item for item in sorted(visible_items, key=len, reverse=True) if _exact(text, item)]


def _direct_claim(text: str, item: str) -> str:
    """Classify local polarity without consulting task status."""
    positions = [m.start() for m in re.finditer(rf"(?<![A-Za-z0-9_]){re.escape(item)}(?![A-Za-z0-9_])", text)]
    if not positions:
        return "absent"
    labels = set()
    low = text.lower()
    for position in positions:
        # A representation may mention several items in one state string.
        # Restrict lexical polarity to the smallest clause containing this
        # occurrence; a negative claim about a neighboring item must not make
        # an otherwise positive claim ambiguous.
        left_candidates = [low.rfind(mark, 0, position) for mark in (";", "\n", "|", ".")]
        left = max(left_candidates, default=-1) + 1
        right_candidates = [index for mark in (";", "\n", "|", ".")
                            if (index := low.find(mark, position + len(item))) >= 0]
        right = min(right_candidates, default=len(low))
        clause = low[left:right]
        has_negative = bool(NEGATIVE_TERMS.search(clause))
        has_positive = bool(POSITIVE_TERMS.search(clause))
        if has_negative and has_positive:
            labels.add("ambiguous")
        elif has_negative:
            labels.add("negative")
        elif has_positive:
            labels.add("positive")
        else:
            labels.add("ambiguous")
    if labels == {"positive"}:
        return "positive"
    if labels == {"negative"}:
        return "negative"
    return "ambiguous"


def _add_claim(state: dict[str, set[str]], item: str, polarity: str) -> None:
    if polarity == "positive":
        state["positive_operational_items"].add(item)
    elif polarity == "negative":
        state["negative_or_excluded_items"].add(item)
    elif polarity == "ambiguous":
        state["ambiguous_items"].add(item)


def _parse_fields(value: Any) -> tuple[dict[str, list[str]], bool, str]:
    if isinstance(value, dict):
        return {str(key).upper(): [_stringify(item)] for key, item in value.items()}, "RAW" not in value, "json_object"
    raw = str(value or "").strip()
    if not raw:
        return {}, False, "missing"
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return {str(key).upper(): [_stringify(item)] for key, item in obj.items()}, "RAW" not in obj, "json_object"
    except Exception:
        pass
    matches = list(ASSIGNMENT_RE.finditer(raw))
    if not matches:
        return {"RAW": [raw]}, False, "raw_fallback"
    fields: dict[str, list[str]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        fields.setdefault(match.group("key").upper(), []).append(raw[match.end():end].strip(" ;\n\t"))
    if "RAW" in fields:
        return fields, False, "raw_field"
    return fields, True, "assignments"


def _claim_field(state: dict[str, set[str]], field: str, value: str, visible_items: list[str]) -> None:
    items = _items_in(value, visible_items)
    if field in POSITIVE_FIELDS:
        for item in items:
            # Inline labels such as TOKEN:BLOCKED override a positive field.
            polarity = _direct_claim(value, item)
            _add_claim(state, item, "negative" if polarity == "negative" else "positive")
    elif field in NEGATIVE_FIELDS:
        for item in items:
            _add_claim(state, item, "negative")
    elif field in SEMANTIC_FIELDS:
        for item in items:
            _add_claim(state, item, _direct_claim(value, item))


def adapt_state(final_state: Any, visible_items: list[str]) -> dict[str, Any]:
    fields, parseable, parse_reason = _parse_fields(final_state)
    state: dict[str, set[str]] = {
        "positive_operational_items": set(),
        "negative_or_excluded_items": set(),
        "ambiguous_items": set(),
        "annotation_items": set(),
    }
    for field, values in fields.items():
        for value in values:
            # Mapping-shaped label fields are still claims supplied by the
            # native representation; labels are interpreted lexically only.
            if field == "STATE_LABELS" and value.lstrip().startswith("{"):
                try:
                    mapping = json.loads(value)
                except Exception:
                    mapping = {}
                if isinstance(mapping, dict):
                    for item, label in mapping.items():
                        if item in visible_items:
                            label_low = str(label).lower()
                            if NEGATIVE_TERMS.search(label_low):
                                polarity = "negative"
                            elif POSITIVE_TERMS.search(label_low):
                                polarity = "positive"
                            else:
                                polarity = "ambiguous"
                            _add_claim(state, item, polarity)
                    continue
            _claim_field(state, field, value, visible_items)
            if field not in POSITIVE_FIELDS and field not in NEGATIVE_FIELDS and field in KNOWN_FIELDS:
                state["annotation_items"].update(_items_in(value, visible_items))
    # Resolve only local representation conflicts; never use oracle status.
    for item in set(state["positive_operational_items"]) & set(state["negative_or_excluded_items"]):
        state["ambiguous_items"].add(item)
    state["positive_operational_items"] -= state["ambiguous_items"]
    state["negative_or_excluded_items"] -= state["ambiguous_items"]
    return {
        "representation_parseable_v3": bool(parseable),
        "parse_reason_v3": parse_reason,
        "positive_operational_items": sorted(state["positive_operational_items"]),
        "negative_or_excluded_items": sorted(state["negative_or_excluded_items"]),
        "ambiguous_items": sorted(state["ambiguous_items"]),
        "annotation_items": sorted(state["annotation_items"]),
        "adapter_oracle_status_access": False,
        "adapter_answer_access": False,
        "adapter_executor_access": False,
    }
