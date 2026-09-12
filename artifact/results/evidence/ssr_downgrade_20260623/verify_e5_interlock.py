#!/usr/bin/env python3
"""Verify E5 interlock coverage for the SSR downgrade evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[3]
LOCKS = {
    "core_pcg_v2": {
        "dir": ROOT / "data" / "pcg_dynamic_state_v2" / "h5_release_lock_20260623",
        "controlled_logs": [
            ROOT
            / "results"
            / "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run"
            / "CONTROLLED_ROWS.jsonl",
            ROOT
            / "results"
            / "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100"
            / "CONTROLLED_ROWS.jsonl",
            ROOT
            / "results"
            / "_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers"
            / "CONTROLLED_ROWS.jsonl",
            ROOT
            / "results"
            / "_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers"
            / "CONTROLLED_ROWS.jsonl",
        ],
    },
    "targeted_backfill": {
        "dir": ROOT / "data" / "pcg_dynamic_state_v2" / "h5_targeted_backfill_lock_20260623",
        "controlled_logs": [
            ROOT
            / "results"
            / "pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623"
            / "BACKFILL_CONTROLLED_ROWS.jsonl",
        ],
    },
    "static_sanity": {
        "dir": ROOT / "data" / "pcg_dynamic_state_v2" / "h5_static_sanity_lock_20260623",
        "controlled_logs": [
            ROOT
            / "results"
            / "pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623"
            / "CONTROLLED_ROWS.jsonl",
        ],
    },
}
REQUIRED_PARENT_HASHES = {
    "dataset_hash",
    "prompt_hash",
    "config_file_byte_sha256",
    "environment_lock_sha256",
    "request_hash",
    "raw_private_file_byte_sha256",
    "raw_response_canonical_sha256_existing",
    "parsed_output_sha256",
    "metric_record_sha256",
    "score_row_canonical_sha256",
    "controlled_row_canonical_sha256",
}


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


def git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(ROOT), *args], text=True, capture_output=True, check=False)


def archive_commit_status() -> dict[str, Any]:
    return {
        "passed": True,
        "release_git_commit": None,
        "archive_mode": True,
        "commit_source": None,
        "dirty_entries": [],
        "cleanliness_check": "not_applicable_to_git_archive",
        "note": "Archive mode verifies internal hash closure and lock consistency without embedded Git metadata.",
        "failures": [],
    }


def git_status(allow_dirty: bool) -> dict[str, Any]:
    if (REPO_ROOT / "RELEASE_METADATA").is_dir():
        return archive_commit_status()

    head = git(["rev-parse", "--verify", "HEAD"])
    if head.returncode != 0:
        return archive_commit_status()

    top = git(["rev-parse", "--show-toplevel"])
    git_root = Path(top.stdout.strip())
    rel_root = ROOT.relative_to(git_root).as_posix()
    dirty = subprocess.run(
        [
            "git",
            "-C",
            str(git_root),
            "status",
            "--porcelain",
            "--untracked-files=normal",
            "--",
            rel_root,
            "artifact/README.md",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    dirty_lines = [line for line in dirty.stdout.splitlines() if line.strip()]
    passed = allow_dirty or not dirty_lines
    return {
        "passed": passed,
        "release_git_commit": head.stdout.strip(),
        "dirty_entries": dirty_lines,
        "failures": [] if passed else ["release artifact files are not committed"],
    }


def redaction_hash_sources() -> dict[str, list[str]]:
    path = ROOT / "REDACTION_MAP.json"
    if not path.exists():
        return {}
    data = read_json(path)
    sources: dict[str, list[str]] = {}
    for item in data.get("redactions", []):
        rel = item["path"]
        sources.setdefault(item["original_sha256"], []).append(f"redacted_original:{rel}")
        sources.setdefault(item["public_sha256"], []).append(f"redacted_public:{rel}")
        prior_public = item.get("prior_public_sha256")
        if prior_public:
            sources.setdefault(prior_public, []).append(f"redacted_prior_public:{rel}")
    return sources


def file_hash_sources() -> dict[str, list[str]]:
    sources: dict[str, list[str]] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        sources.setdefault(file_sha256(path), []).append(rel)
    for digest, paths in redaction_hash_sources().items():
        sources.setdefault(digest, []).extend(paths)
    return sources


def environment_locks() -> tuple[dict[str, str], list[dict[str, Any]]]:
    env_by_lock_dir: dict[str, str] = {}
    failures: list[dict[str, Any]] = []
    for lock in LOCKS.values():
        lock_dir = lock["dir"]
        env_path = lock_dir / "ENVIRONMENT_LOCK.json"
        rel = env_path.relative_to(ROOT).as_posix()
        if not env_path.exists():
            failures.append({"missing_environment_lock": rel})
            continue
        env = read_json(env_path)
        declared = env.get("environment_lock_sha256")
        material = {key: value for key, value in env.items() if key != "environment_lock_sha256"}
        actual = sha256_json(material)
        if actual != declared:
            failures.append({"environment_hash_mismatch": rel, "expected": declared, "actual": actual})
        req_path = env.get("requirements_path")
        req_sha = env.get("requirements_sha256")
        if req_path and req_sha:
            req_file = ROOT / req_path
            if not req_file.exists():
                failures.append({"requirements_missing": req_path})
            elif file_sha256(req_file) != req_sha:
                failures.append({"requirements_hash_mismatch": req_path, "expected": req_sha, "actual": file_sha256(req_file)})
        env_by_lock_dir[lock_dir.name] = declared
    return env_by_lock_dir, failures


def controlled_index(paths: list[Path]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    index: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, Any]] = []
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        if not path.exists():
            failures.append({"missing_controlled_log": rel})
            continue
        for row in read_jsonl(path):
            gid = row.get("global_artifact_id")
            if not gid:
                failures.append({"controlled_row_missing_global_artifact_id": rel})
                continue
            if gid in index:
                failures.append({"duplicate_controlled_global_artifact_id": gid, "path": rel})
            index[gid] = row
    return index, failures


def compare(row_value: Any, controlled_value: Any, field: str, gid: str, failures: list[dict[str, Any]]) -> None:
    if row_value != controlled_value:
        failures.append(
            {
                "field_mismatch": field,
                "global_artifact_id": gid,
                "row_value": row_value,
                "controlled_value": controlled_value,
            }
        )


def verify_row(
    row: dict[str, Any],
    controlled: dict[str, Any],
    hash_sources: dict[str, list[str]],
    lock_dir_name: str,
    expected_env_hash: str | None,
    allow_superseded_missingness: bool = False,
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    gid = row.get("global_artifact_id")
    parents = row.get("parent_hashes", {})

    material = {key: value for key, value in row.items() if key not in {"release_row_h5_sha256", "h5_status", "public_review_status"}}
    if sha256_json(material) != row.get("release_row_h5_sha256"):
        failures.append({"row_h5_hash_mismatch": gid})

    missing = sorted(key for key in REQUIRED_PARENT_HASHES if not parents.get(key))
    if missing:
        failures.append({"missing_parent_hashes": gid, "fields": missing})

    if expected_env_hash and parents.get("environment_lock_sha256") != expected_env_hash:
        failures.append(
            {
                "environment_hash_not_linked_to_lock": gid,
                "expected": expected_env_hash,
                "actual": parents.get("environment_lock_sha256"),
            }
        )

    compare(parents.get("dataset_hash"), controlled.get("task_manifest_sha256"), "dataset_hash/task_manifest_sha256", gid, failures)
    compare(parents.get("prompt_hash"), controlled.get("prompt_hash"), "prompt_hash", gid, failures)
    compare(parents.get("request_hash"), controlled.get("request_hash"), "request_hash", gid, failures)
    compare(
        parents.get("raw_response_canonical_sha256_existing"),
        controlled.get("raw_response_sha256"),
        "raw_response_sha256",
        gid,
        failures,
    )
    compare(parents.get("parsed_output_sha256"), controlled.get("parsed_output_sha256"), "parsed_output_sha256", gid, failures)
    compare(parents.get("metric_record_sha256"), controlled.get("metric_record_sha256"), "metric_record_sha256", gid, failures)
    compare(row.get("existing_manifest_entry_hash"), controlled.get("manifest_entry_hash"), "manifest_entry_hash", gid, failures)
    compare(row.get("existing_h5_chain_hash"), controlled.get("h5_chain_hash"), "h5_chain_hash", gid, failures)

    config_hash = parents.get("config_file_byte_sha256")
    controlled_config_hash = controlled.get("config_sha256")
    if config_hash != controlled_config_hash:
        if not (
            controlled_config_hash
            and controlled_config_hash in hash_sources
            and config_hash
            and config_hash in hash_sources
        ):
            failures.append(
                {
                    "field_mismatch": "config_sha256",
                    "global_artifact_id": gid,
                    "row_value": config_hash,
                    "controlled_value": controlled_config_hash,
                }
            )

    runner_hash = parents.get("runner_file_byte_sha256")
    controlled_runner_hash = controlled.get("runner_sha256")
    if runner_hash != controlled_runner_hash:
        # Provider wrappers can delegate row construction to a shared base runner.
        # The H5 row records the wrapper byte hash; the controlled row may retain
        # the imported base-runner hash. E5 requires both hashes to have public
        # sources, not byte equality between wrapper and delegate.
        if controlled_runner_hash and controlled_runner_hash not in hash_sources:
            failures.append(
                {
                    "controlled_runner_hash_has_no_public_file_source": gid,
                    "row_runner_hash": runner_hash,
                    "controlled_runner_hash": controlled_runner_hash,
                }
            )

    oracle_hash = parents.get("oracle_hash")
    if oracle_hash and controlled.get("scorer_oracle_sha256"):
        compare(oracle_hash, controlled.get("scorer_oracle_sha256"), "oracle_hash/scorer_oracle_sha256", gid, failures)

    for label, digest in [
        ("dataset_hash", parents.get("dataset_hash")),
        ("config_hash", config_hash),
        ("runner_hash", runner_hash),
        ("eval_harness_hash", row.get("effective_eval_harness_sha256") or parents.get("scorer_file_byte_sha256")),
        ("parser_hash", row.get("effective_parser_sha256") or parents.get("scorer_file_byte_sha256")),
        ("raw_output_hash", parents.get("raw_private_file_byte_sha256")),
    ]:
        if digest and digest not in hash_sources:
            failures.append({"hash_has_no_public_file_source": gid, "hash_label": label, "sha256": digest})

    raw_ref = row.get("raw_private_ref")
    raw_sha = parents.get("raw_private_file_byte_sha256")
    if raw_ref and raw_sha:
        raw_path = ROOT / raw_ref
        if not raw_path.exists():
            failures.append({"raw_output_missing": gid, "path": raw_ref})
        elif file_sha256(raw_path) != raw_sha:
            failures.append({"raw_output_hash_mismatch": gid, "path": raw_ref, "expected": raw_sha, "actual": file_sha256(raw_path)})

    if (row.get("gate_status") != "measured" or row.get("gate_reason") != "ok") and not allow_superseded_missingness:
        failures.append({"row_not_measured_ok": gid, "gate_status": row.get("gate_status"), "gate_reason": row.get("gate_reason")})
    if row.get("score_row_joined") is not True:
        failures.append({"score_row_not_joined": gid})
    if not row.get("provider") or not row.get("requested_model") or not row.get("selected_model_or_returned_model"):
        failures.append({"model_provider_record_incomplete": gid})

    return failures


def verify_locks(hash_sources: dict[str, list[str]], env_by_lock_dir: dict[str, str]) -> dict[str, Any]:
    lock_results: dict[str, Any] = {}
    all_failures: list[dict[str, Any]] = []
    backfill_gids: set[str] = set()
    backfill_log = LOCKS["targeted_backfill"]["controlled_logs"][0]
    if backfill_log.exists():
        backfill_gids = {row["global_artifact_id"] for row in read_jsonl(backfill_log) if row.get("global_artifact_id")}
    for lock_name, spec in LOCKS.items():
        lock_dir = spec["dir"]
        row_manifest = lock_dir / "ROW_H5_MANIFEST.jsonl"
        rows = read_jsonl(row_manifest)
        controlled, controlled_failures = controlled_index(spec["controlled_logs"])
        failures = list(controlled_failures)
        superseded_rows = 0
        for row in rows:
            gid = row.get("global_artifact_id")
            controlled_row = controlled.get(gid)
            if controlled_row is None:
                failures.append({"controlled_row_missing_for_h5_row": gid})
                continue
            is_superseded_core_gap = lock_name == "core_pcg_v2" and gid in backfill_gids
            if is_superseded_core_gap:
                superseded_rows += 1
            failures.extend(
                verify_row(
                    row,
                    controlled_row,
                    hash_sources,
                    lock_dir.name,
                    env_by_lock_dir.get(lock_dir.name),
                    allow_superseded_missingness=is_superseded_core_gap,
                )
            )
        lock_results[lock_name] = {
            "passed": not failures,
            "row_count": len(rows),
            "effective_e5_row_count": len(rows) - superseded_rows,
            "superseded_by_targeted_backfill": superseded_rows,
            "controlled_row_count": len(controlled),
            "failure_count": len(failures),
            "failures": failures[:50],
        }
        all_failures.extend({"lock": lock_name, **failure} for failure in failures)
    return {"passed": not all_failures, "lock_results": lock_results, "failures": all_failures[:100]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-dirty", action="store_true", help="Do not fail on uncommitted release artifact files.")
    args = parser.parse_args()

    git_result = git_status(allow_dirty=args.allow_dirty)
    hash_sources = file_hash_sources()
    env_by_lock_dir, env_failures = environment_locks()
    lock_result = verify_locks(hash_sources, env_by_lock_dir)

    failures: list[Any] = []
    failures.extend(git_result.get("failures", []))
    failures.extend(env_failures)
    failures.extend(lock_result.get("failures", []))

    result = {
        "schema_version": "ssr_downgrade_e5_interlock_verifier.v1",
        "passed": not failures,
        "evidence_level": "E5" if not failures else "NOT_E5",
        "scope": "Core PCG v2 downgrade H5 locks, targeted backfill H5 lock, and static sanity H5 lock.",
        "git": git_result,
        "environment_lock_failures": env_failures,
        "hash_source_count": len(hash_sources),
        "locks": lock_result["lock_results"],
        "failure_count": len(failures),
        "failures": failures[:100],
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
