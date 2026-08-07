# Operations guide

## Local health check

```bash
ruff check .
mypy src
pytest
python scripts/security_scan.py .
engagement-platform run --config configs/development.yml --customers 100
```

The run emits one JSON log event and a JSON metrics summary. Expected invariants are:

- input and feature counts match;
- created recommendations do not exceed the sum of enabled regional limits;
- accepted plus exhausted deliveries equals created recommendations;
- all required quality checks pass;
- a repeated run inserts no additional recommendation keys.

## Failure triage

1. Confirm configuration validation and required quality checks.
2. Compare input, feature, recommendation, insertion, and delivery counters.
3. For a concurrent mutation, verify that the operation is classified as transient and that the target predicate contains literal partition values.
4. For a delivery retry, inspect the final receipt, attempt count, and idempotency key without logging payload data.
5. For a historical rebuild, confirm the as-of date and verify that external delivery count remains zero.

## Safe replay

```bash
engagement-platform rebuild \
  --config configs/development.yml \
  --customers 100 \
  --as-of-date 2026-06-01
```

This command generates new synthetic input, applies the historical boundary, and creates a local snapshot. It does not contact a remote system.
