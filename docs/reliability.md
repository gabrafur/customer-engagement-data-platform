# Reliability design

Reliability is presented as explicit contracts with clear integration boundaries. Some
patterns run in the default local pipeline; others are independently executable building
blocks.

| Concern | Evidence | Default pipeline integration |
|---|---|---|
| Deterministic recommendation identity | [ranking.py](../src/engagement_platform/ranking.py) | Yes |
| Insert-once local storage | [storage.py](../src/engagement_platform/storage.py) | Yes |
| Delta MERGE by idempotency key | [storage.py](../src/engagement_platform/storage.py) | Optional adapter |
| Delivery retry and receipt cache | [delivery.py](../src/engagement_platform/delivery.py) | Yes |
| Transactional outbox and transitions | [outbox.py](../src/engagement_platform/outbox.py) | Separate pattern model |
| Mutation retry classification | [retry.py](../src/engagement_platform/retry.py) | Separate helper |
| Literal partition scoping | [partitioning.py](../src/engagement_platform/partitioning.py) | Separate helper |
| As-of rebuild without delivery | [replay.py](../src/engagement_platform/replay.py) | Dedicated CLI path |

## Idempotency

Recommendation keys are SHA-256 hashes of processing date, customer identifier, and
recommendation category. Repeating an identical batch produces the same keys. The in-memory
store and optional Delta adapter insert a key only when it is absent.

ReliableDeliveryService caches a final receipt per key. Repeating a delivery through the
same service instance returns the prior receipt without calling the client again.

## Transient and permanent failures

Two retry mechanisms have different scopes:

- Delivery catches TimeoutError and OSError, and also retries non-202 responses until the
  configured attempt budget is exhausted. The terminal state is RETRY_EXHAUSTED.
- Delta mutation retry handles only ConcurrentMutationError and MetadataRefreshError.
  Exceptions outside that allowlist are raised immediately.

Both policies use bounded exponential delay. Neither retries indefinitely or hides a
permanent error.

## Transactional outbox

The outbox model is append-only. Multiple events may exist for one idempotency key, pending
dispatch selects the newest event, and state changes append to a separate transition log.
Current state is derived from history rather than overwritten in place.

This model is tested in [test_outbox_replay.py](../tests/integration/test_outbox_replay.py),
but EngagementPipeline currently persists recommendations and calls the delivery service
directly. The repository therefore claims an executable outbox pattern, not end-to-end
outbox integration.

## Concurrent Delta mutations

Optimistic storage systems may reject a mutation when another writer commits first.
RetryPolicy limits attempts and delay for explicit transient exceptions.

Retries do not compensate for a broad read set. build_partition_scope produces validated,
escaped, static literal predicates so a caller can declare a narrow target slice. The Delta
adapter, retry helper, and predicate builder remain separate composable functions.

## Historical rebuilding

The rebuild command applies an explicit as-of date to time-sensitive reads. Transactions
after the boundary are excluded. The snapshot is written idempotently and reports zero
external deliveries because no delivery client is constructed.

The result is deterministic for the same synthetic inputs, seed, configuration, and date.
See [ADR 0002](decisions/0002-replay-without-side-effects.md).

## Quality gates and deterministic ordering

Input checks cover identifier uniqueness, engagement ranges, referential integrity,
non-negative amounts, and the processing boundary. Output checks cover idempotency-key
uniqueness, normalized scores, and regional limits. Required gates raise before storage or
delivery.

Ranking orders by descending score and then customer ID, making ties deterministic. Regional
top-K limits and customer/category deduplication bound the output.

## Observable failure states

The repository exposes failed quality gates as DataQualityError, delivery exhaustion as a
receipt state, reconciliation counts for accepted/exhausted delivery, and DAG task states for
success, failure, or skip. Logs and metrics are local process output; no hosted monitoring
system is claimed.
