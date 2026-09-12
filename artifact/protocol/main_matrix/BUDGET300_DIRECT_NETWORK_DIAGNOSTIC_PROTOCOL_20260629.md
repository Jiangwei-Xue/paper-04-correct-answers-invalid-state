# Budget-300 Direct-Network Diagnostic Protocol

Status: diagnostic execution protocol

Created UTC: 2026-06-29T00:00:00Z

Scope: the 800-row budget-300 diagnostic probe for PCG dynamic-state v2.

## Role

The budget-300 run is a v2 direct-network diagnostic probe. It is not a
confirmatory primary-matrix extension, not a primary backfill, and not a
replacement for any row in the 7,200-row confirmatory matrix.

The diagnostic shape is:

```text
40 tasks x 5 models x 4 core methods x 1 budget x 1 run = 800 rows
```

Each model condition contributes 160 rows.

## Analysis Boundary

Budget-300 diagnostic rows must not enter:

- primary claim tables;
- confirmatory mixed-effects models;
- method ranking;
- overall method averages.

The only intended use is descriptive floor-effect, truncation, and carry-failure
diagnosis under extreme state compression.

## Execution Boundary

If executed after clean-v2 primary closure, the 800 rows must be recorded under a
separate diagnostic namespace, for example:

```text
artifact/results/main_matrix/record_mode_20260627/BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/
```

The run must use role `budget300_diagnostic` and preserve its own:

- model-slice configs;
- controlled rows;
- adapter-source rows;
- scores JSONL and CSV;
- VCR cassettes;
- replay outputs;
- VCR audit outputs;
- run reports;
- hash manifests;
- runner logs.

These artifacts may be cited as diagnostic evidence. They must not be pooled with
the clean-v2 confirmatory primary matrix.

## Relationship To Clean-V2 Primary Matrix

The clean-v2 confirmatory primary matrix remains:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

The budget-300 diagnostic probe can be run next, but completing it does not alter
the closed primary-matrix row count, primary analysis population, or primary
claim boundary.
