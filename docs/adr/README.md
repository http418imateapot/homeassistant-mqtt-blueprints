# Architecture Decision Records (ADR)

This directory tracks architecture and design decisions for this repository.

## Purpose

Use ADRs to document:

- Context and problem statement
- Decision taken
- Consequences and trade-offs
- Migration and validation notes

## File Naming Convention

Use the following filename format:

- `ADR-XXXX-short-title.md`

Where:

- `XXXX` is a zero-padded incremental number (for example `0001`, `0002`)
- `short-title` is a concise kebab-case summary

## Status Values

Recommended `Status` values inside each ADR:

- `Proposed`
- `Accepted`
- `Superseded`
- `Rejected`
- `Deprecated`

Optional `Outcome` can be used for implementation tracking:

- `Solved`
- `In Progress`
- `Partially Solved`

## ADR Index

| ADR | Title | Status | Outcome | Date | Related |
| --- | --- | --- | --- | --- | --- |
| [ADR-0003](ADR-0003-domain-based-telemetry.md) | Replace Category-Based Telemetry Grouping with Domain-Based Telemetries Array | Accepted | Solved | 2026-06-20 | #3 |

## How to Add a New ADR

1. Copy an existing ADR as a starting template.
2. Create a new file with the next incremental ADR number.
3. Fill in: Context, Decision, Consequences, Migration Notes, Validation, and Alternatives.
4. Add a new row to the ADR Index table in this file.
5. If this ADR supersedes another one, update both files accordingly.
