#!/usr/bin/env python3
"""Verify the 2026-06-23 targeted backfill H5 lock."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCK_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "h5_targeted_backfill_lock_20260623"
REDACTION_MAP = PROJECT_ROOT / "REDACTION_MAP.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_redactions() -> dict[str, dict[str, Any]]:
    if not REDACTION_MAP.exists():
        return {}
    data = json.loads(REDACTION_MAP.read_text(encoding="utf-8"))
    return {item["path"]: item for item in data.get("redactions", [])}


def main() -> int:
    failures: list[dict[str, Any]] = []
    artifact_manifest = LOCK_DIR / "ARTIFACT_HASH_MANIFEST.jsonl"
    row_manifest = LOCK_DIR / "ROW_H5_MANIFEST.jsonl"
    summary_path = LOCK_DIR / "H5_LOCK_SUMMARY.json"

    for required in [artifact_manifest, row_manifest, summary_path]:
        if not required.exists():
            failures.append({"missing_lock_file": str(required)})

    if failures:
        print(json.dumps({"passed": False, "failures": failures}, ensure_ascii=False, indent=2))
        return 1

    redactions = load_redactions()
    redacted_artifacts_checked: list[str] = []
    for item in read_jsonl(artifact_manifest):
        path = PROJECT_ROOT / item["path"]
        redaction = redactions.get(item["path"])
        if redaction:
            redacted_artifacts_checked.append(item["path"])
            if item["sha256"] != redaction.get("original_sha256"):
                failures.append(
                    {
                        "redaction_original_hash_mismatch": item["path"],
                        "expected": redaction.get("original_sha256"),
                        "actual": item["sha256"],
                    }
                )
            if not path.exists():
                failures.append({"redacted_public_file_missing": item["path"]})
                continue
            actual_public = file_sha256(path)
            if actual_public != redaction.get("public_sha256"):
                failures.append(
                    {
                        "redacted_public_hash_mismatch": item["path"],
                        "expected": redaction.get("public_sha256"),
                        "actual": actual_public,
                    }
                )
            continue
        if not path.exists():
            failures.append({"artifact_missing": item["path"]})
            continue
        actual = file_sha256(path)
        if actual != item["sha256"]:
            failures.append({"artifact_hash_mismatch": item["path"], "expected": item["sha256"], "actual": actual})

    h5_private_rows = 0
    for row in read_jsonl(row_manifest):
        release_hash = row.get("release_row_h5_sha256")
        material = {
            key: value
            for key, value in row.items()
            if key not in {"release_row_h5_sha256", "h5_status", "public_review_status"}
        }
        actual = sha256_json(material)
        if actual != release_hash:
            failures.append(
                {
                    "row_h5_hash_mismatch": row.get("global_artifact_id"),
                    "expected": release_hash,
                    "actual": actual,
                }
            )
        if row.get("h5_status") == "H5_PRIVATE_RAW_LOCK":
            h5_private_rows += 1
        raw_ref = row.get("raw_private_ref")
        raw_sha = row.get("parent_hashes", {}).get("raw_private_file_byte_sha256")
        if raw_ref and raw_sha:
            raw_path = PROJECT_ROOT / raw_ref
            if not raw_path.exists():
                failures.append({"raw_private_missing": raw_ref})
            else:
                actual_raw = file_sha256(raw_path)
                if actual_raw != raw_sha:
                    failures.append({"raw_private_hash_mismatch": raw_ref, "expected": raw_sha, "actual": actual_raw})

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expected_rows = summary.get("row_count")
    actual_rows = len(read_jsonl(row_manifest))
    if expected_rows != actual_rows:
        failures.append({"row_count_mismatch": {"summary": expected_rows, "actual": actual_rows}})
    if summary.get("h5_private_raw_lock_rows") != h5_private_rows:
        failures.append(
            {
                "h5_private_row_count_mismatch": {
                    "summary": summary.get("h5_private_raw_lock_rows"),
                    "actual": h5_private_rows,
                }
            }
        )

    result = {
        "passed": not failures,
        "failures": failures,
        "artifact_manifest_rows": len(read_jsonl(artifact_manifest)),
        "row_manifest_rows": actual_rows,
        "h5_private_raw_lock_rows": h5_private_rows,
        "redacted_artifacts_checked": sorted(redacted_artifacts_checked),
        "public_release_status": summary.get("public_release_status"),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
