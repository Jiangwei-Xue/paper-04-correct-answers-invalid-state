#!/usr/bin/env python3
"""Derive metric-v2 task sidecars from the frozen oracle, offline."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metric_v2.common import read_jsonl, sha256_file, write_jsonl  # noqa: E402


def derive(row: dict, source_hash: str) -> dict:
    oracle = row["oracle"]
    labels = oracle.get("expected_state_labels", {})
    universe = list(dict.fromkeys(
        list(labels.keys()) + list(oracle.get("required_exact_tokens", []))
        + list(oracle.get("allowed_paths", [])) + list(oracle.get("blocked_paths", []))
    ))
    disallowed = list(dict.fromkeys(
        list(oracle.get("final_excluded_set", [])) + list(oracle.get("blocked_paths", []))
    ))
    return {
        "sidecar_schema": "carried_state_validity_v2.oracle_sidecar.v1",
        "derivation_version": "metric_v2_oracle_derivation_20260813",
        "source_oracle_sha256": source_hash,
        "source_task_id": row["task_id"],
        "family": row.get("family", ""),
        "task_relevant_item_universe": universe,
        "required_state_items": list(oracle.get("required_exact_tokens", [])),
        "optional_allowed_items": list(oracle.get("allowed_paths", [])),
        "disallowed_output_items": disallowed,
        "globally_secret_or_oracle_only_items": list(oracle.get("oracle_only_literals", [])),
        "final_item_statuses": dict(labels),
        "required_answer_items": list(oracle.get("required_exact_tokens", [])),
        "allowed_answer_paths": list(oracle.get("allowed_paths", [])),
        "blocked_paths": list(oracle.get("blocked_paths", [])),
        "forbidden_exact_tokens": list(oracle.get("forbidden_exact_tokens", [])),
        "protected_exact_tokens": list(oracle.get("protected_exact_tokens", [])),
        "revoked_exact_tokens": list(oracle.get("revoked_exact_tokens", [])),
        "stale_exact_tokens": list(oracle.get("stale_exact_tokens", [])),
        "expected_state_labels": dict(oracle.get("expected_state_labels", {})),
        "expected_state_transitions": list(oracle.get("expected_state_transitions", [])),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--oracle", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--manifest", required=True, type=Path)
    args = ap.parse_args()
    source_hash = sha256_file(args.oracle)
    rows = read_jsonl(args.oracle)
    sidecars = [derive(row, source_hash) for row in rows]
    write_jsonl(args.out, sidecars)
    manifest = {
        "schema": "carried_state_validity_v2.oracle_sidecar_manifest.v1",
        "source_oracle": str(args.oracle),
        "source_oracle_sha256": source_hash,
        "sidecar": str(args.out),
        "sidecar_sha256": sha256_file(args.out),
        "task_count": len(sidecars),
        "family_counts": {family: sum(x.get("family") == family for x in sidecars) for family in sorted({x.get("family") for x in sidecars})},
        "network_calls_performed": 0,
        "derived_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
