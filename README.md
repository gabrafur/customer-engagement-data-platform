# Customer Engagement Data Platform

[![CI](https://github.com/gabrafur/customer-engagement-data-platform/actions/workflows/test.yml/badge.svg)](https://github.com/gabrafur/customer-engagement-data-platform/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5-E25A1C?logo=apachespark&logoColor=white)](src/engagement_platform/spark_features.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-inspired data engineering platform that demonstrates reliable distributed-data
patterns with PySpark, Delta Lake, and Databricks-compatible deployment. It remains
reproducible on a laptop with deterministic synthetic data and public dependencies.

## Why this project exists

This is an independent portfolio project for making engineering decisions reviewable in
public. It uses synthetic inputs, fictional rules, local execution, and mock delivery so the
repository can demonstrate production-oriented practices without private infrastructure,
production data, or employer-specific logic.

## What this project demonstrates

- [Distributed feature engineering](src/engagement_platform/spark_features.py) with the
  PySpark DataFrame API and Spark SQL expressions, verified by a
  [local Spark integration test](tests/integration/test_spark_features.py).
- [Required data-quality gates](src/engagement_platform/quality.py) before persistence and
  delivery, covering identifiers, references, ranges, time boundaries, and regional limits.
- [Deterministic scoring and ranking](src/engagement_platform/ranking.py) with normalized
  weights, stable tie-breaking, top-K limits, deduplication, and SHA-256 idempotency keys.
- [Idempotent storage contracts](src/engagement_platform/storage.py): a local store for the
  runnable demo and an optional Delta Lake MERGE adapter for insert-once semantics.
- Independently testable [Delta mutation retry](src/engagement_platform/retry.py) and
  [literal partition scoping](src/engagement_platform/partitioning.py) helpers, kept
  composable rather than presented as an integrated writer.
- [Reliable delivery](src/engagement_platform/delivery.py), [reconciliation](src/engagement_platform/reconciliation.py),
  and a separately modeled [transactional outbox](src/engagement_platform/outbox.py) with an
  append-only transition history.
- [Deterministic historical replay](src/engagement_platform/replay.py) with explicit as-of
  boundaries, idempotent local persistence, and no delivery client construction.
- [DAG execution](src/engagement_platform/dag.py), [provenance](src/engagement_platform/provenance.py),
  structured observability, automated CI, packaging, and a
  [Databricks Asset Bundle example](databricks.yml).

## Architecture

![Customer Engagement Data Platform architecture](docs/assets/customer-engagement-architecture.svg)

Solid arrows show the runnable local pipeline. Dashed arrows identify optional distributed
adapters or independently executable reliability/platform patterns; they are intentionally
not portrayed as integrations the repository does not implement.

See the versioned [Mermaid source](docs/architecture.mmd) and
[architecture notes](docs/architecture.md) for boundaries and trade-offs.

## Engineering highlights

| Capability | Executable evidence | Why it matters |
|---|---|---|
| PySpark feature engineering | [spark_features.py](src/engagement_platform/spark_features.py), [Spark integration test](tests/integration/test_spark_features.py) | Exercises filtering, aggregation, left joins, null defaults, and date boundaries under a real local Spark session. |
| Data quality | [quality.py](src/engagement_platform/quality.py), [quality tests](tests/unit/test_quality.py), [SQL checks](sql/data_quality_checks.sql) | Required gates stop invalid inputs or outputs before delivery; SQL examples make lakehouse expectations inspectable. |
| Deterministic ranking | [scoring.py](src/engagement_platform/scoring.py), [ranking.py](src/engagement_platform/ranking.py), [tests](tests/unit/test_scoring_and_ranking.py) | Stable ordering and bounded regional output make reruns explainable and comparable. |
| Idempotent Delta semantics | [storage.py](src/engagement_platform/storage.py) | Delta MERGE inserts only unseen idempotency keys; the local store implements the same insert-once intent. |
| Delta reliability building blocks | [retry.py](src/engagement_platform/retry.py), [partitioning.py](src/engagement_platform/partitioning.py), [tests](tests/unit/test_retry_partitioning_workflow.py) | Separates retryable concurrency failures from permanent errors and narrows target predicates safely. |
| Reliable delivery | [delivery.py](src/engagement_platform/delivery.py), [reconciliation.py](src/engagement_platform/reconciliation.py), [tests](tests/unit/test_delivery.py) | Bounded exponential retry, cached receipts, explicit exhausted states, and reconciliation cover non-happy paths. |
| Transactional outbox model | [outbox.py](src/engagement_platform/outbox.py), [integration test](tests/integration/test_outbox_replay.py) | Append-only events and immutable transitions preserve audit history; this pattern is modeled separately from the default pipeline. |
| Historical replay | [replay.py](src/engagement_platform/replay.py), [ADR 0002](docs/decisions/0002-replay-without-side-effects.md) | Explicit as-of processing rebuilds a deterministic snapshot without invoking downstream delivery. |
| DAG and provenance utilities | [dag.py](src/engagement_platform/dag.py), [provenance.py](src/engagement_platform/provenance.py), [platform design](docs/modular-platform.md) | Topological execution, readiness gates, terminal states, deterministic run identity, and batch fingerprints make failure and lineage explicit. |
| CI, packaging, and deployment example | [test.yml](.github/workflows/test.yml), [pyproject.toml](pyproject.toml), [databricks.yml](databricks.yml), [demo_job.yml](resources/demo_job.yml) | CI verifies lint, strict types, 52 tests, 96%+ measured coverage, wheel build, content safety, and a reviewable Databricks-compatible job definition. |

## Five-minute technical tour

1. **Architecture:** inspect the [system boundaries](docs/architecture.md) and
   [Mermaid source](docs/architecture.mmd); solid and dashed paths prevent optional patterns
   from being mistaken for the default runtime.
2. **Pipeline orchestration:** follow EngagementPipeline.run in
   [orchestration.py](src/engagement_platform/orchestration.py), then review the independent
   DagRunner utility in [dag.py](src/engagement_platform/dag.py).
3. **PySpark implementation:** compare the distributed
   [DataFrame transformation](src/engagement_platform/spark_features.py) with the
   [local feature contract](src/engagement_platform/features.py) and its
   [Spark test](tests/integration/test_spark_features.py).
4. **Data quality:** review [input/output gates](src/engagement_platform/quality.py), their
   [failure-path tests](tests/unit/test_quality.py), and the
   [SQL expectations](sql/data_quality_checks.sql).
5. **Delta and idempotency:** inspect [MERGE semantics](src/engagement_platform/storage.py),
   [retry classification](src/engagement_platform/retry.py), and
   [partition predicates](src/engagement_platform/partitioning.py). The latter two are
   tested building blocks, not wired around the adapter.
6. **Reliability and outbox:** trace direct
   [delivery retry/idempotency](src/engagement_platform/delivery.py),
   [reconciliation](src/engagement_platform/reconciliation.py), and the separate
   [outbox state model](src/engagement_platform/outbox.py).
7. **Historical replay:** read [replay.py](src/engagement_platform/replay.py) and
   [ADR 0002](docs/decisions/0002-replay-without-side-effects.md) for bounded reads and the
   no-side-effect invariant.
8. **Observability:** inspect [JSON logging and counters](src/engagement_platform/monitoring.py)
   plus deterministic [run provenance](src/engagement_platform/provenance.py).
9. **Tests and CI:** start at [testing strategy](docs/testing-strategy.md),
   [tests](tests/), and the complete [GitHub Actions workflow](.github/workflows/test.yml).
10. **Databricks deployment:** review the [bundle](databricks.yml),
    [job resource](resources/demo_job.yml), and [wheel packaging](pyproject.toml), then read
    the deployment limits in [architecture.md](docs/architecture.md).

## Execution boundaries

| Area | What runs locally | What is demonstrated separately |
|---|---|---|
| Processing | Deterministic Python feature, scoring, ranking, quality, storage, delivery, and reconciliation pipeline | PySpark DataFrame implementation of the feature schema |
| Storage | In-memory insert-once store | Delta Lake MERGE adapter, retry policy, and partition-scope builder |
| Reliability | Direct mock delivery with retries and cached receipts; side-effect-free replay | Transactional outbox and immutable transition-log model |
| Orchestration | Explicit sequential stage boundaries in EngagementPipeline | Generic DagRunner with dependencies, readiness gates, failure, and skip states |
| Deployment | Python wheel and CLI | Databricks-compatible Asset Bundle example; no workspace or deployment is claimed |

## Technology stack

- Python 3.11–3.12
- PySpark 3.5 DataFrame API and Spark SQL expressions
- Delta Lake
- YAML and TOML
- pytest, Ruff, mypy, and coverage.py
- GitHub Actions
- Databricks Asset Bundles (deployment example)

## Run locally

Python 3.11 or 3.12 is required. Java 17 is needed for the Spark integration test.

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev,spark]'

engagement-platform generate --customers 100 --output data/generated
engagement-platform run --config configs/development.yml --customers 100
engagement-platform rebuild +  --config configs/development.yml +  --customers 100 +  --as-of-date 2026-06-01
~~~

Every default configuration uses MockDeliveryClient. HttpDeliveryClient requires an endpoint
provided explicitly by a caller and is never constructed by the demo pipeline.

## Verify the repository

~~~bash
ruff check .
mypy src
pytest
python -m build --wheel
python scripts/security_scan.py .
~~~

Verified on Linux with Python 3.12 and Java 17: **52 tests passed**, including the local
Spark integration test, with **96.9% measured coverage** (96.85% before rounding). The CI workflow
runs the same lint, type, test, build, change-impact, and content-scan checks.

## Example output

The CLI emits runtime-derived counters rather than committed performance claims:

~~~json
{"customers_input": 100, "features_created": 100, "recommendations_created": 25}
~~~

Exact recommendation counts depend on configured regional limits. The benchmark command
reports measurements for the current local run; the repository makes no production-scale or
durable performance claim.

## Repository map

~~~text
configs/            Synthetic pipeline, workflow, and module-registry settings
data/sample/        Small hand-authored synthetic CSV examples
docs/               Architecture, reliability, operations, ADRs, and portfolio copy
notebooks/          Output-free local demonstration notebook
resources/          Databricks-compatible job example
scripts/            Local content and secret safety scan
sql/                Generic Delta DDL and data-quality queries
src/                Pipeline and independently testable platform patterns
tests/              Unit, integration, CLI, and local Spark tests
~~~

## Security and clean-room policy

- Data is hand-authored or generated locally from a deterministic pseudo-random seed.
- No environment file, credential, private host, workspace identifier, cloud storage path,
  or private package source is required.
- Generated data, build output, and local environments are ignored by Git.
- The content scanner rejects secret-shaped values, private service URLs, notebook outputs,
  and unexpected file types in the working tree.

## Disclaimer

This is an independent portfolio project built with synthetic data and generic business
rules. It does not contain proprietary source code, confidential information, production
data, internal configurations, or business logic from any current or former employer.
