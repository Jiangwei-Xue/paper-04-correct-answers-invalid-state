# Main Matrix Protocol

This directory contains the reviewer-facing main-matrix protocol. It defines
the intended primary experiment design and separates it from scoped evidence
packets.

For benchmark-level reading, start with `../../BENCHMARK_CARD.md`. Croissant
metadata and mapping notes are under `../../metadata/`.

Current primary design:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

The confirmatory budget levels are `600` and `1200`. Budget `300` is retained
only as a separate low-budget diagnostic probe:

```text
40 tasks x 5 models x 4 core methods x 1 budget x 1 run = 800 rows
```

The evidence basis and analysis boundary for this split are recorded in
`BUDGET_300_DIAGNOSTIC_DISPOSITION.md`. The execution boundary for running those
800 rows after clean-v2 primary closure is recorded in
`BUDGET300_DIRECT_NETWORK_DIAGNOSTIC_PROTOCOL_20260629.md`.

The planned open-weight supplemental model is Qwen3-Coder-480B through a fixed
Alibaba OpenRouter route. Its reproducibility rationale, route controls,
reasoning boundary, reporting exclusion from primary aggregation, and
non-selected candidate disposition are recorded in
`OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_PROTOCOL_20260629.md`.

The primary metric is `reliable_composite_success`. `answer_success` and strict
`state_governance_success` are paired decomposition metrics, and standalone
governance is diagnostic only. This rule is fixed in
`PREREGISTERED_DECISION_RULES.md`.

The primary inference rule is fixed in `STATISTICAL_ANALYSIS_PLAN.md`:
confirmatory method contrasts use design-based paired risk differences within
matched task x model x budget x run blocks, with task-cluster bootstrap
confidence intervals. GLMMs are sensitivity analyses, not the primary arbiter.

The paper-level framing and research questions are fixed in
`PAPER_FRAMING_AND_RQS.md`: this is a measurement paper about reliable
co-success and scoped answer-governance non-overlap, not a new memory method or
a universal SSR-failure claim.

The pre-execution freeze/admission packet is under:

```text
artifact/protocol/main_matrix/configs/
artifact/protocol/main_matrix/admission/
```

It contains the generated `7,200`-row confirmatory row manifest, the separate
`800`-row budget-`300` diagnostic row manifest, a variable freeze spec, a
provider-policy snapshot, model-admission criteria, provider live-refresh
records, benchmark-smoke admission packets, and a hash manifest. Its historical
admission decision was `READY_FOR_MAIN_RECORD_MODE`: all five frozen model
conditions had benchmark smoke packets and were marked `ADMIT_MODEL`. That
decision authorized record-mode execution under the frozen protocol. It is
retained as admission provenance, not as the current execution status.

The clean-v2 row-level primary execution closure is recorded under:

```text
artifact/results/main_matrix/
```

The submission paper-level aggregate result tables are frozen under:

```text
paper/submission_tables/
```

The current final primary execution decision is all-model v2 direct-network
from row zero:

```text
artifact/protocol/main_matrix/V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```

This execution-environment decision preserves the 7,200-row matrix definition
while preventing proxy-mediated v1 rows and direct-network v2 rows from being
pooled in the final primary table.

The currently included SSR downgrade packet is located at:

```text
artifact/results/evidence/ssr_downgrade_20260623/
```

That packet justifies a method-disposition decision. It does not replace the
primary matrix and should not be pooled into primary outcome estimation.

Files in this directory:

- `EXPERIMENT_VARIABLE_CONTROL_OVERVIEW.md`: reviewer-facing single-entry
  summary of matrix axes, frozen controls, and source-file authority.
- `FINAL_MAIN_MATRIX_DEFINITION.md`: axes and row count.
- `METHOD_CONDITIONS.md`: method arms and their roles.
- `PAPER_FRAMING_AND_RQS.md`: paper framing, RQs, and language boundaries.
- `VARIABLE_CONTROL.md`: frozen variables and disallowed pooling.
- `MAIN_RUN_API_POLICY.md`: retry, timeout, concurrency, cache, and missingness
  policy used to govern live record-mode execution.
- `OPENROUTER_POST_PAUSE_RUNTIME_HARDENING_20260627.md`: opt-in OpenRouter
  clean-v2 runtime-hardening mode, covering explicit provider order, disabled
  context compression, metadata header capture, bounded HTTP backoff, and
  halt-on-local-transport-failure controls.
- `NETWORK_TRANSPORT_FAILURE_CLASSIFICATION_AND_RECOVERY_POLICY_20260627.md`:
  separates confirmed local transport-path failures from provider/backend errors
  and model-output failures, and defines the targeted recovery boundary.
- `../../results/main_matrix/record_mode_20260627/OPENROUTER_NETWORK_ENVIRONMENT_EXECUTION_LOG_20260627.md`:
  reviewer-facing execution log for the OpenRouter GPT/Claude network/transport
  instability event and the resulting halt-on-transport-failure control.
- `OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_PROTOCOL_20260627.md`: clean-v2
  decision to restart GPT/Claude from row zero under hardened OpenRouter
  controls, excluding earlier GPT/Claude attempts from primary pooling. This is
  historical after the later all-model direct-network v2 decision.
- `V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md`: final v2 decision to
  rerun all five admitted model conditions from row zero under a unified direct
  network execution environment, while preserving v1 proxy-mediated logs as
  audit evidence.
- `BUDGET_300_DIAGNOSTIC_DISPOSITION.md`: evidence and reporting rule for
  keeping budget `300` out of confirmatory inference.
- `BUDGET300_DIRECT_NETWORK_DIAGNOSTIC_PROTOCOL_20260629.md`: execution and
  analysis boundary for the separate 800-row v2 direct-network diagnostic probe.
- `OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_PROTOCOL_20260629.md`: rationale and
  parameter-control protocol for the open-weight Qwen3-Coder-480B supplemental
  experiment, including disposition of non-selected open-weight candidates; it
  is not a sixth primary model condition.
- `MODEL_AXIS_DISPOSITION.md`: why candidate endpoints such as GLM-family and
  Gemini-family endpoints are not part of the frozen primary model axis.
- `admission/OPENROUTER_VARIABLE_CONTROL_20260626.md`: OpenRouter-specific
  provider-route controls for GPT/Claude and their admission boundary.
- `PROTOCOL_LINEAGE.md`: why the design moved from earlier planning states to
  the current 7,200-row confirmatory matrix plus 800-row low-budget diagnostic
  probe.
- `PREREGISTERED_DECISION_RULES.md`: outcome and reporting rules.
- `STATISTICAL_ANALYSIS_PLAN.md`: primary estimand, task-cluster bootstrap,
  contrast hierarchy, failure coding, and diagnostic exclusions.
- `LEGACY_RESULT_DISPOSITION.md`: how older runs may and may not be used.
- `configs/`: generated main-matrix and diagnostic config/row manifests.
- `admission/`: new-repo admission gate, model-admission criteria, variable
  freeze spec, provider policy snapshot, hash manifest, and admission tables.

Responsible-use and hosting boundaries are documented in
`../../../docs/RAI_ETHICS_LIMITATIONS.md` and
`../../../docs/HOSTING_AND_RELEASE_PLAN.md`.
