#!/usr/bin/env python3
"""Run a minimal live provider refresh for the main-matrix admission gate.

The script sends one short non-benchmark prompt per frozen model condition,
records sanitized response metadata, and emits a provider-adapter JSONL that can
be consumed by `main_matrix_vcr_runner.py --mode record`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import run_model_admission_smoke as smoke


ROOT = Path(__file__).resolve().parents[2]
DATE = "20260625"
ENV_CANDIDATES = [
    ROOT / ".env",
    ROOT / ".env.local",
    ROOT / ".env.save",
]
PROVIDER_SNAPSHOT = ROOT / f"artifact/protocol/main_matrix/admission/PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_{DATE}.json"
OUT_DIR = ROOT / f"artifact/protocol/main_matrix/admission/live_refresh_{DATE}"
SMOKE_CONFIG = OUT_DIR / "provider_live_refresh_smoke_config.json"
SMOKE_ROWS = OUT_DIR / "provider_live_refresh_smoke_config.rows.jsonl"
ADAPTER_SOURCE = OUT_DIR / "provider_adapter_record_source.jsonl"
SUMMARY = OUT_DIR / "provider_live_refresh_summary.json"
REPORT = OUT_DIR / "PROVIDER_LIVE_REFRESH_REPORT.md"

PROMPT = "Return exactly OK."
EXPERIMENT_ID = "pcg_dynamic_state_v2_provider_live_refresh_20260625"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def redact_token(value: str) -> str:
    return f"redacted:{sha256_bytes(value.encode('utf-8'))[:16]}"


def sanitize_provider_value(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            lowered = key.lower()
            if lowered in {"id", "request_id", "generation_id", "system_fingerprint"} and isinstance(item, str):
                out[key] = redact_token(item)
            else:
                out[key] = sanitize_provider_value(item)
        return out
    if isinstance(value, list):
        return [sanitize_provider_value(item) for item in value]
    if isinstance(value, str):
        return value
    return value


def sanitize_generation_body(body: dict[str, Any]) -> dict[str, Any]:
    sanitized = sanitize_provider_value(body)
    error = sanitized.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str):
            error["message"] = re.sub(
                r"Generation\s+[A-Za-z0-9:_-]+\s+not found",
                lambda match: f"Generation {redact_token(match.group(0).split()[1])} not found",
                message,
            )
    return sanitized


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


def endpoint_payload(endpoint: dict[str, Any]) -> dict[str, Any]:
    controls = endpoint["request_controls"]
    payload: dict[str, Any] = {
        "model": endpoint["requested_model"],
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": False,
    }
    if "max_tokens" in controls:
        payload["max_tokens"] = controls["max_tokens"]
    if "max_completion_tokens" in controls:
        payload["max_completion_tokens"] = controls["max_completion_tokens"]
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
    if endpoint.get("openrouter_used"):
        headers = {
            "Authorization": f"Bearer {credential}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://anonymous-review-artifact.local",
            "X-Title": "pcg-dynamic-state-v2-provider-refresh",
        }
        metadata_header = endpoint.get("request_controls", {}).get("openrouter_metadata_header", {})
        if metadata_header.get("send_mode") == "explicit" and metadata_header.get("value"):
            headers["X-OpenRouter-Metadata"] = str(metadata_header["value"])
        return headers
    return {"Authorization": f"Bearer {credential}", "Content-Type": "application/json"}


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 90) -> tuple[int, dict[str, Any], str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(text)
            except json.JSONDecodeError:
                body = {"_non_json_body": text}
            return response.status, body, text
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            body = {"_non_json_body": text}
        return exc.code, body, text
    except Exception as exc:
        return 0, {"error": type(exc).__name__, "message": str(exc)}, ""


def get_json(url: str, headers: dict[str, str], timeout: int = 60) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(text)
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            body = {"_non_json_body": text}
        return exc.code, body
    except Exception as exc:
        return 0, {"error": type(exc).__name__, "message": str(exc)}


def is_error_body(body: dict[str, Any]) -> bool:
    error = body.get("error")
    return isinstance(error, dict) or "_non_json_body" in body


def classify_generation_metadata(status: int | None, body: dict[str, Any] | None) -> tuple[str, bool]:
    if status is None or body is None:
        return "not_requested", False
    if 200 <= status < 300 and not is_error_body(body):
        return "present", False
    return "unavailable_error", True


def extract_message(body: dict[str, Any]) -> tuple[str, dict[str, Any], str | None, str | None]:
    choices = body.get("choices") or []
    if not choices:
        return "", body.get("usage", {}), body.get("model"), None
    choice = choices[0]
    message = choice.get("message") or {}
    content = message.get("content") or ""
    return content, body.get("usage", {}), body.get("model"), choice.get("finish_reason")


def build_smoke_rows(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prompt_hash = sha256_bytes(PROMPT.encode("utf-8"))
    for index, endpoint in enumerate(endpoints, start=1):
        payload = endpoint_payload(endpoint)
        logical_key = {
            "schema_version": "pcg_dynamic_state_v2.provider_live_refresh_request_key.v1",
            "task_id": "provider_live_refresh_nonbenchmark_prompt",
            "method": "provider_refresh",
            "budget": 0,
            "run_id": 1,
            "model_name": endpoint["requested_model"],
            "model_condition_id": endpoint["condition_id"],
            "provider": endpoint["provider"],
            "access_path": endpoint["access_path"],
            "openrouter_used": endpoint["openrouter_used"],
            "fallback_enabled": endpoint["fallback_enabled"],
            "prompt_sha256": prompt_hash,
            "request_payload_sha256": sha256_json(payload),
        }
        rows.append(
            {
                "schema_version": "pcg_dynamic_state_v2.provider_live_refresh_row.v1",
                "row_index": index,
                "experiment_id": EXPERIMENT_ID,
                "matrix_role": "admission_provider_live_refresh_not_primary",
                "primary_analysis_eligible": False,
                "row_id": f"provider_live_refresh::{endpoint['condition_id']}::run1",
                "global_artifact_id": f"{EXPERIMENT_ID}::provider_live_refresh::{endpoint['condition_id']}::run1",
                "task_id": "provider_live_refresh_nonbenchmark_prompt",
                "model_condition_id": endpoint["condition_id"],
                "provider": endpoint["provider"],
                "access_path": endpoint["access_path"],
                "requested_model": endpoint["requested_model"],
                "openrouter_used": endpoint["openrouter_used"],
                "fallback_enabled": endpoint["fallback_enabled"],
                "method": "provider_refresh",
                "budget": 0,
                "run_id": 1,
                "logical_request_key": logical_key,
                "logical_request_hash": sha256_json(logical_key),
            }
        )
    return rows


def build_smoke_config(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "pcg_dynamic_state_v2.provider_live_refresh_config.v1",
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": utc_now(),
        "matrix_role": "admission_provider_live_refresh_not_primary",
        "primary_analysis_eligible": False,
        "matrix_shape": {"expected_rows": len(rows), "models": len(rows), "tasks": 1, "methods": 1, "budgets": 1, "runs": 1},
        "row_manifest": {"path": rel(SMOKE_ROWS), "sha256": sha256_bytes(b''.join((canonical_json(row) + "\n").encode("utf-8") for row in rows))},
        "prompt": {"kind": "nonbenchmark_provider_refresh", "sha256": sha256_bytes(PROMPT.encode("utf-8"))},
    }


def refresh_one(endpoint: dict[str, Any], row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    started = utc_now()
    credential = os.environ.get(endpoint["api_key_env"], "")
    payload = endpoint_payload(endpoint)
    payload_hash = sha256_json(payload)
    if not credential:
        result = {
            "condition_id": endpoint["condition_id"],
            "provider": endpoint["provider"],
            "requested_model": endpoint["requested_model"],
            "status": "missing_api_key",
            "api_key_env": endpoint["api_key_env"],
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
            "request_payload_sha256": payload_hash,
            "logical_request_hash": row["logical_request_hash"],
        }
        return result, None

    url = endpoint["base_url"].rstrip("/") + "/chat/completions"
    headers = request_headers(endpoint, credential)
    status, body, text = post_json(url, payload, headers)
    finished = utc_now()
    content, usage, returned_model, finish_reason = extract_message(body)
    choices = body.get("choices") or []
    message = (choices[0].get("message") or {}) if choices else {}
    completion_details = usage.get("completion_tokens_details") or {}
    reasoning_tokens = completion_details.get("reasoning_tokens")
    generation_metadata_raw: dict[str, Any] | None = None
    generation_metadata: dict[str, Any] | None = None
    generation_metadata_status = "not_applicable"
    generation_metadata_error_body_present = False
    if endpoint.get("openrouter_used") and body.get("id"):
        generation_url = endpoint["base_url"].rstrip("/") + f"/generation?id={body['id']}"
        gen_status, gen_body = get_json(generation_url, request_headers(endpoint, credential))
        generation_metadata_raw = {"http_status": gen_status, "body": sanitize_generation_body(gen_body)}
        generation_metadata_status, generation_metadata_error_body_present = classify_generation_metadata(gen_status, gen_body)
        if generation_metadata_status == "present":
            generation_metadata = generation_metadata_raw

    sanitized_body = sanitize_provider_value(body)

    ok = 200 <= status < 300 and content.strip() == "OK"
    result = {
        "condition_id": endpoint["condition_id"],
        "provider": endpoint["provider"],
        "provider_route_hint": endpoint.get("provider_route_hint"),
        "access_path": endpoint["access_path"],
        "openrouter_used": endpoint["openrouter_used"],
        "requested_model": endpoint["requested_model"],
        "returned_model": returned_model,
        "expected_exact_model_string": endpoint.get("expected_exact_model_string"),
        "fallback_enabled": endpoint["fallback_enabled"],
        "http_status": status,
        "status": "pass" if ok else "fail",
        "content_exact_ok": content.strip() == "OK",
        "finish_reason": finish_reason,
        "message_reasoning_present": bool(message.get("reasoning")),
        "reasoning_details_present": bool(message.get("reasoning_details")),
        "reasoning_tokens": reasoning_tokens,
        "usage": usage,
        "started_at_utc": started,
        "finished_at_utc": finished,
        "request_payload_sha256": payload_hash,
        "raw_response_sha256": sha256_json(sanitized_body),
        "logical_request_hash": row["logical_request_hash"],
        "openrouter_generation_metadata_present": generation_metadata_status == "present",
        "openrouter_generation_metadata_status": generation_metadata_status,
        "openrouter_generation_metadata_http_status": generation_metadata_raw.get("http_status") if generation_metadata_raw else None,
        "openrouter_generation_metadata_error_body_present": generation_metadata_error_body_present,
        "openrouter_generation_metadata_raw_sha256": sha256_json(generation_metadata_raw) if generation_metadata_raw else None,
        "openrouter_generation_metadata_sha256": sha256_json(generation_metadata) if generation_metadata else None,
        "error_body_present": not (200 <= status < 300),
        "sanitized_error_body": sanitized_body if not (200 <= status < 300) else None,
    }
    source_entry = {
        "logical_request_hash": row["logical_request_hash"],
        "row_id": row["row_id"],
        "global_artifact_id": row["global_artifact_id"],
        "raw_response": sanitized_body,
        "raw_response_sha256": sha256_json(sanitized_body),
        "provider_metadata": {
            "condition_id": endpoint["condition_id"],
            "provider": endpoint["provider"],
            "access_path": endpoint["access_path"],
            "openrouter_used": endpoint["openrouter_used"],
            "requested_model": endpoint["requested_model"],
            "returned_model": returned_model,
            "http_status": status,
            "generation_metadata": generation_metadata,
            "generation_metadata_status": generation_metadata_status,
            "generation_metadata_http_status": generation_metadata_raw.get("http_status") if generation_metadata_raw else None,
            "generation_metadata_error_body_present": generation_metadata_error_body_present,
            "generation_metadata_raw_sha256": sha256_json(generation_metadata_raw) if generation_metadata_raw else None,
            "message_reasoning_present": bool(message.get("reasoning")),
            "reasoning_details_present": bool(message.get("reasoning_details")),
            "reasoning_tokens": reasoning_tokens,
        },
        "usage": usage,
        "finish_reason": finish_reason,
    } if 200 <= status < 300 else None
    return result, source_entry


def write_report(results: list[dict[str, Any]], record_source_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Provider Live Refresh Report",
        "",
        f"Created: `{utc_now()}`",
        "",
        "This is an admission-only live refresh. It uses a non-benchmark prompt",
        "and does not populate primary main-matrix results.",
        "",
        "## Results",
        "",
        "| condition | provider | route | status | http | returned model | content OK | reasoning tokens | reasoning payload | generation metadata |",
        "| --- | --- | --- | --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for item in results:
        lines.append(
            "| {condition_id} | {provider} | {route} | {status} | {http_status} | {returned_model} | {content_exact_ok} | {reasoning_tokens} | {reasoning_payload} | {metadata} |".format(
                condition_id=item["condition_id"],
                provider=item["provider"],
                route="OpenRouter" if item["openrouter_used"] else "direct",
                status=item["status"],
                http_status=item.get("http_status", ""),
                returned_model=item.get("returned_model"),
                content_exact_ok=item.get("content_exact_ok"),
                reasoning_tokens=item.get("reasoning_tokens"),
                reasoning_payload=item.get("message_reasoning_present") or item.get("reasoning_details_present"),
                metadata=item.get("openrouter_generation_metadata_status", "not_applicable"),
            )
        )
    lines.extend(
        [
            "",
            "OpenRouter `/generation` error bodies are retained only in redacted form,",
            "and reviewer-visible hashes track the redacted payloads rather than",
            "provider-issued IDs.",
            "",
            "## VCR Adapter Source",
            "",
            f"- Source JSONL: `{rel(ADAPTER_SOURCE)}`",
            f"- Rows available for record mode: `{len(record_source_rows)}`",
            f"- Smoke config: `{rel(SMOKE_CONFIG)}`",
            "",
            "Replay/record closure is checked separately by `main_matrix_vcr_runner.py`.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run_refresh(openrouter_runtime_hardening: bool) -> int:
    load_env_files()
    snapshot = read_json(PROVIDER_SNAPSHOT)
    endpoints = snapshot["endpoints"]
    if openrouter_runtime_hardening:
        endpoints = [
            smoke.apply_openrouter_runtime_hardening(endpoint) if endpoint.get("openrouter_used") else endpoint
            for endpoint in endpoints
        ]
    rows = build_smoke_rows(endpoints)
    write_jsonl(SMOKE_ROWS, rows)
    write_json(SMOKE_CONFIG, build_smoke_config(rows))

    results: list[dict[str, Any]] = []
    record_source_rows: list[dict[str, Any]] = []
    for endpoint, row in zip(endpoints, rows):
        result, source_entry = refresh_one(endpoint, row)
        results.append(result)
        if source_entry is not None:
            record_source_rows.append(source_entry)

    write_jsonl(ADAPTER_SOURCE, record_source_rows)
    passed = len(record_source_rows) == len(rows) and all(item["status"] == "pass" for item in results)
    summary = {
        "schema_version": "pcg_dynamic_state_v2.provider_live_refresh_summary.v1",
        "created_at_utc": utc_now(),
        "passed": passed,
        "endpoint_count": len(rows),
        "successful_adapter_rows": len(record_source_rows),
        "failure_count": sum(1 for item in results if item["status"] != "pass"),
        "api_calls_performed": len(rows),
        "results": results,
        "smoke_config": rel(SMOKE_CONFIG),
        "smoke_rows": rel(SMOKE_ROWS),
        "adapter_record_source": rel(ADAPTER_SOURCE),
    }
    write_json(SUMMARY, summary)
    write_report(results, record_source_rows)
    print(canonical_json({"passed": passed, "endpoint_count": len(rows), "successful_adapter_rows": len(record_source_rows), "failure_count": summary["failure_count"], "summary": rel(SUMMARY)}))
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--openrouter-runtime-hardening",
        action="store_true",
        help="Opt in to post-pause OpenRouter provider-route, compression, metadata, and bounded-backoff controls",
    )
    args = parser.parse_args()
    return run_refresh(args.openrouter_runtime_hardening)


if __name__ == "__main__":
    raise SystemExit(main())
