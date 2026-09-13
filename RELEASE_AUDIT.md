# Scientific reproducibility release audit

## Scope

Release ID: `pcg-v3-github-reproduction-20260913-v8`.

The validated scope is saved-output offline replay. The package recomputes the paper's retained deterministic results without generating new provider responses.

## Experiment inventory

The machine-readable inventory contains six experiment records covering the 7,200-row primary matrix, the 800-row budget diagnostic, the Qwen supplement, the DeepSeek sanity set, the deterministic validity suite, and the V3 executor analysis.

## Experimental design

The public design record specifies the 40-task matrix, five model conditions, six state-transfer protocols, confirmatory budgets, repetitions, control conditions, prompt construction, retry policy, scorer definitions, and task-cluster analysis. The budget-300 rows and model supplements remain outside the primary denominator.

## Reproduction scaffolding

The package retains input builders, production and reference scorers, formal property and mutation checks, representation adapters, VCR fixtures, H5/E5 validators, executor reconstruction, aggregation code, and reference results. `scripts/reproduce_public_release.py` executes the complete saved-output workflow.

## Data and input provenance

The benchmark tasks are synthetic. Frozen task manifests, scorer-only oracles, experiment rows, provider-request controls, and saved responses are retained with content hashes and row identifiers. No external dataset download is required for offline replay.

## Result provenance

`experiments_manifest.json`, `results_manifest.json`, and `docs/PAPER_RESULTS_MAP.md` link each claim-bearing result to its configuration, normalized input, row-level score, aggregate report, and replay stage.

## Dependencies and environment

The workflow requires Python 3.10 or newer and the Python standard library. Archive validation additionally requires a 7-Zip command-line implementation. The documented scientific timezone is UTC. The verified compatibility target is macOS with Python 3.14.5; other operating systems remain untested.

## Validation and reproduction

The release build executes the documented archive verifier, full scientific replay, and package-profile verifier on a fresh extraction. The scientific replay covers 9,616 VCR entries, H5 and E5 interlocks, 45,640 V2/V3 rows, representation invariance, executor reconstruction, and aggregate equivalence.

## Result equivalence

All deterministic reference comparisons are exact. The primary denominator remains 7,200 rows; final-answer success remains 696 rows; answer-aligned V3 validity remains 180 rows; and joint answer/state success remains 173 rows. The task-cluster executor report is regenerated using the frozen analysis seed and compared with the released reference.

## Figure and table provenance

Claim-bearing numeric tables are reproducible from row-level results. Legacy submission tables are retained under `paper/submission_tables/tables/`. Editable presentation sources and the manuscript are outside this repository archive.

## Paper-result mapping

The principal answer/state decomposition, protocol profiles, component counts, hard-cap diagnostic, representation gate, and method-blocked executor results are mapped in `docs/PAPER_RESULTS_MAP.md`.

## Archive and manifest integrity

`RELEASE_METADATA/RELEASE_MANIFEST.jsonl` and `RELEASE_METADATA/SHA256SUMS.txt` define the released members. The canonical builder requires duplicate byte-identical construction, clean extraction, extracted-tree validation, documentation-command execution, and final archive verification.

## Scientific limitations

The package validates saved evidence and deterministic analysis. It does not establish that a future provider call will return identical text, test arbitrary unseen state representations, or constitute an external independent reproduction.

## Validation matrix

| Check | Status | Public evidence |
|---|---|---|
| Experiment definition | PASS | `docs/EXPERIMENT_DESIGN.md`, `experiments_manifest.json` |
| Reproduction scaffolding | PASS | `scripts/reproduce_public_release.py` and retained modules |
| Input/data provenance | PASS | task, oracle, row, and results manifests |
| Result provenance | PASS | `results_manifest.json`, `docs/PAPER_RESULTS_MAP.md` |
| Dependency validation | PASS | `requirements.txt`, `PUBLIC_ENVIRONMENT.json` |
| Unit and property tests | PASS | V2 properties, mutants, and V3 invariance suite |
| Offline/VCR replay | PASS | 13 configurations and 9,616 cassette entries |
| H5 validation | PASS | project-defined hash locks |
| E5 validation | PASS | project-defined lineage interlock |
| Full declared reproduction | PASS | complete saved-output offline replay |
| Expected-result equivalence | PASS | exact deterministic comparisons |
| Figure/table provenance | PASS | mapped numeric tables and generation stages |
| Paper/result mapping | PASS | `docs/PAPER_RESULTS_MAP.md` |
| Bundled paper consistency | N/A | manuscript not bundled |
| Release-manifest integrity | PASS | final manifest closure |
| Archive integrity | PASS | canonical final-archive verification |

PACKAGE VALIDATION: PASS
