# Hosting And Release Plan

This document records how the artifact should be made accessible during
anonymous review and after public release. It does not change the experiment
design.

## Current Anonymous-Review Mode

During anonymous review, the artifact is distributed as an anonymized archive or
anonymous repository. Reviewers should not need API keys, provider accounts, or
private requests to inspect the evidence included in the package.

Reviewer-visible package contents:

- protocol and variable-control documents;
- task, oracle, config, and row manifests;
- clean-v2 row-level execution closure records;
- scoped saved-output evidence packets;
- offline verifier scripts;
- hash manifests and replay cassettes;
- benchmark card, RAI/limitations note, and Croissant metadata draft.

Excluded from release:

- local-only directories;
- credentials and `.env` files;
- private chats and local planning notes;
- non-anonymized logs;
- personal remotes or local-only machine state.

## Public Release Target

For public release, the preferred target is:

- Hugging Face Dataset for the reviewer-friendly dataset interface and
  programmatic access;
- Zenodo DOI for durable archival versioning.

This dual route is practical because Hugging Face gives easy file browsing and
dataset-card workflow, while Zenodo gives a durable citation and fixed archive.

Acceptable alternatives are Harvard Dataverse, OpenML, Kaggle, or another
durable host that keeps data accessible and provides a stable URL.

## Croissant Metadata

The repository includes a draft Croissant file:

```text
artifact/metadata/croissant.json
```

It uses anonymous placeholder URLs until a hosting platform is selected. After
hosting, update:

- dataset URL;
- file `contentUrl` fields;
- DOI or persistent identifier;
- final license URL if different;
- final checksums after archive construction;
- any platform-generated Croissant core fields.

The mapping note is:

```text
artifact/metadata/CROISSANT_MAPPING.md
```

## Sample Requirement For Large Releases

If the public release archive exceeds a large-data threshold or becomes
impractical to inspect directly, provide a small sample package with:

- a few model-visible tasks;
- matching scorer-only oracle rows;
- a few confirmatory row-manifest entries;
- a few diagnostic row-manifest entries;
- a tiny saved-output replay example;
- the same scorer/verifier entry points.

The sample must preserve the oracle boundary: model-visible task surfaces and
scorer-only fields remain separate.

## Versioning

Use immutable release tags for reviewer and public artifacts.

Recommended naming:

```text
reviewer-packaging-YYYYMMDD
public-release-v1.0.0
```

Each release should include:

- `CHANGELOG.md`;
- `STATUS.md`;
- Croissant metadata;
- benchmark card;
- RAI/ethics/limitations note;
- SHA-256 manifest;
- archive contents listing;
- commands used to verify the release.

## Accessibility Boundary

The release should support three access paths:

- read-only browsing for reviewers;
- local offline verification from a cloned repository or extracted archive;
- programmatic download from a public hosting platform after acceptance.

The release should not depend on contacting the authors for credentials,
permissions, API keys, or unreleased files.

## Git Clone Versus Source Archive

Some checks have different requirements:

- saved-output replay, budget-300 diagnostic summaries, Croissant JSON
  validation, and public-hash checks can run from an extracted source archive;
- strict E5 verification reads Git metadata and repository cleanliness from an
  anonymous Git clone that preserves `.git`;
- the generated review archive from `scripts/build_review_archive.sh` does not
  contain `.git`; in archive mode the E5 verifier checks hash closure and
  reports repository cleanliness as not applicable;
- manually zipping a working tree is discouraged because it can include ignored
  private files or omit Git metadata needed for strict checks.

Use `scripts/build_review_archive.sh` for committee-facing archives.

## Accessibility Notes

The reviewer path is command-line based and uses Markdown, JSON, JSONL, CSV,
and plain-text reports. The artifact should keep text equivalents for tables
and should not rely on image-only evidence. Large JSONL files should be paired
with summary README or summary JSON files. Future figures should not rely on
color alone to encode the main claim.

## Current Status

This repository includes the clean-v2 five-model row-level execution closure.
The submission aggregate result layer is frozen under:

```text
paper/submission_tables/
```

This submission layer is a public-lite paper result freeze. Final public hosting
is still pending: Croissant URLs, DOI, license URL, final archive checksums, and
the durable public release package should be updated when the public release is
created. The Croissant placeholders do not block the submission tables/results
freeze.
