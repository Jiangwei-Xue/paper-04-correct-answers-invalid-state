# PCG V3 carried-state reproduction package

This repository reconstructs the paper's claim-bearing results from saved model responses. The verified workflow checks the experiment definition, VCR fixtures, H5 locks, E5 lineage, V2 and V3 scoring, representation invariance, executable-criterion analysis, and aggregate tables without making provider requests.


Corresponding preprint: **When Correct Answers Carry Invalid State: Evaluating Explicit State Carriers in Stateful LLM Agents**, by Jiangwei Xue, Zhida Qin, and Yuda Bi.
DOI: [10.5281/zenodo.22720976](https://doi.org/10.5281/zenodo.22720976).
Reproducibility repository: [https://github.com/Jiangwei-Xue/paper-04-correct-answers-invalid-state](https://github.com/Jiangwei-Xue/paper-04-correct-answers-invalid-state).
Reproduction release: `pcg-v3-github-reproduction-20260912-v7`.
The PDF and complete LaTeX source are supplied separately; `LATEST_PAPER.json` binds their public hashes to this release.

## Reproduction scope

- Verified: saved-output offline replay and deterministic result recomputation.
- Verified: VCR, H5, E5, scorer, executor, aggregate, and expected-result checks.
- Not included: new paid model calls or a claim that future provider responses will be byte-identical.
- Not yet claimed: execution by an independent external research group.

## Requirements

- Python 3.10 or newer; tested with Python 3.14.5.
- `7zz`, `7z`, or `7za` on `PATH` for archive verification.
- At least 2 GB of free space for temporary replay products.
- Python standard library only.

The reproduction semantics do not depend on local time. `TZ=UTC` is used for the documented workflow.

## Quick start

After downloading the release archive:

```sh
7zz x pcg-v3-github-reproduction-20260912-v7.7z
cd pcg-v3-github-reproduction-20260912-v7
python3 scripts/reproduce_public_release.py --archive ../pcg-v3-github-reproduction-20260912-v7.7z
```

The final JSON object must contain `"passed": true` and `"api_calls_performed": 0`.

## One-command verification

<!-- RELEASE_COMMAND:verify -->
```sh
python3 tools/VERIFY_ARCHIVE.py verify --archive <ARCHIVE_PATH> --public
```
<!-- END_RELEASE_COMMAND:verify -->

## Scientific replay

<!-- RELEASE_COMMAND:reproduce -->
```sh
python3 scripts/reproduce_public_release.py --archive <ARCHIVE_PATH>
```
<!-- END_RELEASE_COMMAND:reproduce -->

## Package-profile verification

<!-- RELEASE_COMMAND:profile -->
```sh
python3 scripts/verify_public_package_v6.py --archive <ARCHIVE_PATH>
```
<!-- END_RELEASE_COMMAND:profile -->

The same operations are available as `make verify-release`, `make reproduce`, and `make verify-profile`.

## Evidence surfaces

| Surface | Rows or cases | Validation |
|---|---:|---|
| Primary matrix | 7,200 | VCR and deterministic V2/V3 scoring |
| Budget-300 diagnostic | 800 | VCR and frozen-summary checks |
| Qwen supplement | 1,600 | VCR and V2/V3 scoring |
| DeepSeek sanity | 40 | Saved-cassette replay and V2/V3 scoring |
| Deterministic validity suite | 36,000 | Local regeneration and scorer validation |
| V3 executor analysis | 7,200 | Executor reconstruction and task-cluster bootstrap |
| Representation gate | 10 cases x 3 formats | Representation-invariance verification |

## Documentation map

- `docs/EXPERIMENT_DESIGN.md`: research question, matrix, controls, models, prompts, randomness, retries, and evaluation.
- `docs/REPRODUCTION_PROTOCOL.md`: replay stages and expected outputs.
- `docs/PAPER_RESULTS_MAP.md`: claim-to-input, score, report, and generation mapping.
- `docs/PROJECT_RELEASE_PROFILE.md`: supported scientific scope and limitations.
- `results/README.md`: row-level, intermediate, reference, and aggregate result surfaces.
- `experiments_manifest.json`: machine-readable experiment records.
- `results_manifest.json`: machine-readable result provenance.
- `RELEASE_AUDIT.md`: scientific reproducibility status.

## Licensing

This repository uses layered licensing:

- project-authored analysis, scoring, replay, and verification code:
  MIT License;
- project-authored documentation and derived aggregate tables:
  CC BY 4.0;
- saved provider records, model outputs, benchmark-derived material,
  public data, and third-party content: their original applicable terms.

The manuscript is not bundled in this repository. The separately
published CC BY 4.0 preprint is available at
https://doi.org/10.5281/zenodo.22720976.

See `LICENSE`, `LICENSES/README.md`, and
`LICENSES/THIRD_PARTY.md` for the controlling path and material
boundaries. No single license applies to the repository as a whole.

## Publication metadata verification

<!-- RELEASE_COMMAND:publication -->
```sh
python3 scripts/verify_publication_metadata.py --archive <ARCHIVE_PATH>
```
<!-- END_RELEASE_COMMAND:publication -->
