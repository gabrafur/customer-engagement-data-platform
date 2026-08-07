# Testing strategy

The test pyramid separates fast deterministic behavior from the distributed contract.

| Layer | Coverage |
|---|---|
| Unit | Configuration, quality checks, rules, scoring, ranking, retry, partition predicates, outbox state, and workflow merging |
| Integration | Full pipeline replay, CLI generation, historical rebuild, idempotent rerun, and delivery reconciliation |
| Spark | DataFrame aggregation contract under a real local Spark session |
| Static | Ruff and strict mypy |
| Security | Secret-shaped values, private service URLs, notebook outputs, binary files, and repository history |

Synthetic fixtures use fixed seeds and dates. Tests never require a cloud account, remote dataset, private package source, or environment secret.
