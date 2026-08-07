# ADR 0001: Use a clean-room implementation

## Status

Accepted

## Context

A portfolio project should demonstrate engineering judgment without exposing another organization's code, data, topology, configuration, or business behavior.

## Decision

Every file in this repository is independently authored around a fictional customer engagement domain. The project uses synthetic inputs, new rules, a compact architecture, public dependencies, local observability, and a mock integration. No source tree or version history from an employer is imported.

## Consequences

- The project demonstrates transferable engineering patterns instead of claiming feature parity with another system.
- Examples remain reproducible without a corporate network or cloud account.
- Rules, thresholds, schemas, and workflow boundaries are intentionally simple and generic.
- Future contributions must preserve the synthetic-only data policy.
