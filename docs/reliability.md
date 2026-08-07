# Reliability design

## Idempotency

Recommendation keys are SHA-256 hashes of the processing date, customer identifier, and fictional recommendation category. Repeating an identical batch produces the same keys. Both local storage and the Delta adapter insert a key only when it is absent.

The delivery service caches final receipts by key. A replay therefore returns the existing receipt rather than repeating an external side effect.

## Transactional outbox

The outbox is append-only. Multiple events may exist for one idempotency key, and dispatch selects the newest pending event. State changes are appended to a separate transition log instead of overwriting history. This supports auditability while still exposing a derived current state.

## Concurrent writes

Optimistic storage systems may reject a mutation when another writer commits first. `RetryPolicy` bounds attempts and exponential delay for explicitly retryable exceptions. Permanent errors are surfaced immediately.

Retries cannot compensate for an unnecessarily broad read set. `build_partition_scope` creates static literal predicates so a merge declares the smallest relevant target slice. Identifiers are validated and string literals are escaped.

## Historical rebuilding

The `rebuild` command applies an explicit as-of date to every time-sensitive read. Transactions after that boundary are excluded. The resulting snapshot is persisted idempotently and reports zero external deliveries by design.

## Quality gates

Input checks cover identifier uniqueness, score ranges, referential integrity, non-negative amounts, and the as-of boundary. Output checks cover idempotency-key uniqueness, score normalization, and regional limits. Required gates fail the pipeline before delivery.
