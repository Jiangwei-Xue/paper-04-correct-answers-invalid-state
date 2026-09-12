#!/usr/bin/env python3
"""One-command offline replay for the public PCG V3 release.

The script consumes only files retained in the release. It performs no network
or model-provider calls. Archive integrity is handled by the canonical embedded
verifier; this entry point covers the scientific replay chain.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TIERS = (
    "primary",
    "primary_budget300",
    "qwen",
    "qwen_budget300",
    "deepseek_sanity",
    "deterministic_validity_suite",
)
EXPECTED_TIER_ROWS = {
    "primary": 7200,
    "primary_budget300": 800,
    "qwen": 1440,
    "qwen_budget300": 160,
    "deepseek_sanity": 40,
    "deterministic_validity_suite": 36000,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compare_json(expected: Path, actual: Path, label: str) -> None:
    if load_json(expected) != load_json(actual):
        raise RuntimeError(f"{label} JSON mismatch: {expected} != {actual}")


def compare_bytes(expected: Path, actual: Path, label: str) -> None:
    if sha256(expected) != sha256(actual):
        raise RuntimeError(f"{label} byte mismatch: {expected} != {actual}")


def run(args: list[str], *, label: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    print(f"== {label} ==", flush=True)
    env = {
        key: value
        for key, value in os.environ.items()
        if key in {"PATH", "LANG", "LC_ALL", "SYSTEMROOT", "COMSPEC", "TMPDIR", "TEMP", "TMP"}
    }
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["NO_PROXY"] = "*"
    env["no_proxy"] = "*"
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip(), flush=True)
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr, flush=True)
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed with return code {result.returncode}")
    return result


def resolve_retained_source(source_file: str) -> Path:
    normalized = source_file.replace("\\", "/")
    marker = "/artifact/"
    if marker in normalized:
        return ROOT / "artifact" / normalized.split(marker, 1)[1]
    if normalized.startswith("artifact/"):
        return ROOT / normalized
    raise RuntimeError(f"source path has no retained artifact boundary: {source_file}")


def load_build_v2_module():
    path = ROOT / "scripts" / "build_metric_v2_inputs.py"
    spec = importlib.util.spec_from_file_location("public_build_metric_v2_inputs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load V2 input builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_v2_input_lineage() -> dict[str, int]:
    builder = load_build_v2_module()
    checked: dict[str, int] = {}
    for tier in TIERS:
        input_path = ROOT / "results" / "metric_v2" / "raw_inputs" / f"{tier}.jsonl"
        current_source: Path | None = None
        current_handle = None
        current_line = 0
        current_hash = ""
        rows = 0
        try:
            for public_row in read_jsonl(input_path):
                source = resolve_retained_source(str(public_row["source_file"]))
                if source != current_source:
                    if current_handle is not None:
                        current_handle.close()
                    if not source.is_file():
                        raise RuntimeError(f"missing retained raw source: {source.relative_to(ROOT)}")
                    current_source = source
                    current_handle = source.open("r", encoding="utf-8")
                    current_line = 0
                    current_hash = sha256(source)
                if current_hash != public_row["source_file_sha256"]:
                    raise RuntimeError(f"retained source hash mismatch: {source.relative_to(ROOT)}")
                target_line = int(public_row["source_line_number"])
                if target_line <= current_line:
                    current_handle.close()
                    current_handle = source.open("r", encoding="utf-8")
                    current_line = 0
                source_record = None
                while current_line < target_line:
                    line = current_handle.readline()
                    if not line:
                        break
                    current_line += 1
                    if current_line == target_line:
                        source_record = json.loads(line)
                if source_record is None:
                    raise RuntimeError(f"missing source line {target_line}: {source.relative_to(ROOT)}")
                rebuilt = builder.normalize(source_record, source, target_line, current_hash)
                rebuilt.pop("source_file", None)
                expected = dict(public_row)
                expected.pop("source_file", None)
                if canonical(rebuilt) != canonical(expected):
                    raise RuntimeError(f"V2 normalized-row mismatch in {tier}: {public_row['row_id']}")
                rows += 1
        finally:
            if current_handle is not None:
                current_handle.close()
        if rows != EXPECTED_TIER_ROWS[tier]:
            raise RuntimeError(f"V2 lineage row count mismatch for {tier}: {rows}")
        checked[tier] = rows
    return checked


def vcr_audit() -> dict[str, int]:
    record_root = ROOT / "artifact" / "results" / "main_matrix" / "record_mode_20260627"
    pairs: list[tuple[Path, Path]] = []
    for config in sorted(record_root.rglob("*.config.json")):
        if "excluded_history" in config.parts:
            continue
        cassette = config.with_name(config.name.replace(".config.json", ".cassette.jsonl"))
        if cassette.exists():
            pairs.append((config, cassette))
    failures = []
    rows_checked = 0
    entries_checked = 0
    for config, cassette in pairs:
        result = run(
            [
                sys.executable,
                "artifact/verification/main_matrix_vcr_runner.py",
                "--mode",
                "audit",
                "--config",
                str(config.relative_to(ROOT)),
                "--cassette",
                str(cassette.relative_to(ROOT)),
            ],
            label=f"VCR audit {config.parent.name}/{config.stem}",
        )
        value = json.loads(result.stdout)
        rows_checked += int(value.get("rows_checked", 0))
        entries_checked += int(value.get("cassette_entries_checked", 0))
        if value.get("failure_count") or value.get("cache_miss_count"):
            failures.append(str(config.relative_to(ROOT)))
    if failures or len(pairs) != 13 or rows_checked != 9616 or entries_checked != 9616:
        raise RuntimeError(
            f"VCR audit mismatch: configs={len(pairs)} rows={rows_checked} "
            f"entries={entries_checked} failures={failures[:3]}"
        )
    return {"configs": len(pairs), "rows": rows_checked, "cassette_entries": entries_checked}


def verify_v2_scores(temp: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    sidecar = "results/metric_v2/oracles_v2/main_matrix_v1.sidecar.jsonl"
    for tier in TIERS:
        input_path = f"results/metric_v2/raw_inputs/{tier}.jsonl"
        prod = temp / "v2" / f"{tier}.production.jsonl"
        ref = temp / "v2" / f"{tier}.reference.jsonl"
        run(
            [sys.executable, "-m", "metric_v2.production_scorer", "--sidecar", sidecar, "--outputs", input_path, "--out", str(prod)],
            label=f"V2 production scorer {tier}",
        )
        run(
            [sys.executable, "metric_v2/reference_scorer/reference_scorer.py", "--sidecar", sidecar, "--outputs", input_path, "--out", str(ref)],
            label=f"V2 reference scorer {tier}",
        )
        compare_bytes(ROOT / f"results/metric_v2/scores_v2/{tier}.production.jsonl", prod, f"V2 production {tier}")
        compare_bytes(ROOT / f"results/metric_v2/scores_v2/{tier}.reference.jsonl", ref, f"V2 reference {tier}")
        counts[tier] = count_jsonl(prod)
    return counts


def verify_v2_executor(temp: Path) -> None:
    generated = temp / "v2" / "independent_executor_report.json"
    run(
        [
            sys.executable,
            "scripts/independent_executor.py",
            "--inputs",
            "results/metric_v2/raw_inputs/primary.jsonl",
            "--sidecar",
            "results/metric_v2/oracles_v2/main_matrix_v1.sidecar.jsonl",
            "--scores",
            "results/metric_v2/scores_v2/primary.production.jsonl",
            "--out",
            str(generated),
        ],
        label="V2 independent executor",
    )
    compare_json(ROOT / "reports/metric_v2/independent_executor_report.json", generated, "V2 executor")


def verify_v3(temp: Path) -> dict[str, int]:
    spec_manifest = load_json(ROOT / "reports/metric_v3/v3_spec_hash.json")
    for key, relative in (
        ("spec_sha256", spec_manifest["spec"]),
        ("suite_sha256", spec_manifest["suite"]),
        ("analysis_plan_sha256", spec_manifest["analysis_plan"]),
        ("adapter_sha256", "metric_v3/adapters.py"),
        ("evaluator_sha256", "metric_v3/evaluator.py"),
        ("serializer_sha256", "metric_v3/serialize.py"),
    ):
        if sha256(ROOT / relative) != spec_manifest[key]:
            raise RuntimeError(f"V3 frozen hash mismatch: {relative}")

    v2_source = "results/metric_v2/oracles_v2/main_matrix_v1.sidecar.jsonl"
    sidecar = temp / "v3" / "main_matrix_v1.sidecar.jsonl"
    sidecar_manifest = temp / "v3" / "oracles_v3_manifest.json"
    run(
        [sys.executable, "scripts/derive_metric_v3_oracles.py", "--source", v2_source, "--out", str(sidecar), "--manifest", str(sidecar_manifest)],
        label="V3 oracle derivation",
    )
    compare_bytes(ROOT / "results/metric_v3/oracles_v3/main_matrix_v1.sidecar.jsonl", sidecar, "V3 oracle sidecar")

    scores: list[str] = []
    counts: dict[str, int] = {}
    for tier in TIERS:
        rebuilt_input = temp / "v3" / "inputs" / f"{tier}.jsonl"
        rebuilt_score = temp / "v3" / "scores" / f"{tier}.production.jsonl"
        run(
            [
                sys.executable,
                "scripts/build_metric_v3_inputs.py",
                "--raw",
                f"results/metric_v2/raw_inputs/{tier}.jsonl",
                "--score-v2",
                f"results/metric_v2/scores_v2/{tier}.production_with_v1.jsonl",
                "--out",
                str(rebuilt_input),
            ],
            label=f"V3 input rebuild {tier}",
        )
        compare_bytes(ROOT / f"results/metric_v3/inputs/{tier}.jsonl", rebuilt_input, f"V3 input {tier}")
        run(
            [sys.executable, "scripts/score_metric_v3.py", "--inputs", str(rebuilt_input), "--sidecar", str(sidecar), "--out", str(rebuilt_score)],
            label=f"V3 scorer {tier}",
        )
        compare_bytes(ROOT / f"results/metric_v3/scores_v3/{tier}.production.jsonl", rebuilt_score, f"V3 score {tier}")
        counts[tier] = count_jsonl(rebuilt_score)
        scores.append(str(rebuilt_score))

    invariance = temp / "v3" / "representation_invariance_suite.json"
    run([sys.executable, "scripts/test_metric_v3_invariance.py", "--report", str(invariance)], label="V3 representation invariance")
    compare_json(ROOT / "reports/metric_v3/gates/representation_invariance_suite.json", invariance, "V3 invariance")

    executor_rows = temp / "v3" / "primary.executor.jsonl"
    executor_report = temp / "v3" / "independent_executor_v3_report.json"
    run(
        [
            sys.executable,
            "scripts/independent_executor_v3.py",
            "--inputs",
            str(temp / "v3" / "inputs" / "primary.jsonl"),
            "--sidecar",
            str(sidecar),
            "--out",
            str(executor_rows),
        ],
        label="V3 independent executor rows",
    )
    compare_bytes(ROOT / "results/metric_v3/executor/primary.executor.jsonl", executor_rows, "V3 executor rows")
    run(
        [
            sys.executable,
            "scripts/analyze_metric_v3_executor.py",
            "--scores",
            str(temp / "v3" / "scores" / "primary.production.jsonl"),
            "--executor",
            str(executor_rows),
            "--out",
            str(executor_report),
            "--bootstrap-replicates",
            "10000",
            "--seed",
            "20260813",
        ],
        label="V3 task-cluster executor analysis",
    )
    compare_json(ROOT / "reports/metric_v3/independent_executor_v3_report.json", executor_report, "V3 executor report")

    summary = temp / "v3" / "rescore_summary_v3.json"
    summarize_args = [sys.executable, "scripts/summarize_metric_v3.py"]
    for score in scores:
        summarize_args.extend(["--scores", score])
    summarize_args.extend(
        [
            "--primary-v2-scores",
            "results/metric_v2/scores_v2/primary.production_with_v1.jsonl",
            "--executor-report",
            str(executor_report),
            "--out",
            str(summary),
        ]
    )
    run(summarize_args, label="V3 aggregate summary")
    expected_summary = load_json(ROOT / "reports/metric_v3/rescore_summary_v3.json")
    actual_summary = load_json(summary)
    expected_summary.pop("executor_report", None)
    actual_summary.pop("executor_report", None)
    if expected_summary != actual_summary:
        raise RuntimeError("V3 aggregate summary mismatch")

    cap_table = temp / "v3" / "primary_model_budget_cap_v3.csv"
    run(
        [
            sys.executable,
            "scripts/summarize_metric_v3_model_budget_cap.py",
            "--inputs",
            str(temp / "v3" / "inputs" / "primary.jsonl"),
            "--scores",
            str(temp / "v3" / "scores" / "primary.production.jsonl"),
            "--artifact-root",
            "artifact",
            "--out",
            str(cap_table),
        ],
        label="V3 model-budget hard-cap table",
    )
    compare_bytes(ROOT / "reports/metric_v3/primary_model_budget_cap_v3.csv", cap_table, "V3 hard-cap table")

    primary = load_json(summary)["primary_conditionals"]
    if primary["P_V3_given_A_final_v2"]["numerator"] != 173 or primary["P_V3_given_A_final_v2"]["denominator"] != 696:
        raise RuntimeError("V3 primary conditional count mismatch")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path, help="Downloaded release archive; used as an explicit reproduction anchor.")
    args = parser.parse_args()
    if not args.archive.is_file():
        raise SystemExit(f"archive not found: {args.archive}")

    print("PCG V3 saved-output offline replay: provider calls = 0", flush=True)
    # Some frozen verifiers record output paths relative to the repository.
    # Keep the ephemeral replay tree under the extracted release root and let
    # TemporaryDirectory remove it after all comparisons finish.
    with tempfile.TemporaryDirectory(prefix=".pcg-v3-public-replay-", dir=ROOT) as temp_raw:
        temp = Path(temp_raw)

        run([sys.executable, "artifact/verification/verify_main_matrix_freeze.py"], label="main-matrix freeze")
        run([sys.executable, "artifact/verification/replay_main_matrix_from_cassettes.py", "--output-dir", str(temp / "main_matrix_replay")], label="primary cassette scorer replay")
        vcr = vcr_audit()
        run([sys.executable, "artifact/verification/replay_ssr_downgrade_from_saved_outputs.py", "--compact"], label="SSR saved-output replay")
        run([sys.executable, "artifact/results/evidence/ssr_downgrade_20260623/verify_public_hash_locks.py"], label="SSR public H5 hash locks")
        run([sys.executable, "artifact/results/evidence/ssr_downgrade_20260623/verify_e5_interlock.py"], label="SSR E5 interlock")
        run([sys.executable, "artifact/verification/summarize_budget_300_diagnostic.py", "--check"], label="budget diagnostic frozen summary")
        baseline_build = ROOT / ".verification_build"
        if baseline_build.exists():
            raise RuntimeError("refusing to replace pre-existing .verification_build")
        try:
            run(
                [sys.executable, "artifact/verification/run_minimal_baseline_validity_suite.py", "--check"],
                label="deterministic validity suite",
            )
        finally:
            shutil.rmtree(baseline_build, ignore_errors=True)
        run(
            [sys.executable, "artifact/verification/run_deepseek_v4pro_api_sanity.py", "--check"],
            label="DeepSeek sanity cassette replay",
        )
        run([sys.executable, "artifact/verification/summarize_submission_tables.py", "--check"], label="legacy submission-table freeze")
        load_json(ROOT / "artifact/metadata/croissant.json")

        v2_lineage = verify_v2_input_lineage()
        v2_scores = verify_v2_scores(temp)
        property_before = sha256(ROOT / "reports/metric_v2/property_mutation_report.json")
        run([sys.executable, "scripts/test_metric_v2_properties.py"], label="V2 metamorphic and mutation suite")
        if sha256(ROOT / "reports/metric_v2/property_mutation_report.json") != property_before:
            raise RuntimeError("V2 property/mutation report changed during replay")
        verify_v2_executor(temp)
        v3_scores = verify_v3(temp)

    result = {
        "api_calls_performed": 0,
        "e5_interlock_verified": True,
        "h5_hash_locks_verified": True,
        "passed": True,
        "v2_lineage_rows": sum(v2_lineage.values()),
        "v2_score_rows": sum(v2_scores.values()),
        "v3_score_rows": sum(v3_scores.values()),
        "vcr_cassette_entries": vcr["cassette_entries"],
        "vcr_configs": vcr["configs"],
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
