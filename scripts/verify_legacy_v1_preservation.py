#!/usr/bin/env python3
"""Verify that copied v1 labels match their frozen score rows exactly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def rows(path):
    return {x.get("row_id") or x.get("baseline_row_id"): x for x in (json.loads(line) for line in path.open(encoding="utf-8") if line.strip())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v2", required=True, type=Path)
    ap.add_argument("--legacy", required=True, action="append", type=Path)
    args = ap.parse_args()
    old = {}
    for path in args.legacy: old.update(rows(path))
    checked, failures = 0, []
    for row in (json.loads(line) for line in args.v2.open(encoding="utf-8") if line.strip()):
        key = row["row_id"]
        if key not in old: failures.append({"row_id": key, "reason": "missing_source"}); continue
        ref = old[key]; checked += 1
        expected = (bool(ref.get("state_governance_success", ref.get("state_governance_success_legacy_no_conflict_only", False))), bool(ref.get("reliable_composite_success", ref.get("reliable_success", False))))
        actual = (bool(row.get("state_governance_success_v1")), bool(row.get("reliable_composite_success_v1")))
        if actual != expected: failures.append({"row_id": key, "expected": expected, "actual": actual})
    report = {"schema": "metric_v2_legacy_v1_preservation.v1", "network_calls_performed": 0, "rows_checked": checked, "failures": failures, "passed": not failures}
    out = Path("reports/metric_v2/legacy_v1_preservation.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows_checked": checked, "failure_count": len(failures), "passed": not failures}, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
