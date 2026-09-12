#!/usr/bin/env python3
"""Run per-model benchmark admission smoke under the frozen main-matrix policy."""

from __future__ import annotations

import argparse
import copy
import csv
import email.utils
import hashlib
import importlib.util
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATE = "20260626"
FREEZE_DATE = "20260625"
ADMISSION_DIR = ROOT / "artifact/protocol/main_matrix/admission"
OUT_ROOT = ADMISSION_DIR / f"benchmark_smoke_{DATE}"
CONFIRMATORY_CONFIG = ROOT / "artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625.json"
DIAGNOSTIC_CONFIG = ROOT / "artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_budget300_diagnostic_40task_5model_4method_1budget_1run_20260625.json"
PROVIDER_SNAPSHOT = ADMISSION_DIR / f"PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_{FREEZE_DATE.replace('-', '')}.json"
VARIABLE_FREEZE_SPEC = ADMISSION_DIR / f"VARIABLE_FREEZE_SPEC_{FREEZE_DATE.replace('-', '')}.yaml"
MODEL_ADMISSION_CRITERIA = ADMISSION_DIR / "MODEL_ADMISSION_CRITERIA_20260626.md"
VISIBLE_TASKS = ROOT / "artifact/results/evidence/ssr_downgrade_20260623/data/pcg_dynamic_state_v2/main_matrix_v1/MODEL_VISIBLE_TASK_MANIFEST.jsonl"
ORACLE_TASKS = ROOT / "artifact/results/evidence/ssr_downgrade_20260623/data/pcg_dynamic_state_v2/main_matrix_v1/SCORER_ORACLE_MANIFEST.jsonl"
SCORER_PATH = ROOT / "artifact/results/evidence/ssr_downgrade_20260623/tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_main_matrix.py"

ENV_CANDIDATES = [
    ROOT / ".env",
    ROOT / ".env.local",
    ROOT / ".env.save",
]

RETRYABLE_HTTP = {408, 409, 425, 429, 500, 502, 503, 504}
DEFAULT_RETRY_POLICY = {
    "schema_version": "pcg_dynamic_state_v2.transport_retry_policy.v1",
    "policy_id": "frozen_two_attempt_policy_20260625",
    "max_transport_attempts": 2,
    "retryable_http_statuses": sorted(RETRYABLE_HTTP),
    "backoff_seconds": [2.0],
    "respect_retry_after": False,
    "max_sleep_seconds": 2.0,
}
OPENROUTER_RUNTIME_HARDENING_RETRY_POLICY = {
    "schema_version": "pcg_dynamic_state_v2.transport_retry_policy.v1",
    "policy_id": "openrouter_post_pause_bounded_backoff_20260627",
    "max_transport_attempts": 5,
    "retryable_http_statuses": [408, 429, 500, 502, 503, 504],
    "backoff_seconds": [2.0, 4.0, 8.0, 16.0],
    "respect_retry_after": True,
    "max_sleep_seconds": 180.0,
}
OPENROUTER_PROVIDER_ORDER_BY_CONDITION = {
    "openrouter_gpt55": ["openai"],
    "openrouter_claude48": ["anthropic"],
}
LOCAL_TRANSPORT_PATH_FAILURE_CLASS = "confirmed_local_transport_path_failure"
OPENROUTER_TRANSPORT_HALT_CLASSES = {
    LOCAL_TRANSPORT_PATH_FAILURE_CLASS,
    "transport_timeout",
    "remote_disconnected",
    "transport_error",
}
CONFIRMATORY_METHODS = [
    "loop_only",
    "rolling_summary",
    "rolling_visible_carry_forward",
    "rolling_visible_fields_only",
    "ssr_no_visible_carry",
    "mature_ssr_loop",
]
DIAGNOSTIC_METHODS = [
    "rolling_summary",
    "ssr_no_visible_carry",
    "rolling_visible_carry_forward",
    "mature_ssr_loop",
]
NEUTRAL_TOKEN_RE = re.compile(r"\b(?:REQ|CFG|API|MOD|PATH|FEATURE|FLAG|RULE|PATCH|HOOK|JOB|CHECK)_[0-9]{2}_[A-Z0-9]{6}\b")
PATH_RE = re.compile(r"\bsrc/[A-Za-z0-9_./-]+(?:\.py|\.yaml|\.json|\.md)\b")
STATE_FIELD_RE = re.compile(
    r"(OUT|ALW|ALLOW|ACTIVE_SET|ACTIVE|REQUIRED_TOKENS|REQUIRED|VISIBLE_KEEP|KEEP|OUTPUT_SET|OUTPUT|FINAL_ACTIVE_SET|FINAL_ACTIVE|FINAL|CARRY_ALL|NO_CAT|NO|DENIED|DENY|EXCLUDED|EXCLUDE|FORBIDDEN|PROTECTED|REVOKED|STALE|BLOCKED|BOUNDARY_CHECKS|BOUNDARY|BOUND|B|NOTES|NOTE|CHECKS|CHECK|CK|STATE_LABELS|STATE_TRANSITIONS|LOOP|G|N)\s*=",
    flags=re.I,
)
_PROVIDER_CALL_PACING_LOCK = threading.Lock()
_PROVIDER_CALL_PACING_SECONDS = 0.0
_PROVIDER_CALL_PACING_LAST_AT: dict[str, float] = {}


class LocalTransportPathFailure(RuntimeError):
    """Raised when the local HTTP transport-path fails before provider contact."""

    def __init__(self, message: str, *, attempts: list[dict[str, Any]], retry_policy: dict[str, Any], retry_policy_sha256: str) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.retry_policy = retry_policy
        self.retry_policy_sha256 = retry_policy_sha256


def configure_provider_call_pacing(interval_seconds: float) -> None:
    """Set a process-local minimum interval between actual provider attempts."""
    global _PROVIDER_CALL_PACING_SECONDS
    if interval_seconds < 0:
        raise ValueError("provider call interval must be >= 0")
    with _PROVIDER_CALL_PACING_LOCK:
        _PROVIDER_CALL_PACING_SECONDS = float(interval_seconds)
        _PROVIDER_CALL_PACING_LAST_AT.clear()


def provider_call_pacing_wait(endpoint: dict[str, Any]) -> dict[str, Any]:
    """Reserve and wait for the next provider-call slot.

    The runner submits rows concurrently, but each row can still make several
    sequential provider calls. This process-local throttle paces actual HTTP
    attempts, including retries, before they reach the provider.
    """
    interval = _PROVIDER_CALL_PACING_SECONDS
    if interval <= 0:
        return {
            "enabled": False,
            "interval_seconds": 0.0,
            "waited_seconds": 0.0,
        }
    key = "global_provider_call"
    with _PROVIDER_CALL_PACING_LOCK:
        now = time.monotonic()
        earliest = _PROVIDER_CALL_PACING_LAST_AT.get(key, now)
        scheduled = max(now, earliest)
        _PROVIDER_CALL_PACING_LAST_AT[key] = scheduled + interval
        wait_seconds = max(0.0, scheduled - now)
    if wait_seconds > 0:
        time.sleep(wait_seconds)
    return {
        "enabled": True,
        "scope": key,
        "interval_seconds": interval,
        "waited_seconds": round(wait_seconds, 3),
        "provider": endpoint.get("provider"),
        "openrouter_used": bool(endpoint.get("openrouter_used")),
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
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
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_env_files() -> None:
    for path in ENV_CANDIDATES:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            text = line.strip()
            if not text or text.startswith("#") or "=" not in text:
                continue
            key, value = text.split("=", 1)
            key = key.strip().removeprefix("export ").strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def task_maps() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    return (
        {row["task_id"]: row for row in read_jsonl(VISIBLE_TASKS)},
        {row["task_id"]: row for row in read_jsonl(ORACLE_TASKS)},
    )


def endpoint_by_condition() -> dict[str, dict[str, Any]]:
    snapshot = read_json(PROVIDER_SNAPSHOT)
    return {endpoint["condition_id"]: endpoint for endpoint in snapshot["endpoints"]}


def apply_openrouter_runtime_hardening(endpoint: dict[str, Any]) -> dict[str, Any]:
    """Return a clean-v2 OpenRouter endpoint copy with explicit transport controls.

    This is intentionally opt-in. It is for the clean-v2 OpenRouter GPT/Claude
    namespace after the 2026-06-27 OpenRouter execution-site transport pauses,
    not a retroactive rewrite of existing recorded rows.
    """
    if not endpoint.get("openrouter_used"):
        return copy.deepcopy(endpoint)
    patched = copy.deepcopy(endpoint)
    controls = patched.setdefault("request_controls", {})
    provider_value = copy.deepcopy(controls.get("provider", {}).get("value", {}))
    provider_value["allow_fallbacks"] = False
    provider_value["require_parameters"] = True
    provider_value["order"] = OPENROUTER_PROVIDER_ORDER_BY_CONDITION.get(
        patched.get("condition_id"),
        [str(patched.get("provider_route_hint") or "").lower()],
    )
    provider_value["order"] = [item for item in provider_value["order"] if item]
    controls["provider"] = {"send_mode": "explicit", "value": provider_value}
    controls["plugins"] = {
        "send_mode": "explicit",
        "value": [{"id": "context-compression", "enabled": False}],
    }
    controls["openrouter_metadata_header"] = {"send_mode": "explicit", "value": "enabled"}
    controls["retry_policy"] = copy.deepcopy(OPENROUTER_RUNTIME_HARDENING_RETRY_POLICY)
    controls["local_transport_path_failure_guard"] = {
        "send_mode": "local_guard",
        "value": {
            "enabled": True,
            "action": "halt_slice_without_retry",
            "failure_class": LOCAL_TRANSPORT_PATH_FAILURE_CLASS,
            "trigger": "any pre-HTTP local transport exception classified by the runner",
            "halt_classes": sorted(OPENROUTER_TRANSPORT_HALT_CLASSES),
        },
    }
    patched["openrouter_runtime_hardening"] = {
        "applied": True,
        "policy_id": "openrouter_clean_v2_runtime_hardening_20260627",
        "scope": "openrouter_clean_v2_from_zero",
        "does_not_rewrite_existing_rows": True,
        "official_docs": [
            "https://openrouter.ai/docs/guides/routing/provider-selection.md",
            "https://openrouter.ai/docs/guides/features/message-transforms.md",
            "https://openrouter.ai/docs/api/reference/errors-and-debugging.md",
            "https://openrouter.ai/docs/api/reference/limits.md",
        ],
    }
    return patched


def rows_from_config(config_path: Path, model_condition: str, methods: list[str], budgets: list[int], task_id: str) -> list[dict[str, Any]]:
    config = read_json(config_path)
    rows_path = ROOT / config["row_manifest"]["path"]
    rows = []
    for row in read_jsonl(rows_path):
        if (
            row["model_condition_id"] == model_condition
            and row["task_id"] == task_id
            and row["method"] in methods
            and row["budget"] in budgets
            and row["run_id"] == 1
        ):
            copied = dict(row)
            copied["source_experiment_id"] = copied["experiment_id"]
            copied["source_matrix_role"] = copied["matrix_role"]
            copied["experiment_id"] = f"pcg_dynamic_state_v2_benchmark_admission_smoke_{DATE}"
            copied["matrix_role"] = "admission_benchmark_smoke_not_primary"
            copied["primary_analysis_eligible"] = False
            copied["global_artifact_id"] = f"{copied['experiment_id']}::{copied['row_id']}"
            rows.append(copied)
    expected = len(methods) * len(budgets)
    if len(rows) != expected:
        raise SystemExit(f"{model_condition}: expected {expected} rows from {config_path.name}, observed {len(rows)}")
    rows.sort(key=lambda item: (item["task_id"], item["model_condition_id"], item["method"], item["budget"], item["run_id"]))
    for index, row in enumerate(rows, start=1):
        row["admission_row_index"] = index
    return rows


def build_smoke_config(model_condition: str, rows: list[dict[str, Any]], out_dir: Path, role: str) -> Path:
    rows_path = out_dir / f"{model_condition}_{role}.rows.jsonl"
    write_jsonl(rows_path, rows)
    config = {
        "schema_version": "pcg_dynamic_state_v2.benchmark_admission_smoke_config.v1",
        "experiment_id": f"pcg_dynamic_state_v2_benchmark_admission_smoke_{DATE}",
        "created_at_utc": utc_now(),
        "matrix_role": "admission_benchmark_smoke_not_primary",
        "primary_analysis_eligible": False,
        "model_condition_id": model_condition,
        "role": role,
        "matrix_shape": {
            "expected_rows": len(rows),
            "tasks": len({row["task_id"] for row in rows}),
            "models": 1,
            "methods": len({row["method"] for row in rows}),
            "budgets": len({row["budget"] for row in rows}),
            "runs": 1,
        },
        "row_manifest": {"path": rel(rows_path), "sha256": file_sha256(rows_path)},
        "source_configs": [rel(CONFIRMATORY_CONFIG), rel(DIAGNOSTIC_CONFIG)],
        "variable_freeze_spec": {"path": rel(VARIABLE_FREEZE_SPEC), "sha256": file_sha256(VARIABLE_FREEZE_SPEC)},
        "model_admission_criteria": {"path": rel(MODEL_ADMISSION_CRITERIA), "sha256": file_sha256(MODEL_ADMISSION_CRITERIA)},
        "scorer": {"path": rel(SCORER_PATH), "sha256": file_sha256(SCORER_PATH)},
        "runner": {"path": rel(Path(__file__).resolve()), "sha256": file_sha256(Path(__file__).resolve())},
    }
    config_path = out_dir / f"{model_condition}_{role}.json"
    write_json(config_path, config)
    return config_path


def payload_for(endpoint: dict[str, Any], prompt: str) -> dict[str, Any]:
    controls = endpoint["request_controls"]
    payload: dict[str, Any] = {
        "model": endpoint["requested_model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if "max_tokens" in controls:
        payload["max_tokens"] = controls["max_tokens"]
    temp = controls.get("temperature", {})
    if temp.get("send_mode") == "explicit":
        payload["temperature"] = temp.get("value")
    if endpoint.get("openrouter_used"):
        payload["provider"] = controls.get("provider", {}).get("value", {"allow_fallbacks": False})
        plugins = controls.get("plugins", {})
        if plugins.get("send_mode") == "explicit":
            payload["plugins"] = plugins.get("value", [])
    reasoning = controls.get("reasoning_or_thinking", {})
    if reasoning.get("send_mode") == "explicit" and isinstance(reasoning.get("value"), dict):
        payload.update(reasoning["value"])
    return payload


def request_headers(endpoint: dict[str, Any], credential: str) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {credential}", "Content-Type": "application/json"}
    if endpoint.get("openrouter_used"):
        headers.update(
            {
                "HTTP-Referer": "https://anonymous-review-artifact.local",
                "X-Title": "pcg-dynamic-state-v2-benchmark-admission",
            }
        )
        metadata_header = endpoint.get("request_controls", {}).get("openrouter_metadata_header", {})
        if metadata_header.get("send_mode") == "explicit" and metadata_header.get("value"):
            headers["X-OpenRouter-Metadata"] = str(metadata_header["value"])
    return headers


def post_chat_completion(endpoint: dict[str, Any], credential: str, payload: dict[str, Any]) -> tuple[int, dict[str, str], str]:
    url = endpoint["base_url"].rstrip("/") + "/chat/completions"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = request_headers(endpoint, credential)
    timeout = int(endpoint.get("request_controls", {}).get("request_timeout_seconds", 120))
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read().decode("utf-8", errors="replace")


def sanitize_provider_body(body: str) -> str:
    """Redact provider response ids while preserving deterministic audit hashes.

    OpenRouter generation ids can contain arbitrary base62 substrings. Those
    substrings may accidentally match local anonymity patterns, so the artifact
    stores a stable digest instead of raw provider id strings.
    """
    try:
        parsed = json.loads(body)
    except Exception:
        return body

    def scrub(value: Any) -> Any:
        if isinstance(value, dict):
            out: dict[str, Any] = {}
            for key, item in value.items():
                if key.lower() in {"id", "generation_id"} and isinstance(item, str):
                    out[key] = f"redacted:{sha256_bytes(item.encode('utf-8'))[:16]}"
                else:
                    out[key] = scrub(item)
            return out
        if isinstance(value, list):
            return [scrub(item) for item in value]
        return value

    return json.dumps(scrub(parsed), ensure_ascii=False, sort_keys=True)


def classify_transport_failure(error_type: str | None, message: str | None) -> str:
    text = str(message or "")
    lowered = text.lower()
    if "tunnel connection failed" in lowered and ("503" in lowered or "service unavailable" in lowered):
        return LOCAL_TRANSPORT_PATH_FAILURE_CLASS
    if error_type == "TimeoutError" or "timed out" in lowered:
        return "transport_timeout"
    if error_type == "RemoteDisconnected" or "remote end closed connection" in lowered:
        return "remote_disconnected"
    return "transport_error"


def sanitize_transport_message(message: str | None) -> str:
    text = str(message or "")
    text = re.sub(r"https?://[^\s)]+", "[redacted-url]", text)
    text = re.sub(r"\b(?:127\.0\.0\.1|0\.0\.0\.0|localhost):\d+\b", "[redacted-local-endpoint]", text)
    return text


def local_transport_path_failure_guard_enabled(endpoint: dict[str, Any]) -> bool:
    guard = endpoint.get("request_controls", {}).get("local_transport_path_failure_guard", {})
    value = guard.get("value") if isinstance(guard, dict) else None
    if isinstance(value, dict):
        return bool(value.get("enabled"))
    return False


def transport_halt_classes(endpoint: dict[str, Any]) -> set[str]:
    guard = endpoint.get("request_controls", {}).get("local_transport_path_failure_guard", {})
    value = guard.get("value") if isinstance(guard, dict) else None
    if isinstance(value, dict) and value.get("halt_classes") is not None:
        return {str(item) for item in value.get("halt_classes", [])}
    return set(OPENROUTER_TRANSPORT_HALT_CLASSES)


def attempt_failure_class(attempt: dict[str, Any]) -> str | None:
    if attempt.get("failure_class"):
        return str(attempt["failure_class"])
    if attempt.get("transport_error"):
        return classify_transport_failure(str(attempt.get("transport_error")), str(attempt.get("message") or ""))
    return None


def raw_has_local_transport_path_failure(raw: dict[str, Any]) -> bool:
    return any(attempt_failure_class(attempt) == LOCAL_TRANSPORT_PATH_FAILURE_CLASS for attempt in raw.get("attempts", []))


def retry_policy_for(endpoint: dict[str, Any]) -> dict[str, Any]:
    policy = copy.deepcopy(DEFAULT_RETRY_POLICY)
    override = endpoint.get("request_controls", {}).get("retry_policy")
    if isinstance(override, dict):
        policy.update(copy.deepcopy(override))
    policy["max_transport_attempts"] = max(1, int(policy.get("max_transport_attempts", 1)))
    policy["retryable_http_statuses"] = [int(item) for item in policy.get("retryable_http_statuses", [])]
    policy["backoff_seconds"] = [float(item) for item in policy.get("backoff_seconds", [])] or [0.0]
    policy["max_sleep_seconds"] = float(policy.get("max_sleep_seconds", max(policy["backoff_seconds"])))
    policy["respect_retry_after"] = bool(policy.get("respect_retry_after"))
    return policy


def header_value(headers: dict[str, str], name: str) -> str | None:
    lowered = name.lower()
    for key, value in headers.items():
        if key.lower() == lowered:
            return value
    return None


def parse_retry_after_seconds(headers: dict[str, str]) -> float | None:
    value = header_value(headers, "Retry-After")
    if not value:
        return None
    stripped = str(value).strip()
    try:
        seconds = float(stripped)
        return seconds if seconds >= 0 else None
    except ValueError:
        pass
    try:
        retry_at = email.utils.parsedate_to_datetime(stripped)
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
    except Exception:
        return None


def retry_sleep_seconds(policy: dict[str, Any], attempt_index: int, retry_after_seconds: float | None) -> float:
    backoff = policy["backoff_seconds"]
    planned = backoff[min(attempt_index - 1, len(backoff) - 1)]
    if policy.get("respect_retry_after") and retry_after_seconds is not None:
        planned = max(planned, retry_after_seconds)
    return min(float(planned), float(policy["max_sleep_seconds"]))


def request_with_retry(endpoint: dict[str, Any], credential: str, payload: dict[str, Any]) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    policy = retry_policy_for(endpoint)
    retryable_http = set(policy["retryable_http_statuses"])
    max_attempts = int(policy["max_transport_attempts"])
    for attempt_index in range(1, max_attempts + 1):
        started = utc_now()
        pacing = provider_call_pacing_wait(endpoint)
        try:
            status, headers, body = post_chat_completion(endpoint, credential, payload)
            body = sanitize_provider_body(body)
            retry_after = parse_retry_after_seconds(headers)
            attempt = {
                "attempt_index": attempt_index,
                "started_at_utc": started,
                "finished_at_utc": utc_now(),
                "http_status": status,
                "headers_sha256": sha256_json(headers),
                "body": body,
                "body_sha256": sha256_bytes(body.encode("utf-8")),
                "retry_policy_id": policy.get("policy_id"),
                "retryable_http_status": status in retryable_http,
                "retry_after_seconds": retry_after,
                "provider_call_pacing": pacing,
            }
            attempts.append(attempt)
            if status < 400 or status not in retryable_http:
                break
        except Exception as exc:
            raw_message = str(exc)
            safe_message = sanitize_transport_message(raw_message)
            failure_class = classify_transport_failure(type(exc).__name__, raw_message)
            halt_classes = transport_halt_classes(endpoint)
            attempt = {
                "attempt_index": attempt_index,
                "started_at_utc": started,
                "finished_at_utc": utc_now(),
                "transport_error": type(exc).__name__,
                "message": safe_message,
                "message_sha256": sha256_bytes(raw_message.encode("utf-8")),
                "message_redacted": safe_message != raw_message,
                "failure_class": failure_class,
                "local_transport_path_failure": failure_class == LOCAL_TRANSPORT_PATH_FAILURE_CLASS,
                "openrouter_transport_halt_candidate": endpoint.get("openrouter_used") is True
                and failure_class in halt_classes,
                "retry_policy_id": policy.get("policy_id"),
                "retryable_transport_error": True,
                "retry_after_seconds": None,
                "provider_call_pacing": pacing,
            }
            attempts.append(attempt)
            if (
                endpoint.get("openrouter_used") is True
                and failure_class in halt_classes
                and local_transport_path_failure_guard_enabled(endpoint)
            ):
                raise LocalTransportPathFailure(
                    f"{failure_class}: {type(exc).__name__}: {safe_message}",
                    attempts=list(attempts),
                    retry_policy=policy,
                    retry_policy_sha256=sha256_json(policy),
                ) from exc
        if attempt_index < max_attempts:
            sleep_seconds = retry_sleep_seconds(policy, attempt_index, attempts[-1].get("retry_after_seconds"))
            attempts[-1]["planned_retry_sleep_seconds"] = sleep_seconds
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)
    return {"attempts": attempts, "retry_policy": policy, "retry_policy_sha256": sha256_json(policy)}


def extract_response_content(raw: dict[str, Any], requested_model: str) -> tuple[str, dict[str, Any], str, bool, Any, str | None, int | None]:
    attempts = raw.get("attempts", [])
    last = attempts[-1] if attempts else {}
    status = last.get("http_status")
    body = last.get("body", "")
    if not body:
        return "", {}, "", False, None, None, status
    try:
        obj = json.loads(body)
    except Exception:
        return body, {}, "", False, None, None, status
    choices = obj.get("choices") or []
    choice = choices[0] if choices else {}
    message = choice.get("message") or {}
    content = message.get("content") or ""
    reasoning_present = bool(message.get("reasoning_content") or message.get("reasoning") or message.get("reasoning_details"))
    usage = obj.get("usage") or {}
    reasoning_tokens = usage.get("reasoning_tokens")
    details = usage.get("completion_tokens_details")
    if reasoning_tokens is None and isinstance(details, dict):
        reasoning_tokens = details.get("reasoning_tokens")
    returned_model = str(obj.get("model") or requested_model)
    return content, usage, returned_model, reasoning_present, reasoning_tokens, choice.get("finish_reason"), status


def visible_field_candidates(visible_text: str) -> tuple[list[str], list[str]]:
    negative_terms = ["revoked", "stale", "forbidden", "protected", "blocked", "archive-only", "archive only", "rollback-only", "rollback only", "decoy", "not outputtable", "must not", "do not", "excluded"]
    positive_terms = ["initial active", "active tokens", "currently active", "current allowed", "allowed path", "allowed implementation path", "final active"]
    tokens = dedupe_preserve(NEUTRAL_TOKEN_RE.findall(visible_text))
    keep: list[str] = []
    excluded: list[str] = []
    lowered = visible_text.lower()
    for token in tokens:
        positions = [idx for idx in range(len(visible_text)) if visible_text.startswith(token, idx)]
        windows = [lowered[max(0, idx - 100) : min(len(lowered), idx + len(token) + 100)] for idx in positions]
        has_negative = any(any(term in window for term in negative_terms) for window in windows)
        has_positive = any(any(term in window for term in positive_terms) for window in windows)
        if has_negative and not has_positive:
            excluded.append(token)
        else:
            keep.append(token)
    return dedupe_preserve(keep), dedupe_preserve(excluded)


def visible_allowed_paths(visible_text: str) -> tuple[list[str], list[str]]:
    paths = dedupe_preserve(PATH_RE.findall(visible_text))
    allowed: list[str] = []
    blocked: list[str] = []
    lowered = visible_text.lower()
    for path in paths:
        positions = [idx for idx in range(len(visible_text)) if visible_text.startswith(path, idx)]
        windows = [lowered[max(0, idx - 90) : min(len(lowered), idx + len(path) + 90)] for idx in positions]
        if any("blocked" in window or "attractive path" in window for window in windows):
            blocked.append(path)
        else:
            allowed.append(path)
    return dedupe_preserve(allowed), dedupe_preserve(blocked)


def dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def parse_state_fields(text: str) -> dict[str, str]:
    raw = str(text or "").strip()
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
    except Exception:
        obj = None
    if isinstance(obj, dict):
        return {str(key).upper(): json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value for key, value in obj.items()}
    matches = list(STATE_FIELD_RE.finditer(raw))
    if not matches:
        return {"RAW": raw}
    fields: dict[str, str] = {}
    for index, match in enumerate(matches):
        key = match.group(1).upper()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        fields[key] = raw[start:end].strip(" ;\n\t")
    return fields


def fit_state(text: str, budget: int) -> tuple[str, bool, int, int]:
    before = len(text)
    if before <= budget:
        return text, False, before, len(text)
    return text[:budget], True, before, budget


def build_update_prompt(method: str, task: dict[str, Any], segment: dict[str, Any], state: str, budget: int, visible_text_so_far: str) -> str:
    common = f"""Task id: {task["task_id"]}
Difficulty: {task["difficulty"]}
Family: {task["family"]}
State budget after deterministic fitting: {budget} characters

Prior transferred state:
{state or "[empty]"}

Current segment {segment["segment_id"]}/{len(task["segments"])} ({segment["role"]}):
{segment["text"]}
"""
    if method == "loop_only":
        method_block = """You are writing only a current-segment loop check.
Do not preserve prior-segment details unless they appear in the current segment.
Do not use SSR fields or deterministic visible carry.
Do not use hidden answers, oracle fields, scoring metadata, or required/forbidden arrays.
Return JSON only: {"CURRENT_GOAL":"...", "GAP":"...", "NEXT_MISTAKE_TO_AVOID":"..."}"""
    elif method == "rolling_summary":
        method_block = """You are maintaining the plain natural-language rolling-summary baseline.
Use the same base behavior as visible-carry methods, but without deterministic VISIBLE_KEEP.
Do not use SSR fields or hidden oracle/scoring material.
Return JSON only: {"SUMMARY":"..."}"""
    elif method == "rolling_visible_carry_forward":
        method_block = """You are maintaining the plain natural-language rolling-summary base.
The runner will append deterministic VISIBLE_KEEP after your state update.
Do not use SSR fields OUT/ALW/NO/B/G/N/CK/LOOP and do not use hidden oracle/scoring material.
Return JSON only: {"NOTE":"...", "BOUNDARY":"..."}"""
    elif method == "rolling_visible_fields_only":
        method_block = """You are maintaining the same natural-language rolling-summary base.
The runner will replace broad notes with compact deterministic visible fields only.
Do not use SSR fields OUT/ALW/NO/B/G/N/CK/LOOP and do not use hidden oracle/scoring material.
Return JSON only: {"NOTE":"...", "BOUNDARY":"..."}"""
    elif method == "ssr_no_visible_carry":
        method_block = """You are maintaining SSR schema without runner-side deterministic visible carry.
Use only model-visible text and prior model-visible SSR state.
Do not append all visible candidates mechanically.
NO/B may contain generic exclusion categories but must not seed the final answer.
Return JSON only: {"OUT":"...", "ALW":"...", "NO":"...", "B":"...", "G":"...", "N":"...", "CK":"..."}"""
    else:
        method_block = """You are maintaining mature SSR schema with deterministic visible-carry support.
Use only model-visible text and prior model-visible state.
NO/B may contain generic exclusion categories but must not seed the final answer.
Return JSON only: {"OUT":"...", "ALW":"...", "NO":"...", "B":"...", "G":"...", "N":"...", "CK":"...", "LOOP":"..."}"""
    return f"{method_block}\n\n{common}"


def compile_state(method: str, raw_state: str, visible_text_so_far: str, budget: int) -> tuple[str, dict[str, Any]]:
    candidates = dedupe_preserve(NEUTRAL_TOKEN_RE.findall(visible_text_so_far))
    field_keep, field_excluded = visible_field_candidates(visible_text_so_far)
    allowed_paths, blocked_paths = visible_allowed_paths(visible_text_so_far)
    raw = raw_state.strip()
    if method in {"rolling_summary", "loop_only"}:
        rendered = raw
    elif method == "rolling_visible_carry_forward":
        rendered = f"VISIBLE_KEEP={','.join(candidates)}\nNOTE={raw}"
    elif method == "rolling_visible_fields_only":
        rendered = (
            f"VISIBLE_KEEP={','.join(field_keep)}\n"
            f"VISIBLE_ALLOWED_SCOPE={','.join(allowed_paths)}\n"
            f"VISIBLE_BOUNDARY=excluded_count:{len(field_excluded)}; blocked_path_count:{len(blocked_paths)}\n"
            "VISIBLE_NOTE=compact deterministic visible fields only"
        )
    elif method == "ssr_no_visible_carry":
        rendered = raw
    else:
        fields = parse_state_fields(raw)
        if fields:
            out = fields.get("OUT", "")
            alw = fields.get("ALW", fields.get("ALLOW", ""))
            no = fields.get("NO", fields.get("B", "excluded categories only"))
            rest = "\n".join(f"{k}={v}" for k, v in fields.items() if k not in {"OUT", "ALW", "ALLOW", "NO", "B"})
            rendered = f"OUT={out or ','.join(field_keep)}\nALW={alw or ','.join(allowed_paths)}\nNO={no}\nB=no forbidden/protected/revoked/stale/blocked/archive-only/rollback-only output\n{rest}"
        else:
            rendered = f"OUT={','.join(field_keep)}\nALW={','.join(allowed_paths)}\nNO=excluded categories only\nB=no forbidden/protected/revoked/stale/blocked/archive-only/rollback-only output\nG=solve final active allowed set\nN=continue\nCK=check state labels\nLOOP=boundary-risk check"
    fitted, hard_cap, before, after = fit_state(rendered, budget)
    audit = {
        "visible_identifier_candidates_count": len(candidates),
        "visible_field_keep_count": len(field_keep),
        "visible_field_excluded_count": len(field_excluded),
        "visible_allowed_path_count": len(allowed_paths),
        "visible_blocked_path_count": len(blocked_paths),
        "compiler_input_visible_text_sha256": sha256_bytes(visible_text_so_far.encode("utf-8")),
        "compiler_input_raw_state_sha256": sha256_bytes(raw_state.encode("utf-8")),
        "compiler_output_state_sha256": sha256_bytes(fitted.encode("utf-8")),
        "state_chars_before_budget": before,
        "state_chars_after_budget": after,
        "state_budget": budget,
        "state_budget_fit_success": len(fitted) <= budget,
        "state_hard_cap_used": hard_cap,
        "compiler_forbidden_source_check": "visible_only_no_oracle",
    }
    return fitted, audit


def build_final_prompt(method: str, task: dict[str, Any], state: str) -> str:
    if method == "mature_ssr_loop":
        method_specific = """Mature SSR final-solve contract:
- final_answer.required_tokens must derive only from OUT.
- final_answer.allowed_paths must derive only from ALW.
- Never copy material from NO/B/G/N/CK/LOOP into required_tokens or allowed_paths."""
    elif method == "ssr_no_visible_carry":
        method_specific = """SSR-without-carry final-solve contract:
- final_answer.required_tokens must derive only from OUT.
- final_answer.allowed_paths must derive only from ALW.
- NO/B/excluded fields must not contribute output-bearing tokens."""
    elif method == "rolling_visible_fields_only":
        method_specific = """Visible-fields-only rule:
- VISIBLE_KEEP is output-bearing.
- VISIBLE_ALLOWED_SCOPE is allowed-scope evidence.
- VISIBLE_BOUNDARY and VISIBLE_NOTE are not output-bearing."""
    elif method == "rolling_visible_carry_forward":
        method_specific = """Visible-carry rule:
- VISIBLE_KEEP is output-bearing candidate state.
- NOTE/BOUNDARY may be used only to decide which visible candidates remain safe."""
    elif method == "rolling_summary":
        method_specific = "Use only the transferred natural-language summary."
    else:
        method_specific = "Use only the current-segment loop notes."
    return f"""Use only the transferred state below and the output schema instruction.
Do not use hidden answers, oracle fields, scoring metadata, or external context.
{method_specific}

Task id: {task["task_id"]}
Method: {method}

Transferred state:
{state}

Output schema instruction:
{task["final_instruction"]}

Return JSON only.
"""


def deterministic_mature_final_output(state: str) -> str:
    fields = parse_state_fields(state)
    out_text = fields.get("OUT", "")
    alw_text = fields.get("ALW", fields.get("ALLOW", ""))
    payload = {
        "final_answer": {
            "required_tokens": dedupe_preserve(NEUTRAL_TOKEN_RE.findall(out_text)),
            "allowed_paths": dedupe_preserve(PATH_RE.findall(alw_text)),
            "state_labels": {},
            "state_transitions": [],
            "boundary_checks": {
                "construction": "deterministic_from_mature_ssr_slots",
                "source_for_required_tokens": "OUT",
                "source_for_allowed_paths": "ALW",
                "no_NO_or_B_material_copied": True,
            },
        }
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def json_parse_success(text: str) -> bool:
    stripped = str(text or "").strip()
    if not stripped:
        return False
    try:
        json.loads(stripped)
        return True
    except Exception:
        pass
    match = re.search(r"\{.*\}", stripped, flags=re.S)
    if not match:
        return False
    try:
        json.loads(match.group(0))
        return True
    except Exception:
        return False


def run_one_row(row: dict[str, Any], task: dict[str, Any], oracle: dict[str, Any], endpoint: dict[str, Any], credential: str, scorer: Any) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    method = row["method"]
    budget = int(row["budget"])
    visible_text_so_far = ""
    state = ""
    call_records: list[dict[str, Any]] = []
    compiler_audits: list[dict[str, Any]] = []
    backend_error = False
    expected_model = endpoint.get("expected_exact_model_string") or endpoint["requested_model"]
    returned_model = endpoint["requested_model"]
    reasoning_present_any = False
    reasoning_tokens_observed: Any = None
    finish_reason = None
    http_status = None

    for segment in task["segments"]:
        visible_text_so_far += "\n" + segment["text"]
        prompt_state = "" if method == "loop_only" else state
        prompt = build_update_prompt(method, task, segment, prompt_state, budget, visible_text_so_far)
        payload = payload_for(endpoint, prompt)
        raw = request_with_retry(endpoint, credential, payload)
        content, usage, returned_model, reasoning_present, reasoning_tokens, finish_reason, http_status = extract_response_content(raw, endpoint["requested_model"])
        reasoning_present_any = reasoning_present_any or reasoning_present
        if reasoning_tokens is not None:
            reasoning_tokens_observed = reasoning_tokens
        call_records.append(
            {
                "call_type": "state_update",
                "segment_id": segment["segment_id"],
                "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
                "request_payload_sha256": sha256_json(payload),
                "raw_response_sha256": sha256_json(raw),
                "attempt_count": len(raw.get("attempts", [])),
                "attempt_http_statuses": [attempt.get("http_status") for attempt in raw.get("attempts", [])],
                "attempt_transport_errors": [
                    attempt.get("transport_error")
                    for attempt in raw.get("attempts", [])
                    if attempt.get("transport_error") is not None
                ],
                "attempt_failure_classes": [
                    attempt_failure_class(attempt)
                    for attempt in raw.get("attempts", [])
                    if attempt_failure_class(attempt) is not None
                ],
                "attempt_messages": [
                    attempt.get("message")
                    for attempt in raw.get("attempts", [])
                    if attempt.get("message")
                ],
                "local_transport_path_failure_detected": raw_has_local_transport_path_failure(raw),
                "retry_policy_id": raw.get("retry_policy", {}).get("policy_id"),
                "retry_policy_sha256": raw.get("retry_policy_sha256"),
                "retry_after_seconds": [
                    attempt.get("retry_after_seconds")
                    for attempt in raw.get("attempts", [])
                    if attempt.get("retry_after_seconds") is not None
                ],
                "planned_retry_sleep_seconds": [
                    attempt.get("planned_retry_sleep_seconds")
                    for attempt in raw.get("attempts", [])
                    if attempt.get("planned_retry_sleep_seconds") is not None
                ],
                "usage": usage,
                "returned_model": returned_model,
                "http_status": http_status,
                "finish_reason": finish_reason,
            }
        )
        state, compiler_audit = compile_state(method, content, visible_text_so_far, budget)
        compiler_audits.append(compiler_audit)
        if not content or (http_status is not None and http_status >= 400):
            backend_error = True

    final_prompt = build_final_prompt(method, task, state)
    final_payload = payload_for(endpoint, final_prompt)
    final_output_construction = "provider_final_call"
    if method == "mature_ssr_loop":
        final_output = deterministic_mature_final_output(state)
        final_raw = {
            "attempts": [
                {
                    "attempt_index": 0,
                    "started_at_utc": utc_now(),
                    "finished_at_utc": utc_now(),
                    "synthetic_final_construction": True,
                    "body": json.dumps({"model": "deterministic_mature_ssr_slot_compiler", "choices": [{"message": {"content": final_output}}]}, ensure_ascii=False),
                }
            ]
        }
        final_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        final_output_construction = "deterministic_mature_ssr_slot_compiler"
    else:
        final_raw = request_with_retry(endpoint, credential, final_payload)
        final_output, final_usage, returned_model, reasoning_present, reasoning_tokens, finish_reason, http_status = extract_response_content(final_raw, endpoint["requested_model"])
        reasoning_present_any = reasoning_present_any or reasoning_present
        if reasoning_tokens is not None:
            reasoning_tokens_observed = reasoning_tokens
        if not final_output or (http_status is not None and http_status >= 400):
            backend_error = True

    parsed_output = {"final_output": final_output, "final_state": state}
    raw_response = {
        "state_calls": call_records,
        "final_raw": final_raw,
        "final_output": final_output,
        "final_state": state,
        "compiler_audits": compiler_audits,
    }
    local_transport_path_failure_detected = (
        any(call.get("local_transport_path_failure_detected") for call in call_records)
        or raw_has_local_transport_path_failure(final_raw)
    )
    score_error = None
    try:
        metric = scorer.score_task(
            oracle,
            {
                "task_id": task["task_id"],
                "method": method,
                "model": endpoint["requested_model"],
                "budget": budget,
                "run_id": row["run_id"],
                "final_output": final_output,
                "final_state": state,
            },
        )
        score_row_emitted = True
    except Exception as exc:
        metric = {}
        score_error = f"{type(exc).__name__}: {exc}"
        score_row_emitted = False

    final_parse_success = json_parse_success(final_output)
    returned_model_match = returned_model == expected_model
    if not returned_model_match:
        backend_error = True

    score_row = {
        **metric,
        "schema_version": "pcg_dynamic_state_v2.benchmark_admission_score_row.v1",
        "experiment_id": row["experiment_id"],
        "row_id": row["row_id"],
        "global_artifact_id": row["global_artifact_id"],
        "logical_request_hash": row["logical_request_hash"],
        "task_id": row["task_id"],
        "model_condition_id": row["model_condition_id"],
        "provider": row["provider"],
        "requested_model": row["requested_model"],
        "selected_model_or_returned_model": returned_model,
        "expected_model_string": expected_model,
        "returned_model_match": returned_model_match,
        "method": method,
        "budget": budget,
        "run_id": row["run_id"],
        "matrix_role": row["matrix_role"],
        "primary_analysis_eligible": False,
        "final_json_parse_success": final_parse_success,
        "score_row_emitted": score_row_emitted,
        "backend_error": backend_error,
        "reasoning_content_present": reasoning_present_any,
        "reasoning_tokens_observed": reasoning_tokens_observed,
        "finish_reason": finish_reason,
        "http_status": http_status,
        "score_error": score_error,
        "raw_response_sha256": sha256_json(raw_response),
        "parsed_output_sha256": sha256_json(parsed_output),
        "metric_record_sha256": sha256_json(metric),
        "provider_call_count": len(call_records) + (0 if method == "mature_ssr_loop" else 1),
        "final_attempt_count": len(final_raw.get("attempts", [])),
        "retry_policy_id": final_raw.get("retry_policy", {}).get("policy_id"),
        "retry_policy_sha256": final_raw.get("retry_policy_sha256"),
        "openrouter_runtime_hardening_applied": endpoint.get("openrouter_runtime_hardening", {}).get("applied") is True,
        "final_output_construction": final_output_construction,
        "state_hard_cap_used": any(item.get("state_hard_cap_used") for item in compiler_audits),
        "local_transport_path_failure_detected": local_transport_path_failure_detected,
    }
    adapter_row = {
        "schema_version": "pcg_dynamic_state_v2.benchmark_admission_adapter_source.v1",
        "logical_request_hash": row["logical_request_hash"],
        "row_id": row["row_id"],
        "global_artifact_id": row["global_artifact_id"],
        "raw_response": raw_response,
        "raw_response_sha256": sha256_json(raw_response),
        "provider_metadata": {
            "returned_model": returned_model,
            "backend_error": backend_error,
            "reasoning_content_present": reasoning_present_any,
            "reasoning_tokens_observed": reasoning_tokens_observed,
            "http_status": http_status,
            "finish_reason": finish_reason,
            "final_attempt_count": len(final_raw.get("attempts", [])),
            "retry_policy_id": final_raw.get("retry_policy", {}).get("policy_id"),
            "retry_policy_sha256": final_raw.get("retry_policy_sha256"),
            "local_transport_path_failure_detected": local_transport_path_failure_detected,
            "openrouter_runtime_hardening": endpoint.get("openrouter_runtime_hardening"),
        },
        "usage": final_usage,
        "finish_reason": finish_reason,
    }
    controlled_row = {
        **score_row,
        "final_output": final_output,
        "final_state": state,
        "compiler_audits": compiler_audits,
    }
    return controlled_row, score_row, adapter_row


def admission_decision(confirmatory_scores: list[dict[str, Any]]) -> dict[str, Any]:
    parse_score_rows = [
        row for row in confirmatory_scores
        if row.get("final_json_parse_success") is True and row.get("score_row_emitted") is True
    ]
    hard_failures = [
        row for row in confirmatory_scores
        if row.get("backend_error")
        or row.get("reasoning_content_present")
        or not row.get("returned_model_match", True)
        or not row.get("raw_response_sha256")
    ]
    if hard_failures:
        decision = "HOLD_FOR_RERUN_OR_ADAPTER_FIX"
    elif len(parse_score_rows) >= 11:
        decision = "ADMIT_MODEL"
    else:
        decision = "HOLD_FOR_PROMPT_OR_ADAPTER_FIX"
    return {
        "decision": decision,
        "confirmatory_rows": len(confirmatory_scores),
        "parse_and_score_success_count": len(parse_score_rows),
        "per_model_threshold": "11/12",
        "hard_failure_count": len(hard_failures),
        "outcome_fields_used_for_admission": False,
    }


def write_report(path: Path, model_condition: str, task_id: str, decision: dict[str, Any], confirmatory_scores: list[dict[str, Any]], diagnostic_scores: list[dict[str, Any]]) -> None:
    def count(rows: list[dict[str, Any]], key: str) -> int:
        return sum(1 for row in rows if row.get(key) is True)

    lines = [
        f"# Benchmark Admission Smoke - {model_condition}",
        "",
        f"Date: {DATE}",
        "",
        f"Task: `{task_id}`",
        "",
        f"Decision: `{decision['decision']}`",
        "",
        "## Confirmatory Smoke",
        "",
        "| field | count | denominator |",
        "| --- | ---: | ---: |",
        f"| final_json_parse_success and score_row_emitted | {decision['parse_and_score_success_count']} | {len(confirmatory_scores)} |",
        f"| backend_error | {count(confirmatory_scores, 'backend_error')} | {len(confirmatory_scores)} |",
        f"| reasoning_content_present | {count(confirmatory_scores, 'reasoning_content_present')} | {len(confirmatory_scores)} |",
        f"| answer_success | {count(confirmatory_scores, 'answer_success')} | {len(confirmatory_scores)} |",
        f"| state_governance_success | {count(confirmatory_scores, 'state_governance_success')} | {len(confirmatory_scores)} |",
        f"| reliable_composite_success | {count(confirmatory_scores, 'reliable_composite_success')} | {len(confirmatory_scores)} |",
        "",
        "Outcome fields above are reported, not used as admission filters.",
        "",
        "## Budget-300 Diagnostic Smoke",
        "",
        "| field | count | denominator |",
        "| --- | ---: | ---: |",
        f"| final_json_parse_success and score_row_emitted | {sum(1 for row in diagnostic_scores if row.get('final_json_parse_success') and row.get('score_row_emitted'))} | {len(diagnostic_scores)} |",
        f"| backend_error | {count(diagnostic_scores, 'backend_error')} | {len(diagnostic_scores)} |",
        f"| reliable_composite_success | {count(diagnostic_scores, 'reliable_composite_success')} | {len(diagnostic_scores)} |",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run_model(
    model_condition: str,
    task_id: str,
    max_workers: int,
    openrouter_runtime_hardening: bool,
    provider_call_interval_seconds: float,
) -> int:
    if provider_call_interval_seconds < 0:
        raise SystemExit("--provider-call-interval-seconds must be >= 0")
    load_env_files()
    endpoints = endpoint_by_condition()
    endpoint = endpoints[model_condition]
    if openrouter_runtime_hardening:
        if provider_call_interval_seconds < 15:
            raise SystemExit("--openrouter-runtime-hardening requires --provider-call-interval-seconds >= 15")
        endpoint = apply_openrouter_runtime_hardening(endpoint)
    configure_provider_call_pacing(provider_call_interval_seconds)
    credential = os.environ.get(endpoint["api_key_env"], "")
    if not credential:
        raise SystemExit(f"{endpoint['api_key_env']} not found in environment or local env files")
    visible_by_id, oracle_by_id = task_maps()
    task = visible_by_id[task_id]
    oracle = oracle_by_id[task_id]
    scorer = load_module(SCORER_PATH, "pcg_dynamic_state_v2_main_matrix_scorer")

    out_dir = OUT_ROOT / model_condition
    confirmatory_rows = rows_from_config(CONFIRMATORY_CONFIG, model_condition, CONFIRMATORY_METHODS, [600, 1200], task_id)
    diagnostic_rows = rows_from_config(DIAGNOSTIC_CONFIG, model_condition, DIAGNOSTIC_METHODS, [300], task_id)
    confirmatory_config = build_smoke_config(model_condition, confirmatory_rows, out_dir, "confirmatory_12row")
    diagnostic_config = build_smoke_config(model_condition, diagnostic_rows, out_dir, "budget300_diagnostic_4row")

    all_rows = [("confirmatory", row) for row in confirmatory_rows] + [("diagnostic300", row) for row in diagnostic_rows]
    controlled_by_role: dict[str, list[dict[str, Any]]] = {"confirmatory": [], "diagnostic300": []}
    score_by_role: dict[str, list[dict[str, Any]]] = {"confirmatory": [], "diagnostic300": []}
    adapter_by_role: dict[str, list[dict[str, Any]]] = {"confirmatory": [], "diagnostic300": []}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(run_one_row, row, task, oracle, endpoint, credential, scorer): (role, row)
            for role, row in all_rows
        }
        for future in as_completed(futures):
            role, row = futures[future]
            try:
                controlled, score, adapter = future.result()
            except Exception as exc:
                controlled = {
                    "schema_version": "pcg_dynamic_state_v2.benchmark_admission_score_row.v1",
                    "row_id": row["row_id"],
                    "global_artifact_id": row["global_artifact_id"],
                    "logical_request_hash": row["logical_request_hash"],
                    "task_id": row["task_id"],
                    "model_condition_id": row["model_condition_id"],
                    "method": row["method"],
                    "budget": row["budget"],
                    "run_id": row["run_id"],
                    "backend_error": True,
                    "final_json_parse_success": False,
                    "score_row_emitted": False,
                    "score_error": f"{type(exc).__name__}: {exc}",
                }
                score = dict(controlled)
                adapter = {
                    "logical_request_hash": row["logical_request_hash"],
                    "row_id": row["row_id"],
                    "global_artifact_id": row["global_artifact_id"],
                    "raw_response": {"runner_exception": f"{type(exc).__name__}: {exc}"},
                    "raw_response_sha256": sha256_json({"runner_exception": f"{type(exc).__name__}: {exc}"}),
                    "provider_metadata": {"backend_error": True},
                }
            controlled_by_role[role].append(controlled)
            score_by_role[role].append(score)
            adapter_by_role[role].append(adapter)

    for role in controlled_by_role:
        controlled_by_role[role].sort(key=lambda item: item["row_id"])
        score_by_role[role].sort(key=lambda item: item["row_id"])
        adapter_by_role[role].sort(key=lambda item: item["row_id"])

    write_jsonl(out_dir / "CONTROLLED_ROWS.confirmatory.jsonl", controlled_by_role["confirmatory"])
    write_jsonl(out_dir / "scores.confirmatory.jsonl", score_by_role["confirmatory"])
    write_csv(out_dir / "scores.confirmatory.csv", score_by_role["confirmatory"])
    write_jsonl(out_dir / "adapter_source.confirmatory.jsonl", adapter_by_role["confirmatory"])
    write_jsonl(out_dir / "CONTROLLED_ROWS.budget300_diagnostic.jsonl", controlled_by_role["diagnostic300"])
    write_jsonl(out_dir / "scores.budget300_diagnostic.jsonl", score_by_role["diagnostic300"])
    write_csv(out_dir / "scores.budget300_diagnostic.csv", score_by_role["diagnostic300"])
    write_jsonl(out_dir / "adapter_source.budget300_diagnostic.jsonl", adapter_by_role["diagnostic300"])

    decision = admission_decision(score_by_role["confirmatory"])
    summary = {
        "schema_version": "pcg_dynamic_state_v2.benchmark_admission_summary.v1",
        "created_at_utc": utc_now(),
        "model_condition_id": model_condition,
        "task_id": task_id,
        "decision": decision,
        "confirmatory_config": rel(confirmatory_config),
        "diagnostic_config": rel(diagnostic_config),
        "controlled_rows_confirmatory": rel(out_dir / "CONTROLLED_ROWS.confirmatory.jsonl"),
        "controlled_rows_budget300_diagnostic": rel(out_dir / "CONTROLLED_ROWS.budget300_diagnostic.jsonl"),
        "adapter_source_confirmatory": rel(out_dir / "adapter_source.confirmatory.jsonl"),
        "adapter_source_budget300_diagnostic": rel(out_dir / "adapter_source.budget300_diagnostic.jsonl"),
        "api_calls_performed": sum(int(row.get("provider_call_count", 0) or 0) for row in controlled_by_role["confirmatory"] + controlled_by_role["diagnostic300"]),
    }
    write_json(out_dir / "summary.json", summary)
    write_report(out_dir / "REPORT.md", model_condition, task_id, decision, score_by_role["confirmatory"], score_by_role["diagnostic300"])
    print(canonical_json(summary))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-condition",
        required=True,
        choices=["deepseek_v4pro", "qwen37max", "kimi_k26", "openrouter_gpt55", "openrouter_claude48"],
    )
    parser.add_argument("--task-id", default="pcgds_v2_00001_api_migration_state_transition_easy")
    parser.add_argument("--max-workers", type=int, default=10)
    parser.add_argument(
        "--provider-call-interval-seconds",
        type=float,
        default=0.0,
        help="Process-local minimum interval before each actual provider HTTP attempt, including within-row calls and retries",
    )
    parser.add_argument(
        "--openrouter-runtime-hardening",
        action="store_true",
        help="Opt in to post-pause OpenRouter provider-route, compression, metadata, and bounded-backoff controls",
    )
    args = parser.parse_args()
    return run_model(
        args.model_condition,
        args.task_id,
        args.max_workers,
        args.openrouter_runtime_hardening,
        args.provider_call_interval_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
