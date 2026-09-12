# Main Matrix Record-Mode Batch Log

Created UTC: 2026-06-26T17:26:41Z.

Scope: PCG dynamic-state v2 main-matrix record-mode execution.

This is an execution audit log. It does not modify the frozen main-matrix
protocol, row manifests, model axis, method axis, request controls, scorer,
parser, retry policy, exclusion policy, or statistical analysis plan.

## Reason For Batched Execution

Record-mode execution is being run in batches because each batch must produce
auditable VCR `record -> replay -> audit` closure before execution continues.
After a batch finishes, the operator checks cassette coverage, cache-miss
status, raw-response hashes, replay outputs, score records, and related hash
artifacts. This avoids discovering a broken provider-recording or replay chain
only after the full 7,200-row run has completed.

The paper team also has limited human operator capacity and cannot continuously
supervise all five model conditions in one uninterrupted run. Human supervision
is needed for operational checks, not for outcome-dependent decisions.

Batching, pausing, and resuming are operational controls only. They are not
based on answer success, state-governance success, reliable-composite success,
method ranking, model ranking, budget effects, or any other outcome observed
during the run.

## Non-Intervention Commitments

- Continue from the frozen row manifests.
- Do not delete completed rows.
- Do not selectively rerun rows because of low scores, wrong answers, malformed
  but recorded model behavior, or inconvenient carried state.
- Do not change prompts, configs, request controls, provider routes, parser,
  scorer, aggregation scripts, or exclusion rules during execution.
- Preserve raw outputs, provider metadata, attempt logs, response/error hashes,
  VCR cassette records, replay outputs, score records, and post-run hash
  manifests.
- Treat invalid JSON, parser failure, backend failure after the frozen retry
  policy, timeout, provider error, unverifiable final answer, and unverifiable
  carried state as row outcomes under the frozen analysis plan.
- Record any protocol-level violation separately before any corrective action.

## Batch Events

Append new rows to this table when a model batch starts, pauses, resumes, or
finishes.

| event_utc | event | model_condition_id | row_scope | completed_rows | reason | outcome_reviewed_before_decision | protocol_changed | rows_deleted | selective_rerun | notes |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| 2026-06-26T17:26:41Z | log_created_after_record_mode_started | not_applicable | not_recorded_in_this_entry |  | VCR record/replay/audit closure and limited human operator capacity; execution will be supervised in batches | not_asserted_for_prior_work; record explicitly in later entries | false | false | false | This log begins as an execution audit supplement after record-mode had already started. It records the operational batching reason and does not change the frozen protocol. |
| 2026-06-26T17:31:49Z | batch_completed_and_pause_requested | `deepseek_v4pro` | confirmatory_primary model slice | 1440 | Completed DeepSeek first, then paused before Qwen per operator instruction | engineering closure reviewed after completion only: row count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 1440/1440; backend-error rows 3 retained as row outcomes; Qwen not started |
| 2026-06-26T18:57:43Z | batch_completed | `qwen37max` | confirmatory_primary model slice | 1440 | Completed Qwen after explicit operator instruction to enter Qwen | engineering closure reviewed after completion only: row count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 1414/1440; backend-error rows 46 and parse-failure rows 26 retained as row outcomes; Kimi not started |
| 2026-06-27T01:23:21Z | batch_completed | `kimi_k26` | confirmatory_primary model slice | 1440 | Completed Kimi after prior batches; VCR closure generated from adapter source with no API calls | engineering closure reviewed after completion only: row count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 1405/1440; backend-error rows 73 and parse-failure rows 35 retained as row outcomes; remaining model conditions not started in this entry |
| 2026-06-27T02:19:59Z | batch_paused_for_backend_error_heterogeneity | `openrouter_gpt55` | confirmatory_primary model slice | 395 | GPT showed high provider-specific raw backend-error during formal execution; admission smoke had not exposed this instability | engineering review of backend-error heterogeneity only; valid-output rows not reviewed for replacement and not rerun | false | false | false | GPT partial frozen at 395/1440 attempted rows; 361 valid outputs locked; 34 retry-eligible infrastructure failures; 1045 unattempted rows; pause packet created under `EXECUTION_PAUSE_BACKEND_ERROR_HETEROGENEITY_20260627_101959` |
| 2026-06-27T03:36:00Z | claude_next_execution_decision_recorded | `openrouter_claude48` | confirmatory_primary model slice, not yet started | 0 | GPT/OpenRouter root-cause attribution remains unresolved, but Claude is a separate admitted model condition | engineering execution-order decision only; no GPT recovery or outcome-dependent rerun authorized | false | false | false | Claude may proceed under registered 10-concurrency policy with backend-error pause guard; GPT remains paused and deferred until after Claude |
| 2026-06-27T04:20:09Z | claude_manual_stop_after_32_rows | `openrouter_claude48` | confirmatory_primary model slice partial run | 32 | Manual operator stop for coordination after a short run segment; not triggered by backend-error threshold | engineering row-count/hash check only; no outcome-dependent rerun decision | false | false | false | Existing 32 Claude rows remain first-run outputs; backend-error 0/32; parse+score 31/32; future Claude execution must resume and skip completed adapter rows, not rerun them |
| 2026-06-27T04:29:47Z | claude_backend_error_guard_pause | `openrouter_claude48` | confirmatory_primary model slice partial run | 128 | Registered Claude backend-error guard triggered during 10-concurrency resume | engineering backend-error guard only; no outcome-dependent rerun decision | false | false | false | Claude paused at 128 attempted rows; backend-error 14/128; latest rolling 100-row backend-error rate 14/100; pause packet `CLAUDE_PAUSE_BACKEND_ERROR_GUARD_20260627_042947`; further Claude provider calls require a separate documented execution decision |
| 2026-06-27T05:30:00Z | openrouter_clean_v2_refreeze_recorded | `openrouter_gpt55`; `openrouter_claude48` | clean-v2 from-zero OpenRouter primary slices | 0 | Earlier OpenRouter GPT/Claude attempts used execution conditions that should not be pooled into primary slices; clean-v2 restarts both OpenRouter model conditions from row zero | engineering protocol review only; no model outputs selected, deleted, or replaced | true | false | false | Clean-v2 keeps max-workers 10, enables explicit OpenRouter runtime controls, and halts immediately on the first detected local transport-path failure with a sidecar recording failure class, exception type, sanitized message, in-flight rows, and queued rows |
| 2026-06-27T11:57:38Z | network_environment_smoke_completed | `openrouter_claude48` | network/runtime canary, not primary | 20 | Substantially optimized the execution network environment after local OpenRouter transport instability; tested hardened Claude path | engineering network/runtime canary only; no outcome-dependent primary decision | false | false | false | `cloud_smoke_20260627` completed 20/20 parse+score with backend-error 0/20 and 80 API calls; synced locally and closed through VCR record/replay/audit with cache miss 0; not pooled into clean-v2 primary results |
| 2026-06-27T16:52:14Z | clean_v2_batch_completed | `openrouter_claude48` | clean-v2 confirmatory_primary model slice | 1440 | Completed Claude from row zero under the substantially optimized execution network environment and hardened OpenRouter controls | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 1439/1440; backend-error rows 0; parse-failure row 1 retained as row outcome; HTTP 200 1440/1440; VCR audit cache miss 0; earlier Claude first-pass rows remain diagnostic only |
| 2026-06-28T13:11:50Z | all_model_direct_network_v2_protocol_recorded | `deepseek_v4pro`; `qwen37max`; `kimi_k26`; `openrouter_gpt55`; `openrouter_claude48` | final v2 primary matrix, all model conditions from row zero | 0 | Claude direct-network transition evidence showed 0 backend-error rows, and review of v1 logs found proxy/transport-like backend evidence not exposed by admission; proxy-mediated execution was therefore recognized as an uncontrolled v1 execution-environment condition | engineering execution-environment review only; no model outputs selected, deleted, or replaced | true | false | false | `V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md` supersedes the OpenRouter-only clean-v2 primary plan for final aggregation; all v1 outputs remain append-only audit evidence and are not pooled with v2 direct-network rows |
| 2026-06-28T14:50:43Z | clean_v2_batch_completed | `openrouter_gpt55` | clean-v2 confirmatory_primary model slice | 1440 | Completed GPT from row zero under the same clean-v2 OpenRouter runtime-hardening controls used for Claude, in the adjusted direct-network execution environment | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 1433/1440; backend-error rows 0; parse-failure rows 7 retained as row outcomes; HTTP 200 1440/1440; VCR audit cache miss 0; earlier GPT first-pass rows remain diagnostic only |
| 2026-06-28T17:00:13Z | all_model_direct_clean_v2_batch_completed | `deepseek_v4pro` | all-model v2 direct-network confirmatory_primary model slice | 1440 | Completed DeepSeek from row zero under the all-model v2 direct-network execution protocol | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 1434/1440; backend-error rows 6; one final-call RemoteDisconnected backend row and five backend-metadata rows with successful final HTTP 200 parse-success outputs retained as row outcomes; VCR audit cache miss 0; earlier DeepSeek v1 slice and 23-row launch fragment remain diagnostic/audit evidence only |
| 2026-06-28T18:32:41Z | all_model_direct_clean_v2_batch_completed | `qwen37max` | all-model v2 direct-network confirmatory_primary model slice | 1440 | Completed Qwen from row zero under the all-model v2 direct-network execution protocol | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 1440/1440; backend-error rows 0; HTTP 200 1440/1440; VCR audit cache miss 0; earlier Qwen v1 slice remains append-only audit evidence only |
| 2026-06-29T03:26:44Z | all_model_direct_clean_v2_batch_completed | `kimi_k26` | all-model v2 direct-network confirmatory_primary model slice | 1440 | Completed Kimi from row zero under the all-model v2 direct-network execution protocol | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 1438/1440; backend-error rows 7; two final-call timeout backend rows and five backend-metadata parse-success rows retained as row outcomes; VCR audit cache miss 0; earlier Kimi v1 slice remains append-only audit evidence only |
| 2026-06-29T03:41:45Z | budget300_direct_network_diagnostic_boundary_recorded | `openrouter_gpt55`; `openrouter_claude48`; `deepseek_v4pro`; `qwen37max`; `kimi_k26` | planned v2 direct-network budget300_diagnostic sidecar | 0 | Before any 800-row budget-300 diagnostic execution, the analysis boundary was recorded explicitly | no budget-300 diagnostic outcomes exist yet; decision is protocol-boundary only and not outcome-dependent | true | false | false | `BUDGET300_DIRECT_NETWORK_DIAGNOSTIC_PROTOCOL_20260629.md` defines the 800-row run as diagnostic only: excluded from primary claim tables, confirmatory mixed-effects models, method ranking, and overall method averages; allowed only for floor-effect, truncation, and carry-failure diagnosis |
| 2026-06-29T03:54:54Z | budget300_direct_network_diagnostic_batch_completed | `openrouter_claude48` | v2 direct-network budget300_diagnostic sidecar model slice | 160 | Completed Claude budget-300 diagnostic sidecar after the diagnostic boundary was recorded | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 158/160; backend-error rows 0; API calls 960; VCR audit cache miss 0 and failure 0; hash manifest 15 rows verified with 0 failures; excluded from primary claim tables, confirmatory mixed-effects models, method ranking, and overall method averages |
| 2026-06-29T03:59:40Z | budget300_direct_network_diagnostic_batch_completed | `openrouter_gpt55` | v2 direct-network budget300_diagnostic sidecar model slice | 160 | Completed GPT budget-300 diagnostic sidecar after the Claude diagnostic sidecar completed | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 160/160; backend-error rows 0; API calls 960; VCR audit cache miss 0 and failure 0; hash manifest 15 rows verified with 0 failures; excluded from primary claim tables, confirmatory mixed-effects models, method ranking, and overall method averages |
| 2026-06-29T04:53:56Z | budget300_direct_network_diagnostic_batch_completed | `deepseek_v4pro` | v2 direct-network budget300_diagnostic sidecar model slice | 160 | Completed DeepSeek budget-300 diagnostic sidecar after the diagnostic boundary was recorded | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 160/160; backend-error rows 0; API calls 960; VCR audit cache miss 0 and failure 0; hash manifest 15 rows verified with 0 failures; excluded from primary claim tables, confirmatory mixed-effects models, method ranking, and overall method averages |
| 2026-06-29T05:00:04Z | budget300_direct_network_diagnostic_batch_completed | `qwen37max` | v2 direct-network budget300_diagnostic sidecar model slice | 160 | Completed Qwen budget-300 diagnostic sidecar after the DeepSeek diagnostic sidecar completed | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 160/160; backend-error rows 0; API calls 960; VCR audit cache miss 0 and failure 0; hash manifest 15 rows verified with 0 failures; excluded from primary claim tables, confirmatory mixed-effects models, method ranking, and overall method averages |
| 2026-06-29T05:08:32Z | budget300_direct_network_diagnostic_batch_completed | `kimi_k26` | v2 direct-network budget300_diagnostic sidecar model slice | 160 | Completed Kimi budget-300 diagnostic sidecar after the Qwen diagnostic sidecar completed | engineering closure reviewed after completion only: row count, backend count, VCR record/replay/audit, cache miss count, and hash manifest; no outcome-dependent rerun decision | false | false | false | parse+score 160/160; backend-error rows 0; API calls 960; VCR audit cache miss 0 and failure 0; hash manifest 15 rows verified with 0 failures; excluded from primary claim tables, confirmatory mixed-effects models, method ranking, and overall method averages |
| 2026-06-29T05:08:32Z | budget300_direct_network_diagnostic_sidecar_closed | `openrouter_gpt55`; `openrouter_claude48`; `deepseek_v4pro`; `qwen37max`; `kimi_k26` | full 800-row v2 direct-network budget300_diagnostic sidecar | 800 | All five model-condition diagnostic slices completed and closed through VCR audit and hash-manifest verification | engineering closure reviewed after completion only: aggregate row counts, backend count, VCR record/replay/audit, cache miss count, and hash manifests; no outcome-dependent rerun decision | false | false | false | aggregate parse+score 798/800; backend-error rows 0; API calls 4800; VCR audit cache miss 0 and failure 0; aggregate hash manifest rows 75 verified with 0 failures; closure packet `BUDGET300_DIAGNOSTIC_DIRECT_V2_EXECUTION_CLOSURE_20260629.md` |

## Required Evidence Per Completed Batch

For each completed batch, retain or reference:

- frozen config sha256;
- row manifest sha256;
- model condition id;
- expected row count;
- completed row count;
- raw output location;
- cassette path and sha256;
- replay output path and sha256;
- score output path and sha256;
- attempt log path and sha256;
- hash/H5 manifest path and sha256, when available.
