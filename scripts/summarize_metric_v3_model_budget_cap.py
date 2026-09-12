#!/usr/bin/env python3
"""Summarize the V3 replay by frozen model condition and carrier budget.

The V3 score records intentionally contain only scorer-facing fields.  This
script joins them to their hash-verified, saved provider records solely to
recover the pre-existing ``state_hard_cap_used`` diagnostic.  It performs no
model calls and does not alter either source surface.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_artifact_source(source_file: str, artifact_root: Path) -> Path:
    """Resolve package-relative sources or legacy paths at the artifact boundary."""
    marker = "/artifact/"
    if source_file.startswith("artifact/"):
        relative_to_artifact = source_file[len("artifact/"):]
    elif marker in source_file:
        relative_to_artifact = source_file.split(marker, 1)[1]
    else:
        raise ValueError(f"source path has no artifact boundary: {source_file}")
    candidate = artifact_root / relative_to_artifact
    if not candidate.is_file():
        raise FileNotFoundError(f"missing retained source record: {candidate}")
    return candidate


def hard_cap_used(source_row: dict) -> bool:
    audits = source_row.get("compiler_audits")
    if audits is None:
        audits = source_row.get("raw_response", {}).get("compiler_audits", [])
    return bool(source_row.get("state_hard_cap_used")) or any(
        bool(audit.get("state_hard_cap_used")) for audit in audits
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True, type=Path)
    parser.add_argument("--scores", required=True, type=Path)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    inputs = list(read_jsonl(args.inputs))
    scores = {row["row_id"]: row for row in read_jsonl(args.scores)}
    if len(inputs) != len(scores) or {row["row_id"] for row in inputs} != set(scores):
        raise ValueError("V3 inputs and score records do not have the same row identifiers")

    source_rows: dict[Path, dict[str, dict]] = {}
    groups: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"rows": 0, "hard_cap_rows": 0, "answer_rows": 0,
                 "answer_aligned_validity_rows": 0, "joint_rows": 0}
    )
    for row in inputs:
        source_path = resolve_artifact_source(row["source_file"], args.artifact_root)
        if source_path not in source_rows:
            expected_hash = row["source_file_sha256"]
            if sha256(source_path) != expected_hash:
                raise ValueError(f"source hash mismatch: {source_path}")
            source_rows[source_path] = {source_row["row_id"]: source_row for source_row in read_jsonl(source_path)}
        source_row = source_rows[source_path].get(row["row_id"])
        if source_row is None:
            raise ValueError(f"source record missing row: {row['row_id']}")

        score = scores[row["row_id"]]
        key = (row["model"], row["budget"])
        group = groups[key]
        group["rows"] += 1
        group["hard_cap_rows"] += int(hard_cap_used(source_row))
        group["answer_rows"] += int(bool(score["final_answer_success_v2"]))
        group["answer_aligned_validity_rows"] += int(bool(score["carried_state_validity_v3"]))
        group["joint_rows"] += int(bool(score["joint_final_answer_state_success_v3"]))

    fieldnames = [
        "model", "budget", "rows", "hard_cap_rows", "hard_cap_rate",
        "answer_rows", "answer_rate", "answer_aligned_validity_rows",
        "answer_aligned_validity_rate", "joint_rows", "joint_rate",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for (model, budget), values in sorted(groups.items()):
            row = {"model": model, "budget": budget, **values}
            for name in ("hard_cap", "answer", "answer_aligned_validity", "joint"):
                row[f"{name}_rate"] = f"{values[f'{name}_rows'] / values['rows']:.6f}"
            writer.writerow(row)

    print(json.dumps({
        "rows": len(inputs), "groups": len(groups), "source_files_hash_verified": len(source_rows),
        "hard_cap_rows": sum(group["hard_cap_rows"] for group in groups.values()),
        "answer_aligned_validity_rows": sum(group["answer_aligned_validity_rows"] for group in groups.values()),
        "joint_rows": sum(group["joint_rows"] for group in groups.values()),
        "network_calls_performed": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
