#!/usr/bin/env python3
"""Verify independence and coverage claims of the executor report."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    report = json.loads(Path("reports/metric_v2/independent_executor_report.json").read_text(encoding="utf-8"))
    family_count = len(report.get("family_counts", {}))
    bootstrap = report.get("task_cluster_bootstrap", {}).get("executor_rate", {})
    passed = (
        report.get("rows") == 7200
        and report.get("task_count") == 40
        and family_count == 5
        and report.get("executor_independence", {}).get("final_answer_read") is False
        and report.get("executor_independence", {}).get("scorer_labels_read_by_executor") is False
        and report.get("executor_independence", {}).get("production_scorer_imported") is False
        and report.get("executor_independence", {}).get("reference_scorer_imported") is False
        and bootstrap.get("replicates") == 10000
    )
    result = {"schema": "metric_v2_executor_verification.v1", "network_calls_performed": 0, "passed": passed, "rows": report.get("rows"), "task_count": report.get("task_count"), "family_count": family_count, "bootstrap_replicates": bootstrap.get("replicates")}
    Path("reports/metric_v2/executor_verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
