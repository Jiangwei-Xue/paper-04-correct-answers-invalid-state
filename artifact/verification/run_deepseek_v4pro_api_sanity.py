#!/usr/bin/env python3
"""Run and verify a small DeepSeek v4-pro API sanity baseline.

This is a diagnostic learned-policy scale reference. It is not a primary
matrix slice. Record mode performs one direct DeepSeek v4-pro call per frozen
task with 10-way concurrency by default. Check mode replays the saved cassette
through the deterministic scorer and performs zero API calls.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "artifact" / "results" / "baselines" / "deepseek_v4pro_api_sanity_20260706"
DEFAULT_BUILD_DIR = ROOT / ".verification_build" / "deepseek_v4pro_api_sanity"
VISIBLE_TASK_MANIFEST = (
    ROOT
    / "artifact"
    / "results"
    / "evidence"
    / "ssr_downgrade_20260623"
    / "data"
    / "pcg_dynamic_state_v2"
    / "main_matrix_v1"
    / "MODEL_VISIBLE_TASK_MANIFEST.jsonl"
)
ORACLE_MANIFEST = (
    ROOT
    / "artifact"
    / "results"
    / "evidence"
    / "ssr_downgrade_20260623"
    / "data"
    / "pcg_dynamic_state_v2"
    / "main_matrix_v1"
    / "SCORER_ORACLE_MANIFEST.jsonl"
)
PROVIDER_SNAPSHOT = (
    ROOT
    / "artifact"
    / "protocol"
    / "main_matrix"
    / "admission"
    / "PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_20260625.json"
)
SCORER_PATH = (
    ROOT
    / "artifact"
    / "results"
    / "evidence"
    / "ssr_downgrade_20260623"
    / "tools"
    / "pcg_dynamic_state_v2"
    / "score_pcg_dynamic_state_v2_main_matrix.py"
)

SUITE_ID = "deepseek_v4pro_api_sanity_20260706"
POLICY_ID = "deepseek_v4pro_zero_shot_task_sanity_v1"
RETRYABLE_HTTP = {408, 409, 425, 429, 500, 502, 503, 504}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_line_number"] = line_number
            row["_line_sha256"] = sha256_text(line.rstrip("\n"))
            rows.append(row)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


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
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_env_file(path: Path | None) -> None:
    if path is None:
        return
    if not path.exists():
        raise SystemExit(f"env file not found: {path}")
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def endpoint() -> dict[str, Any]:
    data = read_json(PROVIDER_SNAPSHOT)
    endpoints = {row["condition_id"]: row for row in data["endpoints"]}
    row = endpoints["deepseek_v4pro"]
    if row["requested_model"] != "deepseek-v4-pro" or row.get("openrouter_used"):
        raise SystemExit("deepseek_v4pro endpoint snapshot is not direct deepseek-v4-pro")
    return row


def request_payload(endpoint_row: dict[str, Any], prompt: str) -> dict[str, Any]:
    controls = endpoint_row["request_controls"]
    payload: dict[str, Any] = {
        "model": endpoint_row["requested_model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if "max_tokens" in controls:
        payload["max_tokens"] = controls["max_tokens"]
    temp = controls.get("temperature", {})
    if temp.get("send_mode") == "explicit":
        payload["temperature"] = temp.get("value")
    reasoning = controls.get("reasoning_or_thinking", {})
    if reasoning.get("send_mode") == "explicit" and isinstance(reasoning.get("value"), dict):
        payload.update(reasoning["value"])
    return payload


def sanitize_provider_body(body: str) -> str:
    try:
        parsed = json.loads(body)
    except Exception:
        return body

    def scrub(value: Any) -> Any:
        if isinstance(value, dict):
            out: dict[str, Any] = {}
            for key, item in value.items():
                if key.lower() in {"id", "request_id", "generation_id", "system_fingerprint"} and isinstance(item, str):
                    out[key] = f"redacted:{sha256_text(item)[:16]}"
                else:
                    out[key] = scrub(item)
            return out
        if isinstance(value, list):
            return [scrub(item) for item in value]
        return value

    return json.dumps(scrub(parsed), ensure_ascii=False, sort_keys=True)


def parse_response_content(body: str) -> tuple[str, str, str | None]:
    try:
        parsed = json.loads(body)
        content = parsed["choices"][0]["message"].get("content", "")
    except Exception as exc:
        return body, "", f"{type(exc).__name__}: {exc}"
    final_state = ""
    obj = parse_json_maybe(content)
    if isinstance(obj, dict):
        state = obj.get("final_state", obj.get("carried_state", obj.get("state", "")))
        if state:
            final_state = json.dumps(state, ensure_ascii=False, sort_keys=True) if not isinstance(state, str) else state
    return content, final_state, None


def parse_json_maybe(text: str) -> Any:
    value = str(text or "").strip()
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        pass
    match = re.search(r"\{.*\}", value, flags=re.S)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


def build_prompt(task: dict[str, Any]) -> str:
    segments = "\n\n".join(f"[{segment['role']} {segment['segment_id']}]\n{segment['text']}" for segment in task["segments"])
    return (
        "You are solving a deterministic state-carry evaluation task.\n"
        "Use only the visible task text below. Do not invent tokens or paths.\n"
        "Return JSON only. The JSON must contain:\n"
        "- final_answer.required_tokens: exactly the final active token set.\n"
        "- final_answer.allowed_paths: only currently allowed paths.\n"
        "- final_answer.state_labels: map every visible candidate token to active, revoked, stale, forbidden, protected, blocked, archive_only, rollback_only, decoy, or allowed.\n"
        "- final_answer.state_transitions: the state changes used.\n"
        "- final_answer.boundary_checks: booleans confirming no revoked, stale, forbidden, protected, blocked, archive-only, rollback-only, or decoy token/path is output.\n"
        "- final_state: an object with ACTIVE, ALW, and NO arrays for carried state.\n\n"
        f"{segments}\n\n"
        f"[final_instruction]\n{task['final_instruction']}\n"
    )


def post_once(endpoint_row: dict[str, Any], credential: str, payload: dict[str, Any], timeout: int) -> tuple[int, dict[str, str], str]:
    url = endpoint_row["base_url"].rstrip("/") + "/chat/completions"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Authorization": f"Bearer {credential}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read().decode("utf-8", errors="replace")


def run_api_row(task: dict[str, Any], oracle: dict[str, Any], endpoint_row: dict[str, Any], credential: str, scorer: Any) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    prompt = build_prompt(task)
    payload = request_payload(endpoint_row, prompt)
    request_payload_sha256 = sha256_json(payload)
    started = utc_now()
    attempts: list[dict[str, Any]] = []
    status = 0
    headers: dict[str, str] = {}
    body = ""
    for attempt_index in range(1, 3):
        attempt_started = utc_now()
        try:
            status, headers, body = post_once(endpoint_row, credential, payload, timeout=120)
            sanitized = sanitize_provider_body(body)
            attempts.append(
                {
                    "attempt_index": attempt_index,
                    "started_at_utc": attempt_started,
                    "finished_at_utc": utc_now(),
                    "http_status": status,
                    "body_sha256": sha256_text(sanitized),
                    "headers_sha256": sha256_json({key.lower(): value for key, value in headers.items() if key.lower() not in {"authorization", "set-cookie"}}),
                    "retryable_http_status": status in RETRYABLE_HTTP,
                }
            )
            if status not in RETRYABLE_HTTP:
                break
            time.sleep(2)
        except Exception as exc:  # noqa: BLE001 - preserve failure class in cassette
            attempts.append(
                {
                    "attempt_index": attempt_index,
                    "started_at_utc": attempt_started,
                    "finished_at_utc": utc_now(),
                    "transport_error": f"{type(exc).__name__}: {exc}",
                    "retryable_http_status": True,
                }
            )
            if attempt_index == 2:
                body = json.dumps({"runner_exception": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False)
            else:
                time.sleep(2)
    finished = utc_now()
    sanitized_body = sanitize_provider_body(body)
    final_output, final_state, parse_error = parse_response_content(sanitized_body)
    response_obj = parse_json_maybe(sanitized_body)
    returned_model = response_obj.get("model") if isinstance(response_obj, dict) else None
    finish_reason = None
    usage = None
    if isinstance(response_obj, dict):
        usage = response_obj.get("usage")
        try:
            finish_reason = response_obj["choices"][0].get("finish_reason")
        except Exception:
            finish_reason = None
    raw_response = {
        "final_output": final_output,
        "final_state": final_state,
        "provider_body": sanitized_body,
        "parse_error": parse_error,
    }
    metric = scorer.score_task(
        oracle,
        {
            "task_id": task["task_id"],
            "method": POLICY_ID,
            "model": endpoint_row["requested_model"],
            "budget": 0,
            "run_id": 1,
            "final_output": final_output,
            "final_state": final_state,
        },
    )
    row_id = f"{task['task_id']}::deepseek_v4pro::api_sanity::run1"
    output_row = {
        "schema_version": "pcg_dynamic_state_v2.deepseek_api_sanity_output_row.v1",
        "suite_id": SUITE_ID,
        "row_id": row_id,
        "task_id": task["task_id"],
        "task_family": task["family"],
        "task_difficulty": task["difficulty"],
        "model_condition_id": "deepseek_v4pro",
        "provider": "deepseek",
        "requested_model": endpoint_row["requested_model"],
        "selected_model_or_returned_model": returned_model,
        "returned_model_match": returned_model in {None, endpoint_row["requested_model"]},
        "method": POLICY_ID,
        "run_id": 1,
        "created_at_utc": started,
        "finished_at_utc": finished,
        "api_calls_performed": len(attempts),
        "task_manifest_entry_sha256": task["_line_sha256"],
        "oracle_entry_sha256": oracle["_line_sha256"],
        "prompt_sha256": sha256_text(prompt),
        "request_payload_sha256": request_payload_sha256,
        "raw_response_sha256": sha256_json(raw_response),
        "parsed_output_sha256": sha256_json({"final_output": final_output, "final_state": final_state}),
        "final_output": final_output,
        "final_state": final_state,
        "http_status": status,
        "finish_reason": finish_reason,
        "usage": usage,
        "score_error": parse_error,
    }
    score_row = {
        **metric,
        "schema_version": "pcg_dynamic_state_v2.deepseek_api_sanity_score_row.v1",
        "suite_id": SUITE_ID,
        "row_id": row_id,
        "task_id": task["task_id"],
        "task_family": task["family"],
        "task_difficulty": task["difficulty"],
        "model_condition_id": "deepseek_v4pro",
        "provider": "deepseek",
        "requested_model": endpoint_row["requested_model"],
        "selected_model_or_returned_model": returned_model,
        "returned_model_match": returned_model in {None, endpoint_row["requested_model"]},
        "method": POLICY_ID,
        "run_id": 1,
        "created_at_utc": started,
        "api_calls_performed": len(attempts),
        "http_status": status,
        "finish_reason": finish_reason,
        "score_error": parse_error,
        "prompt_sha256": output_row["prompt_sha256"],
        "request_payload_sha256": request_payload_sha256,
        "raw_response_sha256": output_row["raw_response_sha256"],
        "parsed_output_sha256": output_row["parsed_output_sha256"],
        "metric_record_sha256": sha256_json(metric),
        "score_record_sha256": sha256_json({"metric": metric, "raw_response_sha256": output_row["raw_response_sha256"]}),
    }
    cassette_row = {
        "schema_version": "pcg_dynamic_state_v2.deepseek_api_sanity_cassette_row.v1",
        "suite_id": SUITE_ID,
        "row_id": row_id,
        "task_id": task["task_id"],
        "model_condition_id": "deepseek_v4pro",
        "provider": "deepseek",
        "requested_model": endpoint_row["requested_model"],
        "method": POLICY_ID,
        "prompt_sha256": output_row["prompt_sha256"],
        "request_payload_sha256": request_payload_sha256,
        "raw_response": raw_response,
        "raw_response_sha256": output_row["raw_response_sha256"],
        "provider_metadata": {
            "started_at_utc": started,
            "finished_at_utc": finished,
            "attempts": attempts,
            "http_status": status,
            "returned_model": returned_model,
            "finish_reason": finish_reason,
            "usage": usage,
            "api_key_env": endpoint_row["api_key_env"],
            "api_key_value_stored": False,
        },
    }
    return output_row, score_row, cassette_row


def environment_record(max_workers: int) -> dict[str, Any]:
    system = platform.system() or "UnknownOS"
    machine = platform.machine() or "unknown-arch"
    return {
        "schema_version": "pcg_dynamic_state_v2.deepseek_api_sanity_environment.v1",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": f"{system}-{machine}",
        "implementation": platform.python_implementation(),
        "max_workers": max_workers,
    }


def aggregate(rows: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(tuple(row[key] for key in keys), []).append(row)
    out = []
    for group_key, group_rows in sorted(groups.items(), key=lambda item: tuple(str(part) for part in item[0])):
        n = len(group_rows)
        answer = sum(bool(row["answer_success"]) for row in group_rows)
        governance = sum(bool(row["state_governance_success"]) for row in group_rows)
        co_success = sum(bool(row["reliable_composite_success"]) for row in group_rows)
        record = {key: value for key, value in zip(keys, group_key)}
        record.update(
            {
                "n": n,
                "answer_success_count": answer,
                "answer_success_rate": round(answer / n, 6) if n else 0.0,
                "state_governance_success_count": governance,
                "state_governance_success_rate": round(governance / n, 6) if n else 0.0,
                "co_success_count": co_success,
                "co_success_rate": round(co_success / n, 6) if n else 0.0,
            }
        )
        out.append(record)
    return out


def build_config(started_at_utc: str, max_workers: int) -> dict[str, Any]:
    endpoint_row = endpoint()
    return {
        "schema_version": "pcg_dynamic_state_v2.deepseek_api_sanity_config.v1",
        "suite_id": SUITE_ID,
        "created_at_utc": started_at_utc,
        "matrix_role": "diagnostic_api_sanity_not_primary",
        "primary_analysis_eligible": False,
        "task_count": 40,
        "rows": 40,
        "max_workers": max_workers,
        "model_condition_id": "deepseek_v4pro",
        "provider": "deepseek",
        "requested_model": endpoint_row["requested_model"],
        "openrouter_used": False,
        "api_key_env": endpoint_row["api_key_env"],
        "api_key_value_stored": False,
        "request_controls": endpoint_row["request_controls"],
        "visible_task_manifest": {"path": rel(VISIBLE_TASK_MANIFEST), "sha256": file_sha256(VISIBLE_TASK_MANIFEST)},
        "oracle_manifest": {"path": rel(ORACLE_MANIFEST), "sha256": file_sha256(ORACLE_MANIFEST)},
        "provider_snapshot": {"path": rel(PROVIDER_SNAPSHOT), "sha256": file_sha256(PROVIDER_SNAPSHOT)},
        "scorer": {"path": rel(SCORER_PATH), "sha256": file_sha256(SCORER_PATH)},
        "runner": {"path": rel(SCRIPT_PATH), "sha256": file_sha256(SCRIPT_PATH)},
        "boundary": "Diagnostic learned-policy sanity, not a primary matrix condition.",
    }


def write_report(out_dir: Path, summary: dict[str, Any]) -> None:
    rows = summary["by_policy"]
    lines = [
        "# DeepSeek V4-Pro API Sanity Report",
        "",
        f"- suite_id: `{summary['suite_id']}`",
        f"- created_at_utc: `{summary['created_at_utc']}`",
        f"- model: `{summary['requested_model']}`",
        f"- rows: `{summary['rows']}`",
        f"- api_calls_performed: `{summary['api_calls_performed']}`",
        f"- max_workers: `{summary['max_workers']}`",
        "- boundary: diagnostic learned-policy sanity, not primary matrix evidence",
        "",
        "| policy | n | answer | governance | co-success |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {policy} | {n} | {a:.2%} | {g:.2%} | {r:.2%} |".format(
                policy=row["method"],
                n=row["n"],
                a=row["answer_success_rate"],
                g=row["state_governance_success_rate"],
                r=row["co_success_rate"],
            )
        )
    lines.append("")
    (out_dir / "DEEPSEEK_API_SANITY_REPORT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def manifest_row(path: Path, artifact_id: str, artifact_type: str, created_utc: str, parent_hashes: list[str], notes: str) -> dict[str, Any]:
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    digest = file_sha256(path)
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "path": rel(path),
        "sha256": digest,
        "canonical_sha256": digest,
        "size_bytes": stat.st_size,
        "mtime_utc": mtime,
        "created_utc": created_utc,
        "git_commit": None,
        "produced_by_run": SUITE_ID,
        "consumed_by_runs": [SUITE_ID],
        "parent_artifact_hashes": parent_hashes,
        "child_artifact_hashes": [],
        "notes": notes,
    }


def current_git_commit() -> str | None:
    head = ROOT / ".git" / "HEAD"
    if not head.exists():
        return None
    text = head.read_text(encoding="utf-8").strip()
    if text.startswith("ref: "):
        ref_path = ROOT / ".git" / text.split(" ", 1)[1]
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
    return text if text else None


def refresh_metadata_only(out_dir: Path) -> dict[str, Any]:
    if not out_dir.exists():
        raise SystemExit(f"missing DeepSeek API sanity directory: {out_dir}")

    summary_path = out_dir / "deepseek_api_sanity_summary.json"
    config_path = out_dir / "deepseek_api_sanity_config.json"
    if not summary_path.exists() or not config_path.exists():
        raise SystemExit("missing DeepSeek API sanity summary/config for metadata-only refresh")

    summary = read_json(summary_path)
    config = read_json(config_path)
    max_workers = int(summary.get("max_workers") or config.get("max_workers") or 10)
    created_utc = str(summary.get("created_at_utc") or config.get("created_at_utc") or utc_now())
    files = {
        "config": config_path,
        "environment": out_dir / "environment.json",
        "outputs": out_dir / "deepseek_api_sanity_outputs.jsonl",
        "scores": out_dir / "deepseek_api_sanity_scores.jsonl",
        "scores_csv": out_dir / "deepseek_api_sanity_scores.csv",
        "cassette": out_dir / "deepseek_v4pro_api_sanity.cassette.jsonl",
        "summary": summary_path,
        "summary_csv": out_dir / "deepseek_api_sanity_summary_by_policy.csv",
        "summary_family": out_dir / "deepseek_api_sanity_summary_by_family_difficulty.csv",
        "report": out_dir / "DEEPSEEK_API_SANITY_REPORT.md",
    }
    write_json(files["environment"], environment_record(max_workers))
    write_report(out_dir, summary)
    write_hash_manifest(out_dir, created_utc, files)
    return {
        "passed": True,
        "mode": "metadata_only_refresh",
        "suite_id": SUITE_ID,
        "api_calls_performed": 0,
        "refreshed_files": [
            rel(files["environment"]),
            rel(files["report"]),
            rel(out_dir / "HASH_MANIFEST.jsonl"),
        ],
    }


def write_hash_manifest(out_dir: Path, created_utc: str, files: dict[str, Path]) -> None:
    parent_hashes = [file_sha256(VISIBLE_TASK_MANIFEST), file_sha256(ORACLE_MANIFEST), file_sha256(PROVIDER_SNAPSHOT), file_sha256(SCORER_PATH), file_sha256(SCRIPT_PATH)]
    rows = [
        manifest_row(VISIBLE_TASK_MANIFEST, "visible_task_manifest", "dataset", created_utc, [], "Model-visible task manifest."),
        manifest_row(ORACLE_MANIFEST, "scorer_oracle_manifest", "dataset", created_utc, [], "Scorer-only oracle manifest."),
        manifest_row(PROVIDER_SNAPSHOT, "provider_snapshot", "config", created_utc, [], "Frozen provider endpoint snapshot."),
        manifest_row(SCORER_PATH, "strict_main_matrix_scorer", "eval_harness", created_utc, [], "Strict deterministic scorer."),
        manifest_row(SCRIPT_PATH, "deepseek_api_sanity_runner", "eval_harness", created_utc, [], "DeepSeek API sanity runner."),
    ]
    types = {
        "config": "config",
        "environment": "environment",
        "outputs": "parsed_output",
        "scores": "metric",
        "scores_csv": "metric",
        "cassette": "api_log",
        "summary": "metric",
        "summary_csv": "metric",
        "summary_family": "metric",
        "report": "manifest",
    }
    for artifact_id, path in files.items():
        rows.append(manifest_row(path, artifact_id, types.get(artifact_id, "manifest"), created_utc, parent_hashes, "Generated by DeepSeek v4-pro API sanity runner."))
    write_jsonl(out_dir / "HASH_MANIFEST.jsonl", rows)


def record(out_dir: Path, env_file: Path | None, max_workers: int) -> dict[str, Any]:
    load_env_file(env_file)
    endpoint_row = endpoint()
    credential = os.environ.get(endpoint_row["api_key_env"], "")
    if not credential:
        raise SystemExit(f"{endpoint_row['api_key_env']} not found in environment or env file")
    if endpoint_row["requested_model"] != "deepseek-v4-pro":
        raise SystemExit("refusing to run a model other than deepseek-v4-pro")
    started = utc_now()
    visible_tasks = [{key: value for key, value in row.items() if not key.startswith("_")} | {"_line_sha256": row["_line_sha256"]} for row in read_jsonl(VISIBLE_TASK_MANIFEST)]
    oracle_by_id = {row["task_id"]: {key: value for key, value in row.items() if not key.startswith("_")} | {"_line_sha256": row["_line_sha256"]} for row in read_jsonl(ORACLE_MANIFEST)}
    scorer = load_module(SCORER_PATH, "pcg_dynamic_state_v2_main_matrix_scorer")
    output_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    cassette_rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(run_api_row, task, oracle_by_id[task["task_id"]], endpoint_row, credential, scorer): task["task_id"]
            for task in visible_tasks
        }
        completed = 0
        for future in as_completed(futures):
            output_row, score_row, cassette_row = future.result()
            output_rows.append(output_row)
            score_rows.append(score_row)
            cassette_rows.append(cassette_row)
            completed += 1
            if completed == 1 or completed % 10 == 0 or completed == len(futures):
                print(canonical_json({"mode": "deepseek_api_sanity_progress", "completed": completed, "total": len(futures)}), flush=True)
    output_rows.sort(key=lambda row: row["row_id"])
    score_rows.sort(key=lambda row: row["row_id"])
    cassette_rows.sort(key=lambda row: row["row_id"])
    by_policy = aggregate(score_rows, ["method"])
    by_family_difficulty = aggregate(score_rows, ["method", "task_family", "task_difficulty"])
    api_calls = sum(int(row.get("api_calls_performed", 0) or 0) for row in score_rows)
    config = build_config(started, max_workers)
    environment = environment_record(max_workers)
    summary = {
        "schema_version": "pcg_dynamic_state_v2.deepseek_api_sanity_summary.v1",
        "suite_id": SUITE_ID,
        "created_at_utc": started,
        "rows": len(score_rows),
        "api_calls_performed": api_calls,
        "max_workers": max_workers,
        "model_condition_id": "deepseek_v4pro",
        "provider": "deepseek",
        "requested_model": "deepseek-v4-pro",
        "primary_analysis_eligible": False,
        "by_policy": by_policy,
    }
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "config": out_dir / "deepseek_api_sanity_config.json",
        "environment": out_dir / "environment.json",
        "outputs": out_dir / "deepseek_api_sanity_outputs.jsonl",
        "scores": out_dir / "deepseek_api_sanity_scores.jsonl",
        "scores_csv": out_dir / "deepseek_api_sanity_scores.csv",
        "cassette": out_dir / "deepseek_v4pro_api_sanity.cassette.jsonl",
        "summary": out_dir / "deepseek_api_sanity_summary.json",
        "summary_csv": out_dir / "deepseek_api_sanity_summary_by_policy.csv",
        "summary_family": out_dir / "deepseek_api_sanity_summary_by_family_difficulty.csv",
        "report": out_dir / "DEEPSEEK_API_SANITY_REPORT.md",
    }
    write_json(files["config"], config)
    write_json(files["environment"], environment)
    write_jsonl(files["outputs"], output_rows)
    write_jsonl(files["scores"], score_rows)
    write_csv(files["scores_csv"], score_rows)
    write_jsonl(files["cassette"], cassette_rows)
    write_json(files["summary"], summary)
    write_csv(files["summary_csv"], by_policy)
    write_csv(files["summary_family"], by_family_difficulty)
    write_report(out_dir, summary)
    write_hash_manifest(out_dir, started, files)
    return summary


def replay_from_cassette(out_dir: Path) -> dict[str, Any]:
    if not out_dir.exists():
        raise SystemExit(f"missing DeepSeek API sanity directory: {out_dir}")
    oracle_by_id = {row["task_id"]: {key: value for key, value in row.items() if not key.startswith("_")} for row in read_jsonl(ORACLE_MANIFEST)}
    scorer = load_module(SCORER_PATH, "pcg_dynamic_state_v2_main_matrix_scorer")
    cassette_rows = read_jsonl(out_dir / "deepseek_v4pro_api_sanity.cassette.jsonl")
    expected_scores = read_jsonl(out_dir / "deepseek_api_sanity_scores.jsonl")
    observed_scores = []
    for cassette in cassette_rows:
        raw = cassette["raw_response"]
        task_id = cassette["task_id"]
        metric = scorer.score_task(
            oracle_by_id[task_id],
            {
                "task_id": task_id,
                "method": POLICY_ID,
                "model": "deepseek-v4-pro",
                "budget": 0,
                "run_id": 1,
                "final_output": raw.get("final_output", ""),
                "final_state": raw.get("final_state", ""),
            },
        )
        observed_scores.append(
            {
                **metric,
                "row_id": cassette["row_id"],
                "task_id": task_id,
                "metric_record_sha256": sha256_json(metric),
                "raw_response_sha256": cassette["raw_response_sha256"],
            }
        )
    expected_by_id = {row["row_id"]: row for row in expected_scores}
    failures: list[str] = []
    for observed in observed_scores:
        expected = expected_by_id.get(observed["row_id"])
        if expected is None:
            failures.append(f"missing expected score row {observed['row_id']}")
            continue
        for key in [
            "answer_success",
            "state_governance_success",
            "reliable_composite_success",
            "required_token_recall",
            "metric_record_sha256",
            "raw_response_sha256",
        ]:
            if expected.get(key) != observed.get(key):
                failures.append(f"{observed['row_id']} field {key}: expected={expected.get(key)!r} observed={observed.get(key)!r}")
                if len(failures) >= 20:
                    break
        if len(failures) >= 20:
            break
    failures.extend(validate_hash_manifest(out_dir)[: max(0, 20 - len(failures))])
    return {
        "passed": not failures,
        "suite_id": SUITE_ID,
        "rows_replayed": len(observed_scores),
        "api_calls_performed": 0,
        "failure_count": len(failures),
        "failures": failures,
    }


def validate_hash_manifest(out_dir: Path) -> list[str]:
    manifest = out_dir / "HASH_MANIFEST.jsonl"
    if not manifest.exists():
        return ["missing HASH_MANIFEST.jsonl"]
    failures: list[str] = []
    required = {
        "config",
        "environment",
        "outputs",
        "scores",
        "scores_csv",
        "cassette",
        "summary",
        "summary_csv",
        "summary_family",
        "report",
    }
    seen: set[str] = set()
    for row in read_jsonl(manifest):
        artifact_id = str(row.get("artifact_id", ""))
        seen.add(artifact_id)
        path_value = row.get("path")
        if not path_value:
            failures.append(f"manifest row {artifact_id or '<missing>'} has no path")
            continue
        path = ROOT / str(path_value)
        if not path.exists():
            failures.append(f"manifest row {artifact_id} points to missing file {path_value}")
            continue
        digest = file_sha256(path)
        if artifact_id == "deepseek_api_sanity_runner":
            continue
        if digest != row.get("sha256"):
            failures.append(f"manifest row {artifact_id} sha256 mismatch: expected={row.get('sha256')} observed={digest}")
        if len(failures) >= 20:
            break
    missing = sorted(required - seen)
    if missing:
        failures.append(f"manifest missing artifact ids: {missing}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--refresh-metadata-only", action="store_true")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--max-workers", type=int, default=10)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    if sum([bool(args.record), bool(args.check), bool(args.refresh_metadata_only)]) != 1:
        parser.error("use exactly one of --record, --check, or --refresh-metadata-only")
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if args.record:
        summary = record(out_dir, args.env_file, args.max_workers)
        print(canonical_json({"passed": True, **summary}))
        return 0
    result = refresh_metadata_only(out_dir) if args.refresh_metadata_only else replay_from_cassette(out_dir)
    print(canonical_json(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
