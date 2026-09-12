#!/usr/bin/env python3
"""Build the budget-300 diagnostic evidence summary from released pilot rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from io import StringIO
from pathlib import Path
from statistics import mean, median
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
EVIDENCE_ROOT = REPO_ROOT / "artifact" / "results" / "evidence" / "ssr_downgrade_20260623"
OUTPUT_DIR = REPO_ROOT / "artifact" / "results" / "evidence" / "budget_300_diagnostic_20260625"

SOURCE_FILES = [
    "results/_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100/CONTROLLED_ROWS.jsonl",
    "results/_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl",
    "results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl",
]


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_rows(evidence_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel_path in SOURCE_FILES:
        path = evidence_root / rel_path
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                row["_source_file"] = rel_path
                row["_source_line"] = line_number
                rows.append(row)
    return rows


def hard_cap_any(row: dict[str, Any]) -> bool:
    if row.get("state_hard_cap_used"):
        return True
    audits = row.get("compiler_audits") or []
    return any(bool(audit.get("state_hard_cap_used")) for audit in audits if isinstance(audit, dict))


def audit_chars(row: dict[str, Any], field: str) -> list[int]:
    values: list[int] = []
    for audit in row.get("compiler_audits") or []:
        if isinstance(audit, dict) and field in audit:
            values.append(int(audit[field]))
    return values


def rate(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    before = [value for row in rows for value in audit_chars(row, "state_chars_before_budget")]
    after = [value for row in rows for value in audit_chars(row, "state_chars_after_budget")]
    hard_cap_count = sum(1 for row in rows if hard_cap_any(row))
    answer_count = sum(1 for row in rows if row.get("answer_success"))
    reliable_count = sum(1 for row in rows if row.get("reliable_success") or row.get("reliable_composite_success"))
    governance_count = sum(1 for row in rows if row.get("state_governance_success"))
    final_exact_count = sum(1 for row in rows if row.get("final_exact_success"))
    summary: dict[str, Any] = {
        "rows": len(rows),
        "hard_cap_any_count": hard_cap_count,
        "hard_cap_any_rate": rate(hard_cap_count, len(rows)),
        "answer_success_count": answer_count,
        "answer_success_rate": rate(answer_count, len(rows)),
        "reliable_success_count": reliable_count,
        "reliable_success_rate": rate(reliable_count, len(rows)),
        "state_governance_success_count": governance_count,
        "state_governance_success_rate": rate(governance_count, len(rows)),
        "final_exact_success_count": final_exact_count,
        "final_exact_success_rate": rate(final_exact_count, len(rows)),
    }
    if before:
        summary["state_chars_before_budget"] = {
            "mean": round(mean(before), 1),
            "median": median(before),
            "max": max(before),
        }
    if after:
        summary["state_chars_after_budget"] = {
            "mean": round(mean(after), 1),
            "median": median(after),
            "max": max(after),
        }
    return summary


def build_summary(evidence_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows = read_rows(evidence_root)
    by_budget: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_method_budget: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        budget = int(row["budget"])
        by_budget[budget].append(row)
        by_method_budget[(str(row["method"]), budget)].append(row)

    method_budget_rows: list[dict[str, Any]] = []
    for (method, budget), group in sorted(by_method_budget.items()):
        item = {"method": method, "budget": budget}
        item.update(summarize_group(group))
        method_budget_rows.append(item)

    sample_hard_cap_rows = []
    for row in rows:
        if int(row["budget"]) != 300 or not hard_cap_any(row):
            continue
        before = audit_chars(row, "state_chars_before_budget")
        after = audit_chars(row, "state_chars_after_budget")
        sample_hard_cap_rows.append(
            {
                "global_artifact_id": row["global_artifact_id"],
                "source_file": row["_source_file"],
                "source_line": row["_source_line"],
                "method": row["method"],
                "budget": int(row["budget"]),
                "answer_success": bool(row.get("answer_success")),
                "reliable_success": bool(row.get("reliable_success") or row.get("reliable_composite_success")),
                "state_chars_before_budget_first": before[0] if before else None,
                "state_chars_after_budget_first": after[0] if after else None,
                "state_hard_cap_used": True,
            }
        )
        if len(sample_hard_cap_rows) == 5:
            break

    source_files = [
        {
            "path": rel_path,
            "sha256": file_sha256(evidence_root / rel_path),
            "rows": sum(1 for row in rows if row["_source_file"] == rel_path),
        }
        for rel_path in SOURCE_FILES
    ]
    summary = {
        "schema_version": "budget_300_diagnostic_evidence.v1",
        "source_packet": "artifact/results/evidence/ssr_downgrade_20260623",
        "source_files": source_files,
        "definition": {
            "hard_cap_any": "row.state_hard_cap_used OR any compiler_audits[].state_hard_cap_used",
            "rows_analyzed": "three direct-provider random10 PCG dynamic-state v2 pilot packets",
            "scope": "diagnostic evidence for budget-axis disposition, not primary outcome estimation",
        },
        "aggregate_by_budget": {str(budget): summarize_group(group) for budget, group in sorted(by_budget.items())},
        "aggregate_by_method_budget": method_budget_rows,
        "sample_hard_cap_rows": sample_hard_cap_rows,
        "interpretation": [
            "Budget 300 shows a much higher state hard-cap rate than 600 or 1200 in the released pilot rows.",
            "The 300 rows are evidence for a low-budget diagnostic regime, not a confirmatory budget level.",
            "The evidence supports a bounded claim about frequent hard-capping and low success in key carry conditions; it does not prove that every method always floors at 300.",
        ],
    }
    return summary, method_budget_rows


def render_csv(rows: list[dict[str, Any]]) -> str:
    fields = [
        "method",
        "budget",
        "rows",
        "hard_cap_any_count",
        "hard_cap_any_rate",
        "answer_success_count",
        "answer_success_rate",
        "reliable_success_count",
        "reliable_success_rate",
        "state_governance_success_count",
        "state_governance_success_rate",
        "final_exact_success_count",
        "final_exact_success_rate",
    ]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, default=EVIDENCE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    summary, method_budget_rows = build_summary(args.evidence_root)
    json_text = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    csv_text = render_csv(method_budget_rows)

    output_dir = args.output_dir
    json_path = output_dir / "budget_300_summary.json"
    csv_path = output_dir / "budget_300_by_method_budget.csv"

    if args.check:
        failures = []
        if not json_path.exists() or json_path.read_text(encoding="utf-8") != json_text:
            failures.append(str(json_path))
        if not csv_path.exists() or csv_path.read_text(encoding="utf-8") != csv_text:
            failures.append(str(csv_path))
        result = {"passed": not failures, "checked": [str(json_path), str(csv_path)], "failures": failures}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if not failures else 1

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json_text, encoding="utf-8", newline="\n")
    csv_path.write_text(csv_text, encoding="utf-8", newline="\n")
    print(json.dumps({"written": [str(json_path), str(csv_path)]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
