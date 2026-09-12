#!/usr/bin/env python3
"""Attach unchanged v1 labels to v2 score rows for side-by-side audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from metric_v2.common import write_jsonl


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v2", required=True, type=Path)
    ap.add_argument("--legacy", required=True, action="append", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    legacy: dict[str, dict] = {}
    sources: dict[str, str] = {}
    for path in args.legacy:
        digest = sha256(path)
        for line in path.open(encoding="utf-8"):
            if line.strip():
                row = json.loads(line)
                key = row.get("row_id") or row.get("baseline_row_id")
                if not key:
                    raise SystemExit(f"legacy score has no row identity: {path}")
                legacy[key] = row
                sources[key] = digest
    out = []
    missing = []
    for line in args.v2.open(encoding="utf-8"):
        if not line.strip(): continue
        row = json.loads(line)
        old = legacy.get(row["row_id"])
        if old is None:
            missing.append(row["row_id"])
            continue
        row["state_governance_success_v1"] = bool(old.get("state_governance_success", old.get("state_governance_success_legacy_no_conflict_only", False)))
        row["reliable_composite_success_v1"] = bool(old.get("reliable_composite_success", old.get("reliable_success", False)))
        row["legacy_v1_answer_success"] = bool(old.get("answer_success", False))
        row["legacy_v1_state_governance_success"] = bool(old.get("state_governance_success", False))
        row["legacy_v1_reliable_composite_success"] = bool(old.get("reliable_composite_success", old.get("reliable_success", False)))
        row["legacy_v1_score_source_sha256"] = sources[row["row_id"]]
        row["legacy_v1_score_schema_version"] = old.get("schema_version", "")
        out.append(row)
    if missing:
        raise SystemExit(f"missing legacy labels for {len(missing)} rows; first={missing[:3]}")
    write_jsonl(args.out, out)
    print(json.dumps({"rows": len(out), "legacy_sources": len(args.legacy), "network_calls_performed": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
