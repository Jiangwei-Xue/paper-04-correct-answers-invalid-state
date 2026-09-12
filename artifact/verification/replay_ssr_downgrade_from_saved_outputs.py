#!/usr/bin/env python3
"""Offline saved-output replay for the SSR downgrade evidence packet.

This script does not call model APIs.  It replays the released evidence chain
from saved rows and raw-output files:

1. load controlled output rows;
2. locate the matching H5 row by raw-output reference;
3. verify raw file byte hashes and release-layout H5 links;
4. extract the final provider body and compare it with the saved final output;
5. rerun the hash-locked scorer and compare the reported score fields.

Historical raw files in this packet preserve full final-response bodies but
only summary hashes for intermediate state-update calls.  For that reason this
is a saved-output score replay, not a full HTTP transcript replay.

The H5 manifests also retain historical internal canonical hashes for
pre-release controlled rows and raw response objects.  Those hashes are kept as
provenance metadata, but the anonymous review package redacts provider headers
and uses a reviewer-facing released raw-output layout.  The default verifier
therefore treats those legacy internal canonical hashes as informational and
checks the current release contract instead: row/H5 identity, H5 chain links,
raw file byte hashes, final-output recovery, and score recomputation.  Use
``--strict-legacy-internal-canonical`` only when auditing the original
pre-release private layout.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_EVIDENCE_ROOT = SCRIPT_PATH.parents[1] / "results" / "evidence" / "ssr_downgrade_20260623"

CONTROLLED_ROW_FILES = [
    "results/_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run/CONTROLLED_ROWS.jsonl",
    "results/_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100/CONTROLLED_ROWS.jsonl",
    "results/_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl",
    "results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl",
    "results/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/BACKFILL_CONTROLLED_ROWS.jsonl",
    "results/pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623/CONTROLLED_ROWS.jsonl",
]

H5_MANIFEST_FILES = [
    "data/pcg_dynamic_state_v2/h5_release_lock_20260623/ROW_H5_MANIFEST.jsonl",
    "data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/ROW_H5_MANIFEST.jsonl",
    "data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/ROW_H5_MANIFEST.jsonl",
]

SCORER_FILES = [
    "tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_outputs.py",
    "tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_main_matrix.py",
]

SCORE_FIELDS = [
    "required_token_recall",
    "required_token_missing_count",
    "missing_required_tokens",
    "forbidden_token_leakage",
    "forbidden_token_hits",
    "protected_token_leakage",
    "protected_token_hits",
    "revoked_token_leakage",
    "revoked_token_hits",
    "stale_token_leakage",
    "stale_token_hits",
    "blocked_path_leakage",
    "blocked_path_hits",
    "boundary_violation",
    "state_label_accuracy",
    "state_transition_accuracy",
    "final_exact_success",
    "answer_success",
    "state_governance_success",
    "state_governance_success_legacy_no_conflict_only",
    "state_carry_surface_present",
    "state_governance_audit",
    "reliable_composite_success",
    "reliable_success",
    "state_required_token_present",
    "state_required_token_negated",
    "state_internal_conflict",
    "output_bearing_state_conflict",
    "exclusion_field_conflict",
    "state_forbidden_token_present",
    "state_forbidden_token_negated",
    "mechanical_carry_failure_mode_detected",
]


@dataclass
class FailureLog:
    max_failures: int
    count: int = 0
    items: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        self.items = []

    def add(self, kind: str, path: str, details: dict[str, Any]) -> None:
        self.count += 1
        if self.items is not None and len(self.items) < self.max_failures:
            self.items.append({"kind": kind, "path": path, "details": details})


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def canonical_json_bytes(value: Any) -> bytes:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    return payload.encode("utf-8")


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import scorer module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_scorers(evidence_root: Path) -> dict[str, dict[str, Any]]:
    scorers: dict[str, dict[str, Any]] = {}
    for index, rel_path in enumerate(SCORER_FILES):
        path = evidence_root / rel_path
        digest = file_sha256(path)
        scorers[digest] = {
            "path": rel_path,
            "sha256": digest,
            "module": load_module(path, f"ssr_saved_output_replay_scorer_{index}"),
        }
    return scorers


def load_oracles(evidence_root: Path, failures: FailureLog) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    oracle_paths = sorted((evidence_root / "data" / "pcg_dynamic_state_v2").glob("*/SCORER_ORACLE_MANIFEST.jsonl"))
    oracles: dict[str, dict[str, Any]] = {}
    oracle_hashes: dict[str, str] = {}
    duplicate_rows = 0
    for path in oracle_paths:
        for row in read_jsonl(path):
            task_id = row.get("task_id")
            if not task_id:
                failures.add("oracle_missing_task_id", str(path), {"row": row})
                continue
            digest = canonical_json_sha256(row)
            if task_id in oracle_hashes:
                duplicate_rows += 1
                if oracle_hashes[task_id] != digest:
                    failures.add(
                        "oracle_duplicate_hash_mismatch",
                        str(path),
                        {
                            "task_id": task_id,
                            "first_sha256": oracle_hashes[task_id],
                            "duplicate_sha256": digest,
                        },
                    )
                continue
            oracle_hashes[task_id] = digest
            oracles[task_id] = row
    return oracles, {
        "oracle_manifest_files": len(oracle_paths),
        "unique_tasks": len(oracles),
        "duplicate_task_rows_checked": duplicate_rows,
    }


def load_h5_by_raw_ref(evidence_root: Path, failures: FailureLog) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    h5_by_raw_ref: dict[str, dict[str, Any]] = {}
    rows_loaded = 0
    for rel_path in H5_MANIFEST_FILES:
        path = evidence_root / rel_path
        for row in read_jsonl(path):
            rows_loaded += 1
            raw_ref = row.get("raw_private_ref")
            if not raw_ref:
                failures.add("h5_missing_raw_private_ref", rel_path, {"global_artifact_id": row.get("global_artifact_id")})
                continue
            if raw_ref in h5_by_raw_ref:
                failures.add(
                    "duplicate_h5_raw_private_ref",
                    rel_path,
                    {
                        "raw_private_ref": raw_ref,
                        "first_global_artifact_id": h5_by_raw_ref[raw_ref].get("global_artifact_id"),
                        "duplicate_global_artifact_id": row.get("global_artifact_id"),
                    },
                )
                continue
            row["_h5_manifest_path"] = rel_path
            h5_by_raw_ref[raw_ref] = row
    return h5_by_raw_ref, {
        "h5_manifest_files": len(H5_MANIFEST_FILES),
        "h5_rows_loaded": rows_loaded,
        "unique_h5_raw_refs": len(h5_by_raw_ref),
    }


def extract_final_output(raw_obj: dict[str, Any]) -> str:
    final_raw = raw_obj.get("final_raw") or {}
    if not isinstance(final_raw, dict):
        return str(final_raw)
    attempts = final_raw.get("attempts") or []
    if not attempts:
        return str(final_raw.get("body", ""))
    body = str(attempts[-1].get("body", ""))
    try:
        body_obj = json.loads(body)
    except json.JSONDecodeError:
        return body
    choices = body_obj.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                return content
    return body


def compare_score_fields(
    row: dict[str, Any],
    scored: dict[str, Any],
    row_path: str,
    failures: FailureLog,
) -> int:
    mismatches = 0
    global_artifact_id = row.get("global_artifact_id")
    for field in SCORE_FIELDS:
        if field not in row:
            continue
        if field not in scored:
            mismatches += 1
            failures.add(
                "score_field_missing_from_recomputed_row",
                row_path,
                {"global_artifact_id": global_artifact_id, "field": field},
            )
            continue
        if row[field] != scored[field]:
            mismatches += 1
            failures.add(
                "score_field_mismatch",
                row_path,
                {
                    "global_artifact_id": global_artifact_id,
                    "field": field,
                    "saved_value": row[field],
                    "recomputed_value": scored[field],
                },
            )
    return mismatches


def state_calls_are_summaries(raw_obj: dict[str, Any]) -> bool:
    state_calls = raw_obj.get("state_calls")
    if not isinstance(state_calls, list) or not state_calls:
        return False
    full_body_keys = {"body", "raw_body", "raw_response", "response_body"}
    return not any(isinstance(call, dict) and full_body_keys.intersection(call.keys()) for call in state_calls)


def replay_rows(
    evidence_root: Path,
    oracles: dict[str, dict[str, Any]],
    h5_by_raw_ref: dict[str, dict[str, Any]],
    scorers: dict[str, dict[str, Any]],
    failures: FailureLog,
    strict_legacy_internal_canonical: bool,
) -> dict[str, Any]:
    packets: list[dict[str, Any]] = []
    totals = {
        "controlled_rows_checked": 0,
        "raw_files_checked": 0,
        "raw_file_byte_hashes_checked": 0,
        "legacy_raw_response_canonical_hashes_observed": 0,
        "legacy_raw_response_canonical_hash_mismatches_observed": 0,
        "legacy_controlled_row_canonical_hashes_observed": 0,
        "legacy_controlled_row_canonical_hash_mismatches_observed": 0,
        "h5_chain_hashes_checked": 0,
        "manifest_entry_hashes_checked": 0,
        "final_outputs_checked": 0,
        "score_rows_recomputed": 0,
        "state_call_summary_only_rows": 0,
    }
    seen_raw_refs: set[str] = set()
    scorer_use_counts: dict[str, int] = {}

    for rel_path in CONTROLLED_ROW_FILES:
        path = evidence_root / rel_path
        rows = read_jsonl(path)
        packet_failures_before = failures.count
        packet_stats = {
            "path": rel_path,
            "rows": len(rows),
            "score_rows_recomputed": 0,
            "raw_files_checked": 0,
            "state_call_summary_only_rows": 0,
        }

        for row in rows:
            totals["controlled_rows_checked"] += 1
            raw_ref = row.get("private_raw_ref") or row.get("raw_private_ref")
            global_artifact_id = row.get("global_artifact_id")
            if not raw_ref:
                failures.add("controlled_row_missing_raw_ref", rel_path, {"global_artifact_id": global_artifact_id})
                continue
            h5_row = h5_by_raw_ref.get(raw_ref)
            if h5_row is None:
                failures.add(
                    "h5_row_missing_for_raw_ref",
                    rel_path,
                    {"global_artifact_id": global_artifact_id, "raw_ref": raw_ref},
                )
                continue

            if h5_row.get("global_artifact_id") != global_artifact_id:
                failures.add(
                    "h5_global_artifact_id_mismatch",
                    rel_path,
                    {
                        "raw_ref": raw_ref,
                        "controlled_global_artifact_id": global_artifact_id,
                        "h5_global_artifact_id": h5_row.get("global_artifact_id"),
                    },
                )

            h5_chain_hash = row.get("h5_chain_hash")
            expected_h5_chain_hash = h5_row.get("existing_h5_chain_hash")
            if h5_chain_hash or expected_h5_chain_hash:
                totals["h5_chain_hashes_checked"] += 1
                if h5_chain_hash != expected_h5_chain_hash:
                    failures.add(
                        "h5_chain_hash_mismatch",
                        rel_path,
                        {
                            "global_artifact_id": global_artifact_id,
                            "expected": expected_h5_chain_hash,
                            "actual": h5_chain_hash,
                        },
                    )

            manifest_entry_hash = row.get("manifest_entry_hash")
            expected_manifest_entry_hash = h5_row.get("existing_manifest_entry_hash")
            if manifest_entry_hash or expected_manifest_entry_hash:
                totals["manifest_entry_hashes_checked"] += 1
                if manifest_entry_hash != expected_manifest_entry_hash:
                    failures.add(
                        "manifest_entry_hash_mismatch",
                        rel_path,
                        {
                            "global_artifact_id": global_artifact_id,
                            "expected": expected_manifest_entry_hash,
                            "actual": manifest_entry_hash,
                        },
                    )

            parent_hashes = h5_row.get("parent_hashes") or {}
            expected_controlled_sha = parent_hashes.get("controlled_row_canonical_sha256")
            if expected_controlled_sha:
                totals["legacy_controlled_row_canonical_hashes_observed"] += 1
                actual_controlled_sha = canonical_json_sha256(row)
                if actual_controlled_sha != expected_controlled_sha:
                    totals["legacy_controlled_row_canonical_hash_mismatches_observed"] += 1
                    if strict_legacy_internal_canonical:
                        failures.add(
                            "controlled_row_canonical_hash_mismatch",
                            rel_path,
                            {
                                "global_artifact_id": global_artifact_id,
                                "expected": expected_controlled_sha,
                                "actual": actual_controlled_sha,
                            },
                        )

            raw_path = evidence_root / raw_ref
            if not raw_path.exists():
                failures.add("raw_file_missing", rel_path, {"global_artifact_id": global_artifact_id, "raw_ref": raw_ref})
                continue
            if raw_ref not in seen_raw_refs:
                totals["raw_files_checked"] += 1
                packet_stats["raw_files_checked"] += 1
                seen_raw_refs.add(raw_ref)

            raw_file_sha = file_sha256(raw_path)
            expected_raw_file_sha = parent_hashes.get("raw_private_file_byte_sha256")
            if expected_raw_file_sha:
                totals["raw_file_byte_hashes_checked"] += 1
                if raw_file_sha != expected_raw_file_sha:
                    failures.add(
                        "raw_file_byte_hash_mismatch",
                        rel_path,
                        {
                            "global_artifact_id": global_artifact_id,
                            "raw_ref": raw_ref,
                            "expected": expected_raw_file_sha,
                            "actual": raw_file_sha,
                        },
                    )

            raw_rows = read_jsonl(raw_path)
            if len(raw_rows) != 1:
                failures.add(
                    "raw_file_row_count_not_one",
                    str(raw_path.relative_to(evidence_root)),
                    {"global_artifact_id": global_artifact_id, "rows": len(raw_rows)},
                )
                continue
            raw_obj = raw_rows[0]
            if raw_obj.get("global_artifact_id") != global_artifact_id:
                failures.add(
                    "raw_global_artifact_id_mismatch",
                    str(raw_path.relative_to(evidence_root)),
                    {
                        "controlled_global_artifact_id": global_artifact_id,
                        "raw_global_artifact_id": raw_obj.get("global_artifact_id"),
                    },
                )

            raw_canonical_sha = canonical_json_sha256(
                {"final_raw": raw_obj.get("final_raw"), "state_calls": raw_obj.get("state_calls")}
            )
            expected_raw_canonical_sha = (
                row.get("raw_response_sha256") or parent_hashes.get("raw_response_canonical_sha256_existing")
            )
            if expected_raw_canonical_sha:
                totals["legacy_raw_response_canonical_hashes_observed"] += 1
                if raw_canonical_sha != expected_raw_canonical_sha:
                    totals["legacy_raw_response_canonical_hash_mismatches_observed"] += 1
                    if strict_legacy_internal_canonical:
                        failures.add(
                            "raw_response_canonical_hash_mismatch",
                            str(raw_path.relative_to(evidence_root)),
                            {
                                "global_artifact_id": global_artifact_id,
                                "expected": expected_raw_canonical_sha,
                                "actual": raw_canonical_sha,
                            },
                        )

            if state_calls_are_summaries(raw_obj):
                totals["state_call_summary_only_rows"] += 1
                packet_stats["state_call_summary_only_rows"] += 1

            final_output_from_raw = extract_final_output(raw_obj)
            totals["final_outputs_checked"] += 1
            if final_output_from_raw != row.get("final_output", ""):
                failures.add(
                    "final_output_from_raw_mismatch",
                    str(raw_path.relative_to(evidence_root)),
                    {
                        "global_artifact_id": global_artifact_id,
                        "saved_final_output_len": len(str(row.get("final_output", ""))),
                        "raw_final_output_len": len(final_output_from_raw),
                    },
                )

            task_id = row.get("task_id")
            task = oracles.get(task_id)
            if task is None:
                failures.add("oracle_missing_for_task", rel_path, {"global_artifact_id": global_artifact_id, "task_id": task_id})
                continue

            scorer_sha = parent_hashes.get("scorer_file_byte_sha256")
            scorer = scorers.get(scorer_sha or "")
            if scorer is None:
                failures.add(
                    "unknown_scorer_hash",
                    rel_path,
                    {"global_artifact_id": global_artifact_id, "scorer_sha256": scorer_sha},
                )
                continue

            scorer_use_counts[scorer["path"]] = scorer_use_counts.get(scorer["path"], 0) + 1
            scored = scorer["module"].score_task(task, row)
            totals["score_rows_recomputed"] += 1
            packet_stats["score_rows_recomputed"] += 1
            compare_score_fields(row, scored, rel_path, failures)

        packet_stats["failure_count"] = failures.count - packet_failures_before
        packets.append(packet_stats)

    totals["scorer_use_counts"] = scorer_use_counts
    totals["packets"] = packets
    return totals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, default=DEFAULT_EVIDENCE_ROOT)
    parser.add_argument("--max-failures", type=int, default=50)
    parser.add_argument("--compact", action="store_true", help="print compact JSON")
    parser.add_argument(
        "--strict-legacy-internal-canonical",
        action="store_true",
        help=(
            "also fail when pre-release internal canonical row/response hashes "
            "do not match the anonymous release layout"
        ),
    )
    args = parser.parse_args()

    evidence_root = args.evidence_root.resolve()
    failures = FailureLog(max_failures=args.max_failures)

    if not evidence_root.exists():
        failures.add("evidence_root_missing", str(evidence_root), {})
        summary = {
            "schema_version": "ssr_downgrade.saved_output_replay.v1",
            "passed": False,
            "evidence_root": str(evidence_root),
            "failure_count": failures.count,
            "failures": failures.items,
        }
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=None if args.compact else 2))
        return 1

    scorers = load_scorers(evidence_root)
    oracles, oracle_summary = load_oracles(evidence_root, failures)
    h5_by_raw_ref, h5_summary = load_h5_by_raw_ref(evidence_root, failures)
    replay_summary = replay_rows(
        evidence_root,
        oracles,
        h5_by_raw_ref,
        scorers,
        failures,
        args.strict_legacy_internal_canonical,
    )

    summary = {
        "schema_version": "ssr_downgrade.saved_output_replay.v1",
        "passed": failures.count == 0,
        "mode": "offline_saved_output_score_replay",
        "evidence_root": str(evidence_root),
        "api_calls_performed": 0,
        "network_required": False,
        "legacy_internal_canonical_policy": (
            "Pre-release internal canonical hashes for controlled rows and raw response objects "
            "are reported as informational under the anonymous release layout. They are enforced "
            "only with --strict-legacy-internal-canonical. The default verifier checks the current "
            "reviewer-facing contract: H5 links, raw file byte hashes, final-output recovery, and "
            "score recomputation."
        ),
        "strict_legacy_internal_canonical": args.strict_legacy_internal_canonical,
        "limitation": (
            "Historical raw files include full final-response bodies but only summary hashes "
            "for intermediate state-update calls; final_state is replayed from CONTROLLED_ROWS.jsonl."
        ),
        "oracle_summary": oracle_summary,
        "h5_summary": h5_summary,
        "scorers": [
            {"path": scorer["path"], "sha256": scorer["sha256"]}
            for scorer in sorted(scorers.values(), key=lambda item: item["path"])
        ],
        **replay_summary,
        "failure_count": failures.count,
        "failures": failures.items,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=None if args.compact else 2))
    return 0 if failures.count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
