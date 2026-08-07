# Architecture

## Processing flow

```mermaid
flowchart TB
    subgraph Sources
        C[Generated customers]
        T[Generated transactions]
    end

    subgraph Processing
        V[Schema and configuration validation]
        F[Customer feature aggregation]
        R[Fictional rule selection]
        S[Normalized weighted score]
        K[Regional top-K ranking]
    end

    subgraph Reliability
        D[(Idempotent recommendation store)]
        M[Mock delivery client]
        Y[Retry controller]
        X[Receipt reconciliation]
    end

    subgraph Operations
        L[JSON logs]
        Q[Stage counters]
    end

    C --> V
    T --> V
    V --> F --> R --> S --> K --> D --> Y --> M --> X
    F -. metrics .-> Q
    K -. metrics .-> Q
    X -. metrics .-> Q
    X -. events .-> L
```

## Design boundaries

The local pipeline uses immutable dataclasses and small functions, which keeps rule and transformation tests fast. The Spark module implements the same feature contract with DataFrame expressions. This split lets contributors examine distributed processing without making the local demo depend on a running cluster.

Recommendations receive a SHA-256 idempotency key derived from the run date, customer, and recommendation category. The in-memory store and optional Delta adapter insert a key only once. Delivery also caches a receipt per key, so replaying the same run does not issue a second simulated request.

Only a `202` response is considered accepted in this fictional protocol. Other codes and timeouts are retried, then reconciled as exhausted when the configured attempt limit is reached.

## Deployment portability

The repository includes a generic Databricks Asset Bundle example, but local execution does not require it. No cloud host, account, identity, secret scope, storage path, or private artifact registry is configured.
