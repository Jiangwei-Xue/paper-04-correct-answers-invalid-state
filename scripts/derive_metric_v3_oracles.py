#!/usr/bin/env python3
"""Derive V3 task contracts from the frozen V2 oracle sidecar, offline."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def derive(row: dict, source_hash: str) -> dict:
    active = [item for item, label in row.get("final_item_statuses", {}).items()
              if str(label).lower() == "active"]
    options = list(row.get("allowed_answer_paths", row.get("optional_allowed_items", [])))
    universe = list(dict.fromkeys(row.get("task_relevant_item_universe", []) + active + options))
    return {
        "sidecar_schema": "carried_state_validity_v3.oracle_sidecar.v1",
        "derivation_version": "metric_v3_oracle_derivation_20260813",
        "source_sidecar_sha256": source_hash,
        "source_task_id": row["source_task_id"],
        "family": row.get("family", ""),
        "task_relevant_item_universe": universe,
        "mandatory_current_facts": active,
        "admissible_action_options": options,
        "action_option_requirements": {option: active for option in options},
        "disallowed_output_items": list(row.get("disallowed_output_items", [])),
        "globally_secret_or_oracle_only_items": list(row.get("globally_secret_or_oracle_only_items", [])),
        # These labels are retained as audit metadata for the contract; the
        # adapter never receives them and never consults them.
        "final_item_statuses": dict(row.get("final_item_statuses", {})),
        "expected_state_transitions": list(row.get("expected_state_transitions", [])),
        "required_answer_items": list(row.get("required_answer_items", [])),
        "allowed_answer_paths": options,
        "blocked_paths": list(row.get("blocked_paths", [])),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--manifest", required=True, type=Path)
    args = ap.parse_args()
    source_hash = sha256_file(args.source)
    rows = read_jsonl(args.source)
    sidecars = [derive(row, source_hash) for row in rows]
    write_jsonl(args.out, sidecars)
    manifest = {
        "schema": "carried_state_validity_v3.oracle_sidecar_manifest.v1",
        "source_sidecar": str(args.source),
        "source_sidecar_sha256": source_hash,
        "sidecar": str(args.out),
        "sidecar_sha256": sha256_file(args.out),
        "task_count": len(sidecars),
        "network_calls_performed": 0,
        "derived_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
