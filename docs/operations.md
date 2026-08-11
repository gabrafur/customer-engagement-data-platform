# Operations guide

## Local health check

Use Python 3.11 or 3.12 and Java 17. From an activated environment with
the dev and spark extras installed:

~~~bash
ruff check .
mypy src
pytest
python -m build --wheel
python scripts/security_scan.py .
engagement-platform impact +  --registry configs/modules.toml +  --changed src/engagement_platform/dag.py docs/architecture.md
engagement-platform run --config configs/development.yml --customers 100
~~~

The complete suite executes 52 tests, including a local Spark integration test. The verified
Linux baseline is 96.9% measured coverage (96.85% before rounding).

## Runtime invariants

- input customer count equals produced feature count;
- recommendation count does not exceed enabled regional limits;
- every required input and output quality check passes;
- accepted plus retry-exhausted receipts equals created recommendations;
- repeating a batch against the same store inserts no additional idempotency keys;
- repeating delivery through the same service instance does not call the client twice;
- historical rebuild reports zero external deliveries.

## Failure triage

1. **Configuration or quality failure:** inspect the rejected field/check before considering
   a replay. Quality gates run before storage and delivery.
2. **Delivery exhaustion:** inspect final receipt state, status code, attempts, and
   idempotency key. The demo does not log recommendation payloads.
3. **Concurrent Delta mutation:** verify the error is explicitly retryable, the attempt
   budget is bounded, and the caller supplied a literal target predicate. These helpers are
   not automatically wrapped around the optional adapter.
4. **Unexpected rerun inserts:** compare as-of date, configuration, customer, and
   recommendation category because they contribute to deterministic identity.
5. **Historical mismatch:** confirm the seed and as-of boundary, then compare batch
   fingerprints. External delivery should remain absent.
6. **DAG failure or skip:** inspect TaskExecution.state, error_type, dependency mode, and
   readiness-gate details. DagRunner is an independent utility, not the CLI executor.

## Safe replay

~~~bash
engagement-platform rebuild +  --config configs/development.yml +  --customers 100 +  --as-of-date 2026-06-01
~~~

This command generates deterministic synthetic input, applies the historical boundary, and
creates a local snapshot. It does not instantiate HttpDeliveryClient or contact a remote
system.

## Observability scope

The local run emits one structured JSON completion event and a sorted integer metrics
snapshot. Provenance helpers provide deterministic run identity and batch fingerprints, but
EngagementPipeline does not stamp every output automatically. There is no metrics backend,
dashboard, alert manager, or distributed tracing claim.

## Databricks review boundary

The bundle and job resource can be inspected as a Databricks-compatible packaging example.
No workspace target, credentials, remote validation result, or deployed job is stored in the
repository. Review [databricks.yml](../databricks.yml),
[demo_job.yml](../resources/demo_job.yml), and [pyproject.toml](../pyproject.toml) together.
