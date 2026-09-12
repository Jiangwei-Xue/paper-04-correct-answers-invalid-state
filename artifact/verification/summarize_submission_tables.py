#!/usr/bin/env python3
"""Build deterministic submission aggregate tables from tracked score CSVs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from io import StringIO
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
RECORD_ROOT = REPO_ROOT / "artifact" / "results" / "main_matrix" / "record_mode_20260627"
OUTPUT_DIR = REPO_ROOT / "paper" / "submission_tables" / "tables"
STATUS_CSV = RECORD_ROOT / "CLEAN_V2_MATRIX_MODEL_STATUS_20260629.csv"

PRIMARY_SCORE_FILES = {
    "deepseek_v4pro": RECORD_ROOT
    / "ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628"
    / "deepseek_v4pro"
    / "confirmatory"
    / "scores.confirmatory.csv",
    "qwen37max": RECORD_ROOT
    / "ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628"
    / "qwen37max"
    / "confirmatory"
    / "scores.confirmatory.csv",
    "kimi_k26": RECORD_ROOT
    / "ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628"
    / "kimi_k26"
    / "confirmatory"
    / "scores.confirmatory.csv",
    "openrouter_claude48": RECORD_ROOT
    / "OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627"
    / "openrouter_claude48"
    / "confirmatory"
    / "scores.confirmatory.csv",
    "openrouter_gpt55": RECORD_ROOT
    / "OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627"
    / "openrouter_gpt55"
    / "confirmatory"
    / "scores.confirmatory.csv",
}

BUDGET300_SCORE_FILES = {
    "deepseek_v4pro": RECORD_ROOT
    / "BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629"
    / "deepseek_v4pro"
    / "budget300_diagnostic"
    / "scores.budget300_diagnostic.csv",
    "qwen37max": RECORD_ROOT
    / "BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629"
    / "qwen37max"
    / "budget300_diagnostic"
    / "scores.budget300_diagnostic.csv",
    "kimi_k26": RECORD_ROOT
    / "BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629"
    / "kimi_k26"
    / "budget300_diagnostic"
    / "scores.budget300_diagnostic.csv",
    "openrouter_claude48": RECORD_ROOT
    / "BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629"
    / "openrouter_claude48"
    / "budget300_diagnostic"
    / "scores.budget300_diagnostic.csv",
    "openrouter_gpt55": RECORD_ROOT
    / "BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629"
    / "openrouter_gpt55"
    / "budget300_diagnostic"
    / "scores.budget300_diagnostic.csv",
}

QWEN3_CONFIRMATORY_SCORE = (
    RECORD_ROOT
    / "OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629"
    / "openrouter_qwen3_coder_alibaba_supplement"
    / "scores.confirmatory.csv"
)

METRIC_FIELDS = [
    "backend_error",
    "parse_and_score_success",
    "answer_success",
    "state_governance_success",
    "reliable_composite_success",
    "state_hard_cap_used",
]

OUTPUT_FILES = [
    "primary_overall.csv",
    "primary_by_model.csv",
    "primary_by_method.csv",
    "primary_by_budget.csv",
    "budget300_diagnostic_overall.csv",
    "budget300_diagnostic_by_model.csv",
    "budget300_diagnostic_by_method.csv",
    "qwen3_coder_supplement_overall.csv",
    "qwen3_coder_supplement_by_method.csv",
    "qwen3_coder_supplement_by_budget.csv",
    "submission_summary.json",
    "submission_tables.md",
]


def bool_value(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_labeled_rows(files: dict[str, Path], role: str) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    rows: list[dict[str, str]] = []
    sources: list[dict[str, Any]] = []
    for model_condition_id, path in files.items():
        if not path.exists():
            raise FileNotFoundError(path)
        source_rows = read_csv(path)
        for row in source_rows:
            row["_source_role"] = role
            row["_source_file"] = rel(path)
            row["_source_model_condition_id"] = model_condition_id
        rows.extend(source_rows)
        sources.append(
            {
                "model_condition_id": model_condition_id,
                "path": rel(path),
                "rows": len(source_rows),
                "sha256": file_sha256(path),
            }
        )
    return rows, sources


def parse_and_score_success(row: dict[str, str]) -> bool:
    return bool_value(row.get("final_json_parse_success")) and bool_value(row.get("score_row_emitted"))


def row_success(row: dict[str, str], field: str) -> bool:
    if field == "parse_and_score_success":
        return parse_and_score_success(row)
    return bool_value(row.get(field))


def rate(count: int, total: int) -> str:
    return f"{count / total:.6f}" if total else "0.000000"


def summarize_rows(rows: Iterable[dict[str, str]], label_fields: dict[str, Any]) -> dict[str, Any]:
    material = list(rows)
    total = len(material)
    summary: dict[str, Any] = dict(label_fields)
    summary["rows"] = total
    for field in METRIC_FIELDS:
        count = sum(1 for row in material if row_success(row, field))
        prefix = "hard_cap" if field == "state_hard_cap_used" else field
        summary[f"{prefix}_rows"] = count
        summary[f"{prefix}_rate"] = rate(count, total)
    return summary


def group_summary(rows: list[dict[str, str]], group_field: str, output_field: str | None = None) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[group_field])].append(row)
    field = output_field or group_field
    return [summarize_rows(grouped[key], {field: key}) for key in sorted(grouped)]


def overall_summary(rows: list[dict[str, str]], population: str) -> list[dict[str, Any]]:
    return [summarize_rows(rows, {"population": population})]


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    fieldnames = list(rows[0].keys())
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def markdown_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    fields = list(rows[0].keys())
    lines = [
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join(["---"] * len(fields)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[field]) for field in fields) + " |")
    return "\n".join(lines) + "\n"


def validate_primary_against_status(primary_rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    status_rows = read_csv(STATUS_CSV)
    by_model = {row["model_condition_id"]: row for row in status_rows if row["model_condition_id"] != "TOTAL"}
    observed_by_model = {
        item["model_condition_id"]: item
        for item in group_summary(primary_rows, "model_condition_id")
    }
    observed_total = overall_summary(primary_rows, "primary_clean_v2_7200")[0]

    if set(by_model) != set(PRIMARY_SCORE_FILES):
        failures.append(f"model status ids {sorted(by_model)} do not match primary score files {sorted(PRIMARY_SCORE_FILES)}")

    for model_condition_id, status in sorted(by_model.items()):
        observed = observed_by_model.get(model_condition_id)
        if observed is None:
            failures.append(f"missing observed summary for {model_condition_id}")
            continue
        checks = {
            "score_rows": "rows",
            "backend_error_rows": "backend_error_rows",
            "parse_and_score_success_rows": "parse_and_score_success_rows",
        }
        for status_field, observed_field in checks.items():
            if int(status[status_field]) != int(observed[observed_field]):
                failures.append(
                    f"{model_condition_id}: {status_field}={status[status_field]} "
                    f"!= recomputed {observed_field}={observed[observed_field]}"
                )

    total = next((row for row in status_rows if row["model_condition_id"] == "TOTAL"), None)
    if total is None:
        failures.append("missing TOTAL row in model status CSV")
    else:
        checks = {
            "score_rows": "rows",
            "backend_error_rows": "backend_error_rows",
            "parse_and_score_success_rows": "parse_and_score_success_rows",
        }
        for status_field, observed_field in checks.items():
            if int(total[status_field]) != int(observed_total[observed_field]):
                failures.append(
                    f"TOTAL: {status_field}={total[status_field]} "
                    f"!= recomputed {observed_field}={observed_total[observed_field]}"
                )
    return failures


def build_outputs() -> tuple[dict[str, str], dict[str, Any], list[str]]:
    primary_rows, primary_sources = load_labeled_rows(PRIMARY_SCORE_FILES, "primary_confirmatory_clean_v2")
    budget300_rows, budget300_sources = load_labeled_rows(BUDGET300_SCORE_FILES, "budget300_diagnostic")
    qwen3_rows, qwen3_sources = load_labeled_rows(
        {"openrouter_qwen3_coder_alibaba_supplement": QWEN3_CONFIRMATORY_SCORE},
        "qwen3_coder_supplement_confirmatory",
    )

    failures = validate_primary_against_status(primary_rows)
    if len(primary_rows) != 7200:
        failures.append(f"primary row count is {len(primary_rows)}, expected 7200")
    if len(budget300_rows) != 800:
        failures.append(f"budget300 row count is {len(budget300_rows)}, expected 800")
    if len(qwen3_rows) != 1440:
        failures.append(f"Qwen3-Coder supplement row count is {len(qwen3_rows)}, expected 1440")

    tables: dict[str, list[dict[str, Any]]] = {
        "primary_overall": overall_summary(primary_rows, "primary_clean_v2_7200"),
        "primary_by_model": group_summary(primary_rows, "model_condition_id"),
        "primary_by_method": group_summary(primary_rows, "method"),
        "primary_by_budget": group_summary(primary_rows, "budget"),
        "budget300_diagnostic_overall": overall_summary(budget300_rows, "budget300_diagnostic_800"),
        "budget300_diagnostic_by_model": group_summary(budget300_rows, "model_condition_id"),
        "budget300_diagnostic_by_method": group_summary(budget300_rows, "method"),
        "qwen3_coder_supplement_overall": overall_summary(qwen3_rows, "qwen3_coder_supplement_1440"),
        "qwen3_coder_supplement_by_method": group_summary(qwen3_rows, "method"),
        "qwen3_coder_supplement_by_budget": group_summary(qwen3_rows, "budget"),
    }

    summary = {
        "schema_version": "pcg_dynamic_state_v2.submission_tables_tables.v1",
        "analysis_boundary": {
            "primary_matrix": "clean-v2 five-model confirmatory matrix, 7,200 rows",
            "budget300": "diagnostic sidecar only, excluded from primary claims",
            "qwen3_coder": "open-weight supplement, excluded from primary aggregation",
            "live_api_reproducibility": "saved-output replay verifies recorded outputs; future live APIs are not guaranteed bit-identical",
        },
        "sources": {
            "primary": primary_sources,
            "budget300_diagnostic": budget300_sources,
            "qwen3_coder_supplement": qwen3_sources,
            "model_status": {
                "path": rel(STATUS_CSV),
                "sha256": file_sha256(STATUS_CSV),
                "rows": len(read_csv(STATUS_CSV)),
            },
        },
        "tables": tables,
        "validation_failures": failures,
    }

    outputs: dict[str, str] = {}
    for name, rows in tables.items():
        outputs[f"{name}.csv"] = csv_text(rows)

    outputs["submission_summary.json"] = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

    md_parts = [
        "# Submission Aggregate Tables",
        "",
        "These tables are generated from tracked score CSV files by",
        "`artifact/verification/summarize_submission_tables.py`. They do not call",
        "model APIs or use private files.",
        "",
    ]
    for name in [
        "primary_overall",
        "primary_by_model",
        "primary_by_method",
        "primary_by_budget",
        "budget300_diagnostic_overall",
        "budget300_diagnostic_by_model",
        "budget300_diagnostic_by_method",
        "qwen3_coder_supplement_overall",
        "qwen3_coder_supplement_by_method",
        "qwen3_coder_supplement_by_budget",
    ]:
        md_parts.extend([f"## {name}", "", markdown_table(tables[name])])
    outputs["submission_tables.md"] = "\n".join(md_parts)
    return outputs, summary, failures


def write_outputs(outputs: dict[str, str], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in outputs.items():
        (output_dir / filename).write_text(text, encoding="utf-8", newline="\n")


def check_outputs(outputs: dict[str, str], output_dir: Path) -> list[str]:
    failures: list[str] = []
    for filename, expected in outputs.items():
        path = output_dir / filename
        if not path.exists():
            failures.append(f"missing {rel(path)}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            failures.append(f"content mismatch {rel(path)}")
    expected_names = set(outputs)
    if output_dir.exists():
        for path in output_dir.iterdir():
            if path.is_file() and path.name in OUTPUT_FILES and path.name not in expected_names:
                failures.append(f"unexpected managed file {rel(path)}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--check", action="store_true", help="verify checked-in tables match recomputed outputs")
    args = parser.parse_args()

    outputs, summary, validation_failures = build_outputs()
    if validation_failures:
        print(
            json.dumps(
                {
                    "passed": False,
                    "mode": "validation",
                    "failures": validation_failures,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 1

    if args.check:
        check_failures = check_outputs(outputs, args.output_dir)
        result = {
            "passed": not check_failures,
            "mode": "check",
            "output_dir": rel(args.output_dir),
            "managed_files": sorted(outputs),
            "failures": check_failures,
            "primary_rows": summary["tables"]["primary_overall"][0]["rows"],
            "budget300_rows": summary["tables"]["budget300_diagnostic_overall"][0]["rows"],
            "qwen3_coder_rows": summary["tables"]["qwen3_coder_supplement_overall"][0]["rows"],
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if not check_failures else 1

    write_outputs(outputs, args.output_dir)
    print(
        json.dumps(
            {
                "written": [rel(args.output_dir / filename) for filename in sorted(outputs)],
                "primary_rows": summary["tables"]["primary_overall"][0]["rows"],
                "budget300_rows": summary["tables"]["budget300_diagnostic_overall"][0]["rows"],
                "qwen3_coder_rows": summary["tables"]["qwen3_coder_supplement_overall"][0]["rows"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
