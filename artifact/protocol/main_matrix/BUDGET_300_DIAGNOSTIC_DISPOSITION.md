# Budget 300 Diagnostic Disposition

Budget `300` is outside the confirmatory budget axis.

The current main matrix uses budgets `600` and `1200`:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

Budget `300` is retained as a separate diagnostic probe:

```text
40 tasks x 5 models x 4 core methods x 1 budget x 1 run = 800 rows
```

## Evidence Basis

The decision is based on released PCG dynamic-state v2 random10 pilot rows, not
on a completed main-matrix outcome table.

Derived evidence lives in:

```text
artifact/results/evidence/budget_300_diagnostic_20260625/
```

The summary covers `540` direct-provider pilot rows.  Each budget level has
`180` rows.  The state hard-cap rate is:

| budget | hard-cap rows | hard-cap rate |
|---:|---:|---:|
| 300 | 154/180 | 0.856 |
| 600 | 72/180 | 0.400 |
| 1200 | 18/180 | 0.100 |

For the key carry condition `rolling_visible_carry_forward`, answer success is
`4/30` at budget `300`, compared with `22/30` at budget `600` and `20/30` at
budget `1200`.

This is enough to classify `300` as a low-budget stress regime.  It is not a
clean confirmatory level for method ranking.

## Analysis Rule

When executed after the clean-v2 primary matrix, the budget-300 run is a v2
direct-network diagnostic probe. It is not a confirmatory primary-matrix
extension, not a primary backfill, and not a replacement for any 7,200-row
confirmatory primary row.

Rows from the `300` diagnostic probe must not enter:

- primary claim tables;
- confirmatory mixed-effects models;
- method ranking;
- overall method averages.

Report `300` descriptively. The intended use is floor-effect, truncation, and carry-failure analysis under extreme state compression.

## Method Boundary

This is not a method change.  The method axis remains:

- `loop_only`;
- `rolling_summary`;
- `rolling_visible_carry_forward`;
- `rolling_visible_fields_only`;
- `ssr_no_visible_carry`;
- `mature_ssr_loop`.

The budget disposition changes the analysis plan.  It does not rename, add, or
remove a method condition.
