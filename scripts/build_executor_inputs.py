#!/usr/bin/env python3
"""Strip saved rows to the state/environment-independent-executor surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from metric_v2.common import write_jsonl


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    out = []
    for line in args.source.open(encoding="utf-8"):
        if not line.strip(): continue
        row = json.loads(line)
        # Deliberately do not copy final_output or any scorer field.
        out.append({k: row.get(k, "") for k in ("row_id", "task_id", "model", "method", "budget", "run_id", "final_state", "source_file", "source_line_number", "source_file_sha256", "raw_response_sha256")})
    write_jsonl(args.out, out)
    print(json.dumps({"rows": len(out), "source_fields_used": ["row_id", "task_id", "model", "method", "budget", "run_id", "final_state", "source_file", "source_line_number", "source_file_sha256", "raw_response_sha256"], "final_answer_field_included": False, "scorer_labels_included": False, "network_calls_performed": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
