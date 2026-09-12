# Budget 300 Diagnostic Evidence

Budget `300` is not a confirmatory budget level.  The released pilot rows show
that this regime frequently hits the state budget cap.  Key carry conditions
also have much lower success at this budget.  It is useful as a stress probe.
It is not clean enough for primary method ranking.

## Source Rows

This packet is a derived summary.  It reads only released rows from the scoped
SSR downgrade evidence packet:

- `artifact/results/evidence/ssr_downgrade_20260623/results/_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100/CONTROLLED_ROWS.jsonl`
- `artifact/results/evidence/ssr_downgrade_20260623/results/_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl`
- `artifact/results/evidence/ssr_downgrade_20260623/results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl`

These three direct-provider pilot packets contain `540` rows:

```text
3 models x 10 tasks x 6 methods x 3 budgets x 1 run = 540 rows
```

Each budget level contributes `180` rows.

## Main Numbers

`hard_cap_any` means that the row-level `state_hard_cap_used` flag is true, or
at least one `compiler_audits[]` entry has `state_hard_cap_used=true`.

| budget | rows | hard-cap rows | hard-cap rate | answer success | reliable success |
|---:|---:|---:|---:|---:|---:|
| 300 | 180 | 154 | 0.856 | 19/180 | 6/180 |
| 600 | 180 | 72 | 0.400 | 36/180 | 10/180 |
| 1200 | 180 | 18 | 0.100 | 31/180 | 12/180 |

The carry mechanism shows the practical effect.  For
`rolling_visible_carry_forward`, answer success is `4/30` at budget `300`,
`22/30` at budget `600`, and `20/30` at budget `1200`.  Reliable success is
`1/30`, `8/30`, and `10/30`.

## Interpretation

The evidence supports a bounded claim:

> Budget `300` shows frequent state hard-capping and low success for key carry
> conditions in the released pilot rows.  It should be reported as a low-budget
> diagnostic probe, not as a confirmatory budget level.

The evidence does not support a broader claim that every method always floors at
budget `300`.  `300` remains useful for diagnosing truncation, carry failure,
and boundary behavior under extreme state compression.

## Reproduce

From the repository root:

```bash
python3 artifact/verification/summarize_budget_300_diagnostic.py --check
```

Generated files:

- `budget_300_summary.json`
- `budget_300_by_method_budget.csv`
