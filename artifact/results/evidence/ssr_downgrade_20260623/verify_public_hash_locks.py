#!/usr/bin/env python3
"""Verify the anonymous-review H5 hash locks.

The row manifests retain historical field names such as ``raw_private_ref``.
In this anonymous-review package those raw files are included, so this verifier
checks them byte-for-byte instead of treating them as hidden dependencies.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LOCKS = [
    ROOT / "data" / "pcg_dynamic_state_v2" / "h5_release_lock_20260623",
    ROOT / "data" / "pcg_dynamic_state_v2" / "h5_targeted_backfill_lock_20260623",
    ROOT / "data" / "pcg_dynamic_state_v2" / "h5_static_sanity_lock_20260623",
]
PRIVATE_ARTIFACT_TYPES = {"raw_output", "raw_private_output"}
HISTORICAL_MANIFEST = ROOT / "HISTORICAL_EVIDENCE_PUBLIC_HASH_MANIFEST.jsonl"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_redactions() -> dict[str, dict[str, Any]]:
    path = ROOT / "REDACTION_MAP.json"
    if not path.exists():
        return {}
    data = read_json(path)
    return {item["path"]: item for item in data.get("redactions", [])}


def verify_lock(lock_dir: Path, redactions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    redacted_artifacts: list[str] = []
    skipped_private_artifacts: list[str] = []
    verified_private_artifacts: list[str] = []
    skipped_private_raw_refs = 0
    verified_private_raw_refs = 0

    artifact_manifest = lock_dir / "ARTIFACT_HASH_MANIFEST.jsonl"
    row_manifest = lock_dir / "ROW_H5_MANIFEST.jsonl"
    summary_path = lock_dir / "H5_LOCK_SUMMARY.json"

    for required in [artifact_manifest, row_manifest, summary_path]:
        if not required.exists():
            failures.append({"missing_lock_file": str(required.relative_to(ROOT))})

    if failures:
        return {"lock_dir": str(lock_dir.relative_to(ROOT)), "passed": False, "failures": failures}

    artifact_rows = read_jsonl(artifact_manifest)
    row_manifest_rows = read_jsonl(row_manifest)

    for item in artifact_rows:
        rel = item["path"]
        artifact_type = item.get("artifact_type")
        if artifact_type in PRIVATE_ARTIFACT_TYPES or rel.startswith("private/"):
            path = ROOT / rel
            if not path.exists():
                skipped_private_artifacts.append(rel)
                continue
            actual = file_sha256(path)
            if actual != item.get("sha256"):
                failures.append(
                    {"private_artifact_hash_mismatch": rel, "expected": item.get("sha256"), "actual": actual}
                )
            else:
                verified_private_artifacts.append(rel)
            continue

        path = ROOT / rel
        redaction = redactions.get(rel)
        if redaction:
            redacted_artifacts.append(rel)
            if redaction.get("original_sha256") != item.get("sha256"):
                failures.append(
                    {
                        "redaction_original_hash_mismatch": rel,
                        "manifest_sha256": item.get("sha256"),
                        "redaction_original_sha256": redaction.get("original_sha256"),
                    }
                )
            if not path.exists():
                failures.append({"redacted_public_file_missing": rel})
                continue
            actual_public = file_sha256(path)
            if actual_public != redaction.get("public_sha256"):
                failures.append(
                    {
                        "redacted_public_hash_mismatch": rel,
                        "expected_public_sha256": redaction.get("public_sha256"),
                        "actual_public_sha256": actual_public,
                    }
                )
            continue

        if not path.exists():
            failures.append({"artifact_missing": rel})
            continue
        actual = file_sha256(path)
        if actual != item.get("sha256"):
            failures.append({"artifact_hash_mismatch": rel, "expected": item.get("sha256"), "actual": actual})

    h5_private_rows = 0
    for row in row_manifest_rows:
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
            raw_path = ROOT / raw_ref
            if not raw_path.exists():
                skipped_private_raw_refs += 1
            else:
                actual_raw = file_sha256(raw_path)
                if actual_raw != raw_sha:
                    failures.append(
                        {
                            "raw_private_hash_mismatch": raw_ref,
                            "expected": raw_sha,
                            "actual": actual_raw,
                        }
                    )
                else:
                    verified_private_raw_refs += 1

    summary = read_json(summary_path)
    if summary.get("row_count") != len(row_manifest_rows):
        failures.append(
            {"row_count_mismatch": {"summary": summary.get("row_count"), "actual": len(row_manifest_rows)}}
        )
    if summary.get("h5_private_raw_lock_rows") != h5_private_rows:
        failures.append(
            {
                "h5_private_row_count_mismatch": {
                    "summary": summary.get("h5_private_raw_lock_rows"),
                    "actual": h5_private_rows,
                }
            }
        )

    if skipped_private_raw_refs:
        review_release_status = "HASH_COMMITMENT_ONLY_FOR_MISSING_RAW_OUTPUTS"
    elif verified_private_raw_refs == h5_private_rows:
        review_release_status = "ANON_REVIEW_READY_WITH_RELEASED_RAW_OUTPUTS"
    else:
        review_release_status = "ANON_REVIEW_READY_WITH_PARTIAL_RAW_OUTPUTS"

    return {
        "lock_dir": str(lock_dir.relative_to(ROOT)),
        "passed": not failures,
        "failures": failures,
        "artifact_manifest_rows": len(artifact_rows),
        "row_manifest_rows": len(row_manifest_rows),
        "h5_private_raw_lock_rows": h5_private_rows,
        "redacted_artifacts_checked": sorted(redacted_artifacts),
        "skipped_private_artifacts": sorted(skipped_private_artifacts),
        "verified_private_artifacts": sorted(verified_private_artifacts),
        "skipped_private_raw_refs": skipped_private_raw_refs,
        "verified_private_raw_refs": verified_private_raw_refs,
        "historical_summary_public_release_status": summary.get("public_release_status"),
        "review_release_status": review_release_status,
    }


def verify_historical_manifest() -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not HISTORICAL_MANIFEST.exists():
        return {"passed": False, "failures": [{"missing_historical_manifest": str(HISTORICAL_MANIFEST.name)}]}

    rows = read_jsonl(HISTORICAL_MANIFEST)
    for row in rows:
        rel = row["path"]
        path = ROOT / rel
        if not path.exists():
            failures.append({"historical_artifact_missing": rel})
            continue
        actual = file_sha256(path)
        if actual != row.get("sha256"):
            failures.append({"historical_artifact_hash_mismatch": rel, "expected": row.get("sha256"), "actual": actual})

    roles = sorted({row.get("evidence_role") for row in rows})
    return {"passed": not failures, "failures": failures, "rows": len(rows), "evidence_roles": roles}


def main() -> int:
    redactions = load_redactions()
    results = [verify_lock(lock_dir, redactions) for lock_dir in LOCKS]
    historical_result = verify_historical_manifest()
    failures = [failure for result in results for failure in result.get("failures", [])]
    failures.extend(historical_result.get("failures", []))
    output = {
        "passed": not failures,
        "lock_results": results,
        "historical_manifest_result": historical_result,
        "redaction_map_rows": len(redactions),
        "raw_output_policy": "raw outputs referenced by the H5 locks are included in this anonymous-review package and checked byte-for-byte",
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
