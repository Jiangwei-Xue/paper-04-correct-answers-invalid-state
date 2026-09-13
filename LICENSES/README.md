# Layered licensing

No single license applies to this repository as a whole. License scope is
determined by both path and material type; a file-specific or upstream notice
takes precedence.

| Repository material | Governing license or terms |
|---|---|
| Project-authored code under `metric_v2/`, `metric_v3/`, `scripts/`, and `tools/` | MIT License; see `MIT.txt` |
| Project-authored Python code under `artifact/`, plus `Makefile` and other project-authored executable configuration | MIT License; see `MIT.txt` |
| `README.md`, project-authored documentation under `docs/`, `RELEASE_AUDIT.md`, and `CITATION.cff` | CC BY 4.0; see `CC-BY-4.0.txt` |
| Project-authored documentation under `artifact/` | CC BY 4.0; see `CC-BY-4.0.txt` |
| Author-generated aggregate tables under `paper/submission_tables/tables/` and aggregate tables and reports under `reports/` | CC BY 4.0; see `CC-BY-4.0.txt` |
| Model requests, model responses, provider metadata, and provider-generated records under `artifact/results/` | Original provider and model terms; no new license is granted |
| Benchmark-derived records, public data, and material derived from public data | Original source, dataset, or benchmark terms; no new license is granted unless a file-specific notice says otherwise |
| Third-party code, libraries, repository content, trademarks, and independently licensed components | Their original licenses or terms; see `THIRD_PARTY.md` |

The MIT grant for project-authored Python code under `artifact/` does not cover
saved records, model outputs, provider metadata, benchmark-derived content, or
third-party material that happens to appear below that directory. Likewise, the
CC BY 4.0 grant for project-authored documentation does not apply automatically
to every Markdown file or to embedded third-party material.

## Manuscript boundary

The manuscript is not bundled in this GitHub repository. The separately
published preprint, DOI `10.5281/zenodo.22720976`, is licensed under CC BY 4.0
according to the license attached to its Zenodo record. That license does not
extend to this repository as a whole, to provider records, or to model outputs.

See `THIRD_PARTY.md` for the repository-specific inventory and reuse boundaries.
