#!/usr/bin/env python3
"""Targeted technical backfill for two PCG dynamic-state v2 missing rows.

The script preserves the original packets. It reuses the original runner,
compiler, prompt, provider, request-control, and scorer code for the affected
rows, but writes all backfill artifacts into a separate packet.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKFILL_ID = "pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623"
RESULT_DIR = PROJECT_ROOT / "results" / BACKFILL_ID
RAW_ROOT = PROJECT_ROOT / "private" / "model_outputs" / BACKFILL_ID
AUDIT_JSON = RESULT_DIR / "BACKFILL_AUDIT.json"
AUDIT_MD = RESULT_DIR / "BACKFILL_AUDIT.md"
CONTROLLED_ROWS = RESULT_DIR / "BACKFILL_CONTROLLED_ROWS.jsonl"
SCORES_JSONL = RESULT_DIR / "BACKFILL_SCORES.jsonl"
SCORES_CSV = RESULT_DIR / "BACKFILL_SCORES.csv"
HASH_MANIFEST = RESULT_DIR / "BACKFILL_HASH_MANIFEST.jsonl"
SENSITIVITY_MD = RESULT_DIR / "MISSINGNESS_SENSITIVITY_AUDIT.md"

DECISIVE_RUNNER_PATH = PROJECT_ROOT / "tools" / "run_ecvs_deepseek_pcg_dynamic_state_v2_e10_h3_decisive_4method_2budget_1run.py"
RANDOM10_RUNNER_PATH = PROJECT_ROOT / "tools" / "run_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py"


TARGETS = [
    {
        "packet_id": "deepseek_decisive_104",
        "module": "decisive",
        "role": "method_triage_decisive_probe_missing_mature_ssr_row",
        "experiment_id": "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run",
        "result_dir": PROJECT_ROOT
        / "results"
        / "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run",
        "config": PROJECT_ROOT
        / "configs"
        / "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run.json",
        "model_visible": PROJECT_ROOT
        / "data"
        / "pcg_dynamic_state_v2"
        / "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run"
        / "MODEL_VISIBLE_TASK_MANIFEST.jsonl",
        "oracle": PROJECT_ROOT
        / "data"
        / "pcg_dynamic_state_v2"
        / "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run"
        / "SCORER_ORACLE_MANIFEST.jsonl",
        "runner": DECISIVE_RUNNER_PATH,
        "scorer": PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_outputs.py",
        "task_id": "pcgds_v2_00026_decoy_heavy_same_prefix_config_easy",
        "method": "mature_ssr_loop",
        "budget": 600,
        "run_id": 1,
    },
    {
        "packet_id": "deepseek_random10_rerun100",
        "module": "random10",
        "role": "direct_provider_random10_probe_missing_loop_only_row",
        "experiment_id": "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100",
        "result_dir": PROJECT_ROOT
        / "results"
        / "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100",
        "config": PROJECT_ROOT
        / "configs"
        / "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100.json",
        "model_visible": PROJECT_ROOT
        / "data"
        / "pcg_dynamic_state_v2"
        / "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100"
        / "MODEL_VISIBLE_TASK_MANIFEST.jsonl",
        "oracle": PROJECT_ROOT
        / "data"
        / "pcg_dynamic_state_v2"
        / "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100"
        / "SCORER_ORACLE_MANIFEST.jsonl",
        "runner": RANDOM10_RUNNER_PATH,
        "scorer": PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_main_matrix.py",
        "task_id": "pcgds_v2_00032_decoy_heavy_same_prefix_config_hard",
        "method": "loop_only",
        "budget": 300,
        "run_id": 1,
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def find_row(rows: list[dict[str, Any]], target: dict[str, Any]) -> dict[str, Any] | None:
    for row in rows:
        if (
            row.get("task_id") == target["task_id"]
            and row.get("method") == target["method"]
            and int(row.get("budget", row.get("state_budget"))) == int(target["budget"])
            and int(row.get("run_id", 1)) == int(target["run_id"])
        ):
            return row
    return None


def row_key(target: dict[str, Any]) -> str:
    return f"{target['experiment_id']}::{target['task_id']}::{target['method']}::budget{target['budget']}::run{target['run_id']}"


def configure_runner(target: dict[str, Any], decisive_module: Any, random_module: Any, raw_dir: Path) -> Any:
    if target["module"] == "decisive":
        runner = decisive_module
        runner.RAW_DIR = raw_dir
        return runner

    random_module.patch_base_globals()
    runner = random_module.B
    runner.EXPERIMENT_ID = target["experiment_id"]
    runner.MODEL_VISIBLE_SUBSET = target["model_visible"]
    runner.SCORER_ORACLE_SUBSET = target["oracle"]
    runner.CONFIG_PATH = target["config"]
    runner.RESULT_DIR = target["result_dir"]
    runner.RAW_DIR = raw_dir
    runner.SCORER_PATH = target["scorer"]
    runner.build_update_prompt = random_module.build_update_prompt
    runner.compile_state = random_module.compile_state
    runner.build_final_prompt = random_module.build_final_prompt
    runner.git_commit = lambda: "git_not_invoked_by_policy"
    return runner


def score_row_for_output(target: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    metric_keys = {
        "task_id",
        "method",
        "model",
        "budget",
        "run_id",
        "state_budget",
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
        "provider_call_count",
        "final_output_construction",
        "gate_status",
        "gate_reason",
    }
    out = {key: value for key, value in row.items() if key in metric_keys}
    out["packet_id"] = target["packet_id"]
    return out


def build_preflight() -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for target in TARGETS:
        required = [
            target["result_dir"] / "CONTROLLED_ROWS.jsonl",
            target["config"],
            target["model_visible"],
            target["oracle"],
            target["runner"],
            target["scorer"],
        ]
        missing = [rel(path) for path in required if not path.exists()]
        original_rows = read_jsonl(target["result_dir"] / "CONTROLLED_ROWS.jsonl") if not missing else []
        original_row = find_row(original_rows, target)
        finding = {
            "packet_id": target["packet_id"],
            "target_key": row_key(target),
            "required_files_missing": missing,
            "original_row_found": original_row is not None,
            "original_gate_status": original_row.get("gate_status") if original_row else None,
            "original_gate_reason": original_row.get("gate_reason") if original_row else None,
            "original_config_sha256": file_sha256(target["config"]) if target["config"].exists() else None,
            "original_runner_sha256": file_sha256(target["runner"]) if target["runner"].exists() else None,
            "original_scorer_sha256": file_sha256(target["scorer"]) if target["scorer"].exists() else None,
            "original_model_visible_sha256": file_sha256(target["model_visible"]) if target["model_visible"].exists() else None,
            "original_oracle_sha256": file_sha256(target["oracle"]) if target["oracle"].exists() else None,
            "preflight_status": "PASS"
            if not missing
            and original_row is not None
            and original_row.get("gate_status") == "rerun_required"
            and original_row.get("gate_reason") == "backend_or_empty_output"
            else "FAIL",
        }
        findings.append(finding)
    return {
        "backfill_id": BACKFILL_ID,
        "created_at_utc": utc_now(),
        "api_called": False,
        "api_key_value_printed": False,
        "scope": "targeted technical backfill for two backend_or_empty_output rows; no protocol, prompt, scorer, dataset, model, provider, or sampling changes",
        "targets": findings,
        "overall_status": "PASS" if all(item["preflight_status"] == "PASS" for item in findings) else "FAIL",
    }


def assert_preflight(audit: dict[str, Any]) -> None:
    if audit["overall_status"] != "PASS":
        raise SystemExit("Backfill preflight failed:\n" + json.dumps(audit, ensure_ascii=False, indent=2))


def run_target(target: dict[str, Any], decisive_module: Any, random_module: Any, credential: str) -> dict[str, Any]:
    raw_dir = RAW_ROOT / target["packet_id"] / "deepseek"
    runner = configure_runner(target, decisive_module, random_module, raw_dir)
    visible_by_id = {row["task_id"]: row for row in read_jsonl(target["model_visible"])}
    oracle_by_id = {row["task_id"]: row for row in read_jsonl(target["oracle"])}
    task = visible_by_id[target["task_id"]]
    oracle = oracle_by_id[target["task_id"]]
    row = runner.run_one_row(
        task,
        oracle,
        target["method"],
        int(target["budget"]),
        int(target["run_id"]),
        credential,
        file_sha256(target["config"]),
        file_sha256(target["runner"]),
        file_sha256(target["scorer"]),
    )
    row["backfill_id"] = BACKFILL_ID
    row["backfill_packet_id"] = target["packet_id"]
    row["backfill_role"] = target["role"]
    row["backfill_created_at_utc"] = utc_now()
    row["backfill_runner_sha256"] = file_sha256(Path(__file__).resolve())
    row["original_experiment_id"] = target["experiment_id"]
    row["original_result_dir"] = rel(target["result_dir"])
    row["original_config_path"] = rel(target["config"])
    row["original_runner_path"] = rel(target["runner"])
    row["original_scorer_path"] = rel(target["scorer"])
    row["targeted_backfill_policy"] = "append_only_no_original_overwrite"
    row["backfill_row_sha256"] = sha256_json(row)
    return row


def bool01(value: Any) -> int:
    return 1 if bool(value) else 0


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "measured_rows": sum(1 for row in rows if row.get("gate_status") == "measured"),
        "rerun_required_rows": sum(1 for row in rows if row.get("gate_status") == "rerun_required"),
        "by_target": [
            {
                "packet_id": row.get("backfill_packet_id"),
                "task_id": row.get("task_id"),
                "method": row.get("method"),
                "budget": row.get("budget", row.get("state_budget")),
                "run_id": row.get("run_id"),
                "gate_status": row.get("gate_status"),
                "gate_reason": row.get("gate_reason"),
                "answer_success": bool(row.get("answer_success")),
                "state_governance_success": bool(row.get("state_governance_success")),
                "reliable_composite_success": bool(row.get("reliable_composite_success")),
                "provider_call_count": row.get("provider_call_count"),
                "private_raw_ref": row.get("private_raw_ref"),
                "backfill_row_sha256": row.get("backfill_row_sha256"),
            }
            for row in rows
        ],
    }


def sensitivity_text(rows: list[dict[str, Any]]) -> str:
    decisive = next((row for row in rows if row.get("backfill_packet_id") == "deepseek_decisive_104"), None)
    random_row = next((row for row in rows if row.get("backfill_packet_id") == "deepseek_random10_rerun100"), None)
    decisive_rel = bool01(decisive.get("reliable_composite_success")) if decisive else 0
    decisive_after = (3 + decisive_rel) / 26
    random_loop_rel = bool01(random_row.get("reliable_composite_success")) if random_row else 0
    return f"""# Missingness Sensitivity Audit

Backfill id: `{BACKFILL_ID}`

## Scope

This is a targeted technical backfill for two `backend_or_empty_output` rows.
It does not change the original protocol, prompts, task manifests, provider,
sampling controls, scorer, or original result packets.

## Backfilled Rows

| packet | task | method | budget | gate | answer | governance | reliable |
|---|---|---|---:|---|---:|---:|---:|
| `deepseek_decisive_104` | `{decisive.get("task_id") if decisive else ""}` | `{decisive.get("method") if decisive else ""}` | `{decisive.get("budget", decisive.get("state_budget")) if decisive else ""}` | `{decisive.get("gate_status") if decisive else ""}` | `{bool(decisive.get("answer_success")) if decisive else ""}` | `{bool(decisive.get("state_governance_success")) if decisive else ""}` | `{bool(decisive.get("reliable_composite_success")) if decisive else ""}` |
| `deepseek_random10_rerun100` | `{random_row.get("task_id") if random_row else ""}` | `{random_row.get("method") if random_row else ""}` | `{random_row.get("budget", random_row.get("state_budget")) if random_row else ""}` | `{random_row.get("gate_status") if random_row else ""}` | `{bool(random_row.get("answer_success")) if random_row else ""}` | `{bool(random_row.get("state_governance_success")) if random_row else ""}` | `{bool(random_row.get("reliable_composite_success")) if random_row else ""}` |

## Decision Sensitivity

- Original decisive mature SSR reliable count was `3/26 = 0.115`.
- With this targeted backfill row counted as observed, mature SSR reliable is
  `{3 + decisive_rel}/26 = {decisive_after:.3f}`.
- The decisive visible-carry comparator remains `13/26 = 0.500`.
- Therefore the preregistered downgrade conclusion is unchanged.
- The random10 backfill target is `loop_only`; its reliable value is
  `{random_loop_rel}` and it is not part of the SSR-vs-visible comparison.

## Interpretation

The backfill closes a reviewer-facing missingness gap. It does not rescue
tested mature/schema-heavy SSR as a primary method.
"""


def write_hash_manifest(extra_paths: list[Path]) -> None:
    paths = [
        Path(__file__).resolve(),
        AUDIT_JSON,
        AUDIT_MD,
        CONTROLLED_ROWS,
        SCORES_JSONL,
        SCORES_CSV,
        SENSITIVITY_MD,
    ]
    for target in TARGETS:
        paths.extend([target["config"], target["model_visible"], target["oracle"], target["runner"], target["scorer"]])
    paths.extend(extra_paths)
    rows = []
    seen: set[Path] = set()
    for path in paths:
        if path.exists() and path not in seen:
            rows.append(
                {
                    "path": rel(path),
                    "sha256": file_sha256(path),
                    "size_bytes": path.stat().st_size,
                    "mtime_ns": path.stat().st_mtime_ns,
                }
            )
            seen.add(path)
    write_jsonl(HASH_MANIFEST, rows)


def write_audit_md(audit: dict[str, Any], rows: list[dict[str, Any]] | None = None) -> None:
    target_lines = "\n".join(
        f"| `{item['packet_id']}` | `{item['target_key']}` | `{item['original_gate_status']}` | `{item['original_gate_reason']}` | `{item['preflight_status']}` |"
        for item in audit["targets"]
    )
    result_section = ""
    if rows is not None:
        result_lines = "\n".join(
            f"| `{row.get('backfill_packet_id')}` | `{row.get('task_id')}` | `{row.get('method')}` | `{row.get('budget', row.get('state_budget'))}` | `{row.get('gate_status')}` | `{bool(row.get('answer_success'))}` | `{bool(row.get('state_governance_success'))}` | `{bool(row.get('reliable_composite_success'))}` | `{row.get('private_raw_ref')}` |"
            for row in rows
        )
        result_section = f"""
## Backfill Results

| packet | task | method | budget | gate | answer | governance | reliable | raw ref |
|---|---|---|---:|---|---:|---:|---:|---|
{result_lines}
"""
    AUDIT_MD.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_MD.write_text(
        f"""# Targeted Missing-Row Backfill Audit

Backfill id: `{BACKFILL_ID}`

Status: `{audit['overall_status']}`

This packet is append-only. It does not overwrite the original result packets.
API key values are never printed or written.

## Targets

| packet | row | original gate | original reason | preflight |
|---|---|---|---|---|
{target_lines}
{result_section}
## Variable Control

- Provider: direct DeepSeek.
- Requested model: `deepseek-v4-pro`.
- Temperature: explicit `0`.
- Max tokens: `4096`.
- Thinking control: `thinking.type=disabled`.
- Tools/web/cache: disabled or not requested.
- Fallback: disabled.
- Original configs, task manifests, method protocols, runners, and scorers are reused.

## Non-Pooling Rule

These rows are targeted technical backfill rows. Use them to close missingness
only; do not treat them as a new protocol version or as a new matrix.
""",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-api", action="store_true", help="Call DeepSeek for the two missing rows.")
    parser.add_argument("--max-workers", type=int, default=1)
    args = parser.parse_args()

    audit = build_preflight()
    write_json(AUDIT_JSON, audit)
    write_audit_md(audit)
    print(json.dumps({"backfill_id": BACKFILL_ID, "preflight_status": audit["overall_status"], "result_dir": rel(RESULT_DIR)}, ensure_ascii=False, indent=2))
    assert_preflight(audit)

    if not args.run_api:
        write_hash_manifest([])
        return 0

    if CONTROLLED_ROWS.exists():
        raise SystemExit(f"Refusing to overwrite existing backfill rows: {rel(CONTROLLED_ROWS)}")

    decisive_module = load_module(DECISIVE_RUNNER_PATH, "pcg_v2_decisive_runner_for_backfill")
    random_module = load_module(RANDOM10_RUNNER_PATH, "pcg_v2_random10_runner_for_backfill")
    credential = decisive_module.get_api_key()
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = [
            pool.submit(run_target, target, decisive_module, random_module, credential)
            for target in TARGETS
        ]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(f"completed {len(rows)}/{len(TARGETS)} {row['backfill_packet_id']} {row['task_id']} {row['method']} budget={row.get('budget', row.get('state_budget'))}", flush=True)

    rows.sort(key=lambda row: (row["backfill_packet_id"], row["task_id"], row["method"], int(row.get("budget", row.get("state_budget")))))
    write_jsonl(CONTROLLED_ROWS, rows)
    score_rows = [score_row_for_output(next(target for target in TARGETS if target["packet_id"] == row["backfill_packet_id"]), row) for row in rows]
    write_jsonl(SCORES_JSONL, score_rows)
    write_csv(SCORES_CSV, score_rows)
    audit = {**audit, "api_called": True, "completed_at_utc": utc_now(), "result_summary": summarize_rows(rows)}
    write_json(AUDIT_JSON, audit)
    write_audit_md(audit, rows)
    SENSITIVITY_MD.write_text(sensitivity_text(rows), encoding="utf-8", newline="\n")
    raw_paths = [Path(row["private_raw_ref"]) if Path(row["private_raw_ref"]).is_absolute() else PROJECT_ROOT / row["private_raw_ref"] for row in rows]
    write_hash_manifest(raw_paths)
    print(json.dumps(audit["result_summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
