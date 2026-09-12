# Reproduction protocol

## Scope

This protocol replays saved model evidence and recomputes deterministic results. It does not regenerate provider responses.

## Complete offline replay

From the extracted package root:

```sh
TZ=UTC python3 scripts/reproduce_public_release.py --archive <ARCHIVE_PATH>
```

The command writes replay products to a temporary directory and performs these stages:

1. validate the supplied archive anchor;
2. audit primary, diagnostic, supplement, and sanity VCR fixtures;
3. validate H5 locks and the project-defined E5 interlock;
4. rebuild V2 inputs and compare production and reference scorers;
5. run V2 property, mutation, executor, and preservation checks;
6. rebuild V3 inputs and scores for all six evidence tiers;
7. run the 10-case by 3-representation invariance suite;
8. reconstruct the 7,200 executor rows and task-cluster analysis;
9. regenerate aggregate V3 and model-by-budget summaries;
10. compare generated scientific fields with released references.

The final line must contain:

```json
{"api_calls_performed": 0, "passed": true}
```

## Package verification

```sh
TZ=UTC python3 tools/VERIFY_ARCHIVE.py verify --archive <ARCHIVE_PATH> --public
TZ=UTC python3 scripts/verify_public_package_v6.py --archive <ARCHIVE_PATH>
```

## Outputs

Replay products are temporary. Reference results remain under `results/`, `reports/`, and `paper/submission_tables/`. Their roles are described in `results/README.md` and `docs/PAPER_RESULTS_MAP.md`.

## Failure interpretation

- A manifest, hash, VCR, H5, E5, score, or result mismatch fails validation.
- A later provider returning different text is outside the replay claim.
- A platform that has not been tested is `NOT_VERIFIED`.
