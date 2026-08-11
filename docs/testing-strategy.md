# Testing strategy

The test pyramid separates fast deterministic domain behavior from integration and
distributed contracts.

| Layer | Scope | Evidence |
|---|---|---|
| Unit | Configuration, quality, rules, scoring, ranking, retry, partition predicates, outbox state, DAG behavior, provenance, and workflow merging | [tests/unit](../tests/unit/) |
| Integration | End-to-end local pipeline, idempotent rerun, CLI commands, historical rebuild, outbox history, and reconciliation | [tests/integration](../tests/integration/) |
| Spark | PySpark DataFrame API and Spark SQL expressions for filtering, aggregation, left join, null handling, and date boundaries | [test_spark_features.py](../tests/integration/test_spark_features.py) |
| Static | Ruff rules and strict mypy over the source package | [pyproject.toml](../pyproject.toml) |
| Packaging | Isolated wheel build through hatchling | [pyproject.toml](../pyproject.toml) |
| Content safety | Secret-shaped values, private service URLs, notebook outputs, and unexpected working-tree file types | [security_scan.py](../scripts/security_scan.py) |

## Verified baseline

Validated on Linux, Python 3.12.3, and Java 17:

~~~text
52 passed
TOTAL 826 statements, 26 missed, 96.85% measured coverage (96.9% to one decimal)
Ruff: all checks passed
mypy: no issues in 25 source files
wheel: customer_engagement_data_platform-0.2.0-py3-none-any.whl
security scan: passed
~~~

pytest is configured with an 85% minimum, while the current measured result is higher. The
README reports 96.9% measured coverage, not a guarantee that every future revision must
remain at that exact percentage.

## CI contract

[test.yml](../.github/workflows/test.yml) provisions Python 3.11 and Java 17, installs the dev
and spark extras from public indexes, and runs:

1. Ruff;
2. strict mypy;
3. a deterministic change-impact resolver example;
4. all pytest tests, including the Spark marker;
5. an isolated wheel build;
6. the security/content scanner.

The change-impact utility can produce a selective matrix, but the current workflow validates
the resolver and then runs one complete job; it does not dynamically fan out that matrix.

## Determinism and isolation

Synthetic fixtures use fixed seeds and dates. Tests require no cloud account, remote
dataset, private package source, environment secret, or live endpoint. The Spark test uses a
single local worker.

The content scanner examines the working tree recursively and ignores known local build and
cache directories. It does not scan Git history; provenance of the clean-room implementation
is documented separately in [ADR 0001](decisions/0001-clean-room-implementation.md).
