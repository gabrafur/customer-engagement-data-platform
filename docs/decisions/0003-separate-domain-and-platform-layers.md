# ADR 0003: Separate domain and platform layers

## Status

Accepted

## Context

Recommendation logic and repository-scale delivery concerns change for different reasons. Combining them makes tests slower and hides which capability a change exercises.

## Decision

Keep scoring, ranking, storage, and delivery in the domain pipeline. Model orchestration, provenance, change-impact resolution, modular versions, and benchmarking as independent platform utilities with their own tests and configuration.

## Consequences

- Domain tests remain deterministic and fast.
- Platform components can be demonstrated without a cloud control plane.
- Changed paths can map to more than one module and check set.
- Versioned artifacts remain explicit without coupling version numbers to branch names.
