#!/usr/bin/env python3
"""Attach the frozen final-answer-v2 label to saved V3 replay inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metric_v2.common import sha256_file, write_jsonl  # noqa: E402


def read_labels(path: Path) -> dict[str, bool]:
    labels: dict[str, bool] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                labels[str(row["row_id"])] = bool(row.get("answer_success_v2", False))
    return labels


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--score-v2", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    labels = read_labels(args.score_v2)
    source_hash = sha256_file(args.score_v2)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    missing = None
    with args.raw.open("r", encoding="utf-8") as source, args.out.open("w", encoding="utf-8") as target:
        for line in source:
            if not line.strip():
                continue
            row = json.loads(line)
            row_id = str(row["row_id"])
            if row_id not in labels:
                missing = row_id
                break
            row["final_answer_success_v2"] = labels[row_id]
            row["final_answer_label_source"] = str(args.score_v2)
            row["final_answer_label_source_sha256"] = source_hash
            target.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    if missing is not None:
        args.out.unlink(missing_ok=True)
        raise SystemExit(f"missing V2 final-answer label for row: {missing}")
    print(json.dumps({"out": str(args.out), "rows": count, "source_raw": str(args.raw),
                      "source_v2_score": str(args.score_v2), "network_calls_performed": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
