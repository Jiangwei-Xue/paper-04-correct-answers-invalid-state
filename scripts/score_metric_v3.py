#!/usr/bin/env python3
"""Offline V3 replay over saved normalized rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metric_v3.evaluator import score_row_v3  # noqa: E402


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, type=Path)
    ap.add_argument("--sidecar", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    rows = read_jsonl(args.inputs)
    sidecars = {str(row["source_task_id"]): row for row in read_jsonl(args.sidecar)}
    scored = []
    missing = []
    for row in rows:
        task = sidecars.get(str(row.get("task_id", "")))
        if task is None:
            missing.append(row.get("task_id", ""))
            continue
        scored.append(score_row_v3(task, row))
    if missing:
        raise SystemExit(f"missing V3 sidecars for {len(missing)} rows; first={missing[0]}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for row in scored:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "rows": len(scored), "network_calls_performed": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
