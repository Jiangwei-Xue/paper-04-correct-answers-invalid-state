#!/usr/bin/env python3
"""Validate the public scientific profile of the PCG V3 GitHub package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
RELEASE_ID = "pcg-v3-github-reproduction-20260913-v8"

REQUIRED_FILES = {
    "README.md",
    "RELEASE_AUDIT.md",
    "LICENSE",
    "LICENSES/README.md",
    "LICENSES/CC-BY-4.0.txt",
    "LICENSES/MIT.txt",
    "LICENSES/THIRD_PARTY.md",
    "Makefile",
    "PUBLIC_ENVIRONMENT.json",
    "PUBLIC_RELEASE_STATUS.json",
    "experiments_manifest.json",
    "results_manifest.json",
    "docs/EXPERIMENT_DESIGN.md",
    "docs/REPRODUCTION_PROTOCOL.md",
    "docs/PAPER_RESULTS_MAP.md",
    "docs/PROJECT_RELEASE_PROFILE.md",
    "results/README.md",
    "scripts/reproduce_public_release.py",
    "scripts/verify_public_package_v6.py",
    "reports/metric_v3/rescore_summary_v3.json",
    "reports/metric_v3/independent_executor_v3_report.json",
    "reports/metric_v3/primary_model_budget_cap_v3.csv",
}

EXPECTED_METADATA = {
    "BUILD_ATTESTATION.json",
    "DOCUMENTATION_ATTESTATION.json",
    "RELEASE_CONFIG.public.json",
    "RELEASE_MANIFEST.jsonl",
    "SHA256SUMS.txt",
    "TOOL_PROVENANCE.json",
}

PRESENTATION_SUFFIXES = {
    ".ppt",
    ".pptx",
    ".pptm",
    ".pot",
    ".potx",
    ".pps",
    ".ppsx",
    ".key",
}

ARCHIVE_SUFFIXES = (".7z", ".zip", ".tar", ".tar.gz", ".tgz")
VCS_DIRECTORIES = {".git", ".hg", ".svn"}
COMMIT_KEYS = {
    "git_commit",
    "commit_sha",
    "repository_commit",
    "experiment_repository_commit",
    "private_repository_commit",
}
HEX_COMMIT = re.compile(r"^[0-9a-fA-F]{7,40}$")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def iter_json_values(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from iter_json_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_json_values(item)


def check_release_identifiers() -> bool:
    for path in ROOT.rglob("*.json"):
        try:
            value = load_json(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return False
        for item in iter_json_values(value):
            for key in COMMIT_KEYS:
                candidate = item.get(key)
                if isinstance(candidate, str) and HEX_COMMIT.fullmatch(candidate):
                    return False
            if item.get("type") == "commit":
                candidate = item.get("ref")
                if isinstance(candidate, str) and HEX_COMMIT.fullmatch(candidate):
                    return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args()

    checks: dict[str, bool] = {}
    checks["Package files"] = args.archive.is_file() and all((ROOT / item).is_file() for item in REQUIRED_FILES)
    checks["Runtime"] = sys.version_info >= (3, 10) and any(shutil.which(name) for name in ("7zz", "7z", "7za"))

    bad_tree_member = False
    nested_archive = False
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in VCS_DIRECTORIES for part in relative.parts):
            bad_tree_member = True
        if path.is_file() and path.suffix.lower() in PRESENTATION_SUFFIXES:
            bad_tree_member = True
        if path.is_file() and path.name not in {args.archive.name}:
            lower = path.name.lower()
            if any(lower.endswith(suffix) for suffix in ARCHIVE_SUFFIXES):
                nested_archive = True
    checks["Repository layout"] = not bad_tree_member and not nested_archive

    metadata_dir = ROOT / "RELEASE_METADATA"
    checks["Release metadata"] = metadata_dir.is_dir() and {
        path.name for path in metadata_dir.iterdir() if path.is_file()
    } == EXPECTED_METADATA

    try:
        public_config = load_json(metadata_dir / "RELEASE_CONFIG.public.json")
        checks["Release definition"] = (
            public_config.get("release_name") == RELEASE_ID
            and public_config.get("public_disclosure_profile") == "minimal"
        )
    except (OSError, json.JSONDecodeError):
        checks["Release definition"] = False

    try:
        experiments = load_json(ROOT / "experiments_manifest.json")
        results = load_json(ROOT / "results_manifest.json")
        checks["Experiment inventory"] = len(experiments.get("experiments", [])) == 6
        checks["Result inventory"] = all(
            key in results
            for key in ("primary", "executor", "model_budget_diagnostic", "paper_tables")
        )
    except (OSError, json.JSONDecodeError):
        checks["Experiment inventory"] = False
        checks["Result inventory"] = False

    try:
        summary = load_json(ROOT / "reports/metric_v3/rescore_summary_v3.json")
        primary = summary["tiers"]["primary"]
        counts = primary["counts"]
        conditional = summary["primary_conditionals"]["P_V3_given_A_final_v2"]
        checks["Primary reference results"] = (
            primary["rows"] == 7200
            and counts["final_answer_success_v2"] == 696
            and counts["carried_state_validity_v3"] == 180
            and counts["joint_final_answer_state_success_v3"] == 173
            and conditional["numerator"] == 173
            and conditional["denominator"] == 696
        )
    except (KeyError, OSError, json.JSONDecodeError, TypeError):
        checks["Primary reference results"] = False

    checks["Scientific versioning"] = check_release_identifiers()
    checks["Layered licensing"] = all(
        (ROOT / relative).is_file()
        for relative in (
            "LICENSES/CC-BY-4.0.txt",
            "LICENSES/MIT.txt",
            "LICENSES/THIRD_PARTY.md",
        )
    )

    status = "PASS" if all(checks.values()) else "FAIL"
    for label, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {label}")
    print(f"PACKAGE VALIDATION: {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
