# All-Model Direct Clean-V2 From-Zero Runs

Created: 2026-06-28 UTC

This namespace stores v2 direct-network from-zero confirmatory slices for the
five-model primary matrix. It supersedes pooling v1 proxy-mediated model slices
with later clean-v2 rows.

Current contents:

| model condition | role | status | rows | backend rows | parse+score success | replay closure |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `deepseek_v4pro` | `confirmatory_primary` | `COMPLETE` | 1,440 | 6 | 1,434 | VCR audit passed, cache miss 0 |
| `qwen37max` | `confirmatory_primary` | `COMPLETE` | 1,440 | 0 | 1,440 | VCR audit passed, cache miss 0 |
| `kimi_k26` | `confirmatory_primary` | `COMPLETE` | 1,440 | 7 | 1,438 | VCR audit passed, cache miss 0 |

The DeepSeek execution also produced a 23-row launch/monitoring fragment before
the complete from-zero slice was run. That superseded fragment is not included
in this reviewer-facing namespace. It did not produce a complete 1,440-row
summary and is not primary matrix evidence.

## Boundary

Rows in this namespace are v2 direct-network from-zero rows. Earlier v1
record-mode outputs under sibling model directories remain append-only audit
evidence and must not be pooled with this namespace for final primary
aggregation.

The governing protocol is:

```text
../../../protocol/main_matrix/V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```
