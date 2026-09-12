# _probe_ecvs_deepseek_v4pro_harder_stress_v1_2mode20_readeraware_vs_schemaaware_attempt3_15task_2method_3budget_1run Run Plan

Positioning: `calibration_only_not_primary_evidence`.

This plan is prepared for a later user-confirmed API run. It is not a result.

## Matrix

- Tasks: 15 harder stress v1 tasks
- Methods: `rolling_visible_carry_forward2.0(reader_aware)`, `mature_ssr_loop2.0(schema_aware)`
- Budgets: 300, 600, 1200
- Runs: 1
- Expected rows: 90
- Provider/model: DeepSeek direct `deepseek-v4-pro`

## Safety

- Prompt construction uses only `MODEL_VISIBLE_TASK_MANIFEST.jsonl` / `model_visible_task_content`.
- Scoring uses `SCORER_ORACLE_MANIFEST.jsonl` only after provider output is captured.
- Failed rows and retry attempts are preserved.
- Backend errors are `rerun_required`.
- Positive reasoning tokens or returned reasoning content are `excluded`.
- Parse failures remain measured rows.

## Command After User Confirmation

```bash
cd <local-pilot-repo>
python3 tools/run_ecvs_deepseek_harder_stress_v1_2mode20_readeraware_vs_schemaaware_attempt3.py --run-api --max-workers 100
```
