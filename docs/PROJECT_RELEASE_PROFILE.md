# Project reproduction profile

## Validated profile

`SAVED_OUTPUT_OFFLINE_REPLAY`

The package reconstructs paper results from frozen provider responses and deterministic local evidence. It performs no model-provider request.

## Scientific checks

- primary and diagnostic matrix definition;
- VCR request/response fixture consistency;
- H5 hash-lock validation;
- project-defined E5 lineage validation;
- V2 and V3 input reconstruction and scorer replay;
- representation-invariance, metamorphic, and mutation tests;
- V3 executor reconstruction and task-cluster analysis;
- aggregate and model-by-budget result equivalence;
- paper-result provenance mapping;
- package manifest and archive integrity.

## Reproduction levels

- Frozen-result recomputation: verified.
- Offline/VCR replay: verified.
- New model-output generation: not performed.
- External independent reproduction: not yet established.

## Environment

The workflow uses Python 3.10 or newer and the standard library. Archive verification requires `7zz`, `7z`, or `7za`. The documented scientific timezone is UTC. Testing was completed on macOS with Python 3.14.5; cross-platform execution remains unverified.

## Figure boundary

The numeric data underlying claim-bearing tables and figures are replayed. Editable presentation sources and the manuscript are not part of this repository archive.
