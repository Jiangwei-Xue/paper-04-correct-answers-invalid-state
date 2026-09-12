# Main Matrix Results

This directory holds the main-matrix execution records for the 7,200-row
confirmatory matrix and related diagnostic sidecars.

The clean-v2 five-model row-level execution layer is complete. The repository
also retains the earlier v1 proxy-mediated record-mode outputs, the OpenRouter
clean-v2 transition evidence, the later all-model v2 direct-network protocol
decision, and the completed all-model v2 direct-network slices. Final primary
aggregation should use the v2 direct-network from-zero matrix only, not a mix
of v1 and v2 rows. Paper-level aggregation tables, statistical interpretation,
and venue-facing claim tables remain in separate manuscript/release layers. The
submission descriptive aggregate tables are frozen under
`paper/submission_tables/`.

Included audit evidence:

- `record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/deepseek_v4pro/confirmatory/`:
  DeepSeek all-model v2 direct-network slice, 1,440/1,440 rows from row zero,
  backend-error 6/1,440, parse+score 1,434/1,440, VCR
  record/replay/audit closed with zero cache misses. This is the current v2
  DeepSeek primary-candidate slice.
- `record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/qwen37max/confirmatory/`:
  Qwen all-model v2 direct-network slice, 1,440/1,440 rows from row zero,
  backend-error 0/1,440, parse+score 1,440/1,440, VCR
  record/replay/audit closed with zero cache misses. This is the current v2
  Qwen primary-candidate slice.
- `record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/kimi_k26/confirmatory/`:
  Kimi all-model v2 direct-network slice, 1,440/1,440 rows from row zero,
  backend-error 7/1,440, parse+score 1,438/1,440, VCR
  record/replay/audit closed with zero cache misses. This is the current v2
  Kimi primary-candidate slice.
- `record_mode_20260627/deepseek_v4pro/confirmatory/`: DeepSeek confirmatory
  v1 slice, 1,440/1,440 rows, VCR record/replay/audit closed with zero cache
  misses. Retained as v1 audit evidence after the all-model v2 decision.
- `record_mode_20260627/qwen37max/confirmatory/`: Qwen confirmatory slice,
  1,440/1,440 rows, VCR record/replay/audit closed with zero cache misses.
  Retained as v1 audit evidence after review found proxy/transport-like
  backend signatures in part of the v1 logs.
- `record_mode_20260627/kimi_k26/confirmatory/`: Kimi confirmatory slice,
  1,440/1,440 rows, VCR record/replay/audit closed with zero cache misses.
  Retained as v1 audit evidence after review found proxy/transport-like
  backend signatures in part of the v1 logs.
- `record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627/openrouter_claude48/confirmatory/`:
  Claude clean-v2 transition slice, 1,440/1,440 rows from row zero,
  backend-error 0/1,440, parse+score 1,439/1,440, VCR
  record/replay/audit closed with zero cache misses.
- `record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627/openrouter_gpt55/confirmatory/`:
  GPT clean-v2 transition slice, 1,440/1,440 rows from row zero,
  backend-error 0/1,440, parse+score 1,433/1,440, VCR
  record/replay/audit closed with zero cache misses.

The five budget-300 slices below share the same boundary: they are retained for
diagnosis and remain outside the primary evidence surface.

- `record_mode_20260627/BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/openrouter_claude48/budget300_diagnostic/`:
  Claude v2 direct-network budget-300 diagnostic sidecar slice, 160/160 rows,
  backend-error 0/160, parse+score 158/160, VCR record/replay/audit closed
  with zero cache misses.
- `record_mode_20260627/BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/openrouter_gpt55/budget300_diagnostic/`:
  GPT v2 direct-network budget-300 diagnostic sidecar slice, 160/160 rows,
  backend-error 0/160, parse+score 160/160, VCR record/replay/audit closed
  with zero cache misses.
- `record_mode_20260627/BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/deepseek_v4pro/budget300_diagnostic/`:
  DeepSeek v2 direct-network budget-300 diagnostic sidecar slice, 160/160 rows,
  backend-error 0/160, parse+score 160/160, VCR record/replay/audit closed with
  zero cache misses.
- `record_mode_20260627/BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/qwen37max/budget300_diagnostic/`:
  Qwen v2 direct-network budget-300 diagnostic sidecar slice, 160/160 rows,
  backend-error 0/160, parse+score 160/160, VCR record/replay/audit closed with
  zero cache misses.
- `record_mode_20260627/BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/kimi_k26/budget300_diagnostic/`:
  Kimi v2 direct-network budget-300 diagnostic sidecar slice, 160/160 rows,
  backend-error 0/160, parse+score 160/160, VCR record/replay/audit closed with
  zero cache misses.
- `record_mode_20260627/openrouter_gpt55/confirmatory/`: GPT first-pass
  diagnostic partial slice, 395/1,440 planned rows attempted, paused before
  completion because of backend-error heterogeneity.
- `record_mode_20260627/openrouter_claude48/confirmatory/`: Claude first-pass
  diagnostic partial slice, 128/1,440 planned rows attempted, paused by the
  backend-error guard.
- `record_mode_20260627/EXECUTION_PAUSE_BACKEND_ERROR_HETEROGENEITY_20260627_101959/`:
  append-only pause/audit packet for the GPT runtime exception.
- `cloud_smoke_20260627/openrouter_claude48/confirmatory/`: 20-row
  network/runtime canary for the hardened Claude path, synced into this
  repository and closed through local VCR record/replay/audit. This packet is
  not a primary clean-v2 slice and must not be pooled into primary results.

The OpenRouter GPT/Claude primary slices follow the clean-v2 from-zero
protocol:

```text
../../protocol/main_matrix/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_PROTOCOL_20260627.md
```

That OpenRouter-only plan is now historical. The broader all-model v2
direct-network protocol is:

```text
../../protocol/main_matrix/V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```

The v1 outputs remain append-only audit history and help explain why v2 was
introduced. They are not pooled with v2 direct-network rows in the final
primary result table.

Reference benchmark card and metadata:

- `../../BENCHMARK_CARD.md`
- `../../metadata/croissant.json`
- `../../metadata/CROISSANT_MAPPING.md`

Paper-level submission contents live outside this results directory:

- `../../../paper/submission_tables/RESULTS_FREEZE.md`
- `../../../paper/submission_tables/tables/`

Final public-release hosting metadata, DOI fields, and manuscript claim wording
stay in separate release/manuscript layers.

Admission probes, sentinel probes, historical calibration rows, and
method-disposition evidence packets belong outside this results layer. The
800-row budget-`300` run is a v2 direct-network diagnostic probe: it remains
outside primary claim tables, confirmatory mixed-effects models, method ranking,
and overall method averages, and is used for floor-effect, truncation, and
carry-failure diagnosis.
