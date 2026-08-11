# Modular platform design

The platform utilities demonstrate repository-scale concerns independently from the
recommendation pipeline. They are executable and tested, but they are not presented as a
cloud control plane or as hidden stages in EngagementPipeline.

## Orchestration

~~~mermaid
flowchart LR
    A[Task specifications] --> V{DAG validation}
    G[Readiness gates] --> R[Topological runner]
    V --> R
    R --> S[Success]
    R --> F[Failure]
    R --> K[Skipped]
    S --> P[Execution records]
    F --> P
    K --> P
~~~

DagRunner rejects duplicate names, unknown dependencies, and cycles before execution. Tasks
can require every dependency to succeed or continue when at least one alternative succeeds.
Failed gates and unsatisfied dependencies create explicit skipped executions rather than
ambiguous missing output.

EngagementPipeline remains a direct sequential orchestrator. DagRunner proves generic DAG
semantics without claiming that it schedules the domain pipeline or replaces a cloud
orchestrator.

## Provenance

RunContext derives a deterministic run identifier from pipeline name, source version, as-of
date, and canonical parameters. Stamping returns a copied record with run metadata and never
mutates the source. batch_fingerprint produces an order-independent SHA-256 digest for
synthetic batch comparison.

These utilities are available to callers; the default pipeline does not automatically stamp
every recommendation.

## Change-impact resolution

~~~mermaid
flowchart LR
    C[Changed paths] --> M[TOML module registry]
    M --> I[Impacted modules]
    I --> Q[Required checks]
    I --> A[Versioned artifact tags]
    Q --> X[Candidate CI matrix]
~~~

The registry describes three generic modules for this repository. A path may affect multiple
modules, so the resolver preserves overlapping ownership and deduplicates checks. Unmatched
paths remain visible.

The GitHub Actions workflow exercises the resolver with deterministic inputs, then runs the
full quality job. It does not currently consume the returned matrix to create dynamic jobs.

Example:

~~~bash
engagement-platform impact +  --registry configs/modules.toml +  --changed src/engagement_platform/spark_features.py docs/architecture.md
~~~

## Benchmark harness

The benchmark command uses generated data and reports input/output counts, elapsed time, and
records per second for the current local process. Results are emitted at runtime rather than
committed as durable performance or production-scale claims.
