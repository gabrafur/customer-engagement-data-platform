# ADR 0002: Keep historical rebuilding side-effect free

## Status

Accepted

## Context

Historical recomputation is useful for debugging and reproducibility, but repeating an old batch must not accidentally invoke a current downstream integration.

## Decision

Historical rebuilding accepts an explicit as-of date, caps input reads at that boundary, recomputes the recommendation snapshot, and writes idempotently. It does not construct or call a delivery client.

## Consequences

- Historical results are deterministic for the same seed, configuration, and date.
- Delivery behavior remains testable through the separate simulator.
- The CLI can report external deliveries as zero by construction.
