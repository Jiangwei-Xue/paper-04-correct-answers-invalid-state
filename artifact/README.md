# Artifact Contents

This directory is organized by artifact role, not by experiment chronology.

Reviewer-facing benchmark and metadata entries:

- `BENCHMARK_CARD.md`: benchmark scope, intended use, failure modes, and
  limitations.
- `metadata/croissant.json`: draft Croissant metadata for anonymous review and
  later hosted release.
- `metadata/CROISSANT_MAPPING.md`: mapping from Croissant objects and record
  sets to artifact files.

## Protocol

- `protocol/main_matrix/`: frozen main-matrix definition, method conditions,
  variable controls, lineage, and decision rules.
- `protocol/main_matrix/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_PROTOCOL_20260629.md`:
  reproducibility-oriented open-weight Qwen3-Coder-480B supplement protocol;
  this is not a sixth primary model condition and includes the disposition of
  non-selected open-weight candidates.
- `protocol/sentinel_drift_probe/`: reserved endpoint-drift audit protocol.
  Sentinel probes are not main results and are not included in primary outcome
  estimation.

The main-matrix protocol fixes `reliable_composite_success` as the primary
metric. `answer_success` and strict `state_governance_success` are paired
decomposition metrics; standalone governance is diagnostic only.

## Results

- `results/main_matrix/`: clean-v2 row-level execution outputs, model status
  files, and VCR closure records for the five primary model conditions. The
  execution layer is closed. submission aggregate tables are stored outside this
  directory under `../paper/submission_tables/`.
- `results/main_matrix/record_mode_20260627/excluded_history/`: retained old
  first-pass/proxy-mediated execution history. It is verifier-backed audit
  history and is excluded from all primary aggregates.
- `results/evidence/ssr_downgrade_20260623/`: verifier-backed SSR downgrade
  evidence packet. This packet is evidence for method disposition, not a
  replacement for the primary main matrix.
- `results/sentinel_drift_probe_results/`: reserved location for endpoint drift
  audit outputs, separated from the primary matrix.

## Raw Outputs And Verification

- `raw_outputs/`: neutral top-level landing area for future saved model outputs.
  Current released raw outputs remain inside the SSR downgrade evidence packet
  because its H5 row manifests reference their historical relative paths.
- `verification/`: reserved location for shared artifact verifiers. Current
  verifiers live inside the evidence packet they verify.

Each evidence packet should state its own scope, released files, verification
commands, and claim boundary.

Responsible-use and release boundaries are documented in:

- `../docs/RAI_ETHICS_LIMITATIONS.md`
- `../docs/HOSTING_AND_RELEASE_PLAN.md`
