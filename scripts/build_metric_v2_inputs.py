#!/usr/bin/env python3
"""Create versioned, read-only-derived scorer inputs from saved output rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metric_v2.common import write_jsonl  # noqa: E402


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize(row: dict, source: Path, line_number: int, source_sha: str) -> dict:
    raw = row.get("raw_response") if isinstance(row.get("raw_response"), dict) else row
    global_id = str(row.get("global_artifact_id", row.get("source_global_artifact_id", "")))
    bits = global_id.split("::")
    row_id = row.get("row_id") or row.get("baseline_row_id") or global_id
    task_id = row.get("task_id") or (bits[1] if len(bits) > 1 else str(row_id).split("::")[0])
    model = row.get("model") or row.get("model_condition_id") or (bits[2] if len(bits) > 2 else "")
    method = row.get("method") or row.get("source_method") or (bits[3] if len(bits) > 3 else "")
    budget = row.get("budget") or row.get("source_budget") or (bits[4] if len(bits) > 4 else "")
    run_id = row.get("run_id") or row.get("source_run_id") or (bits[5] if len(bits) > 5 else "")
    return {
        "row_id": str(row_id),
        "task_id": str(task_id),
        "model": str(model),
        "method": str(method),
        "budget": str(budget),
        "run_id": str(run_id),
        "final_output": raw.get("final_output", row.get("final_output", "")),
        "final_state": raw.get("final_state", row.get("final_state", "")),
        "source_file": str(source),
        "source_line_number": line_number,
        "source_file_sha256": source_sha,
        "raw_response_sha256": row.get("raw_response_sha256", row.get("raw_response_sha256", "")),
        "finish_reason": row.get("finish_reason", ""),
        "usage": row.get("usage", {}),
        "provider_metadata": row.get("provider_metadata", {}),
        "source_schema_version": row.get("schema_version", ""),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--source", required=True, action="append", type=Path)
    args = ap.parse_args()
    rows: list[dict] = []
    seen: set[str] = set()
    for source in args.source:
        digest = file_hash(source)
        with source.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                norm = normalize(row, source, line_number, digest)
                if norm["row_id"] in seen:
                    raise SystemExit(f"duplicate row_id: {norm['row_id']}")
                seen.add(norm["row_id"])
                rows.append(norm)
    write_jsonl(args.out, rows)
    print(json.dumps({"out": str(args.out), "rows": len(rows), "source_count": len(args.source), "network_calls_performed": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
