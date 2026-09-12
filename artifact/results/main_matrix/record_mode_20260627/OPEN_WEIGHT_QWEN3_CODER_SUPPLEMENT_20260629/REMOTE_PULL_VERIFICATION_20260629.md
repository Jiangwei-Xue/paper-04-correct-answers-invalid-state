# Qwen3-Coder Open-Weight Supplement Remote Pull Verification

Date: 2026-06-29

Scope: local receipt and verification note for the Qwen3-Coder open-weight
supplement. This note does not change the frozen run protocol or request
controls.

## Remote Run

- Run id: `20260629T112443Z`
- Remote status: `COMPLETE`
- Remote finished at UTC: `2026-06-29T12:15:54Z`
- Network execution recorded by run summaries: `direct_no_system_proxy`
- Model condition: `openrouter_qwen3_coder_alibaba_supplement`
- Scope flag: `open_weight_supplement=true`
- Primary matrix flag: `primary_analysis_eligible=false`

## Local Receipt

- Local result directory:
  `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/`
- Local private archive filename:
  `qwen3_coder480b_supplement_20260629T112443Z_results.tar.gz`
- Archive SHA-256:
  `186ca376882e31ff6877d04f37cd4a206f5d88219134a1e74ea5e9b5f5d41d8b`

## Phase Summary

| phase | rows | backend | parse-and-score success | returned-model match | reasoning content | nonzero reasoning tokens | VCR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| admission | 16/16 | 0 | 16 | 16 | 0 | 0 | complete |
| confirmatory | 1440/1440 | 0 | 1439 | 1440 | 0 | 0 | complete |
| budget300_diagnostic | 160/160 | 0 | 160 | 160 | 0 | 0 | complete |

Admission decision: `ADMIT_OPEN_WEIGHT_SUPPLEMENT`.

The only parse failure is a non-backend, HTTP-200, returned-model-matched
confirmatory row:

```text
pcgds_v2_00014_permission_boundary_with_attractive_blocked_path_hard::openrouter_qwen3_coder_alibaba_supplement::loop_only::budget600::run1
```

## Local Verification

The pulled archive was checked against the remote SHA-256 value. The extracted
result files were then checked against `HASH_MANIFEST.admission.jsonl`,
`HASH_MANIFEST.confirmatory.jsonl`, and
`HASH_MANIFEST.budget300_diagnostic.jsonl`; no missing files or hash
mismatches were observed.

VCR audit logs report `failure_count=0` for admission, confirmatory, and
budget300 diagnostic phases.
