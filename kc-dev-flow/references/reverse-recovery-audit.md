---
name: reverse-recovery-audit
description: "Triggered brownfield audit that distinguishes recovery, missing capability, and removal candidates before new implementation is accepted"
version: 0.4.0
---

# Reverse-Recovery Audit

Use this reference only when the selected profile stage emits its typed trigger,
or when a source-maintenance skill explicitly invokes the audit. Its purpose is
to stop a proposed addition, replacement, or removal from bypassing existing
working or repairable code.

## Trigger

`brownfield_capability_change` is true when work in an existing codebase
proposes to create, replace, or remove a capability or abstraction, or claims
that one is missing.

Do not load it for a greenfield experiment, a direct repair of an already named
broken seam, or a mechanical docs, configuration, rename, formatting, or pinned
dependency change. Implementation does not repeat a completed shape audit. If
implementation discovers an unplanned surface, return that changed premise to
the profile stage that owns scope.

## Two-axis classification

Completeness and need answer different questions. Record both for every layer
that the proposed change would create, replace, remove, or directly build on.

| Completeness | Meaning | Minimum evidence |
|---|---|---|
| `WORKING` | Works through the relevant journey | Runtime or end-to-end observation |
| `WORKING_UNIT_UNPROVEN` | Owned logic passes but wiring is unproved | Focused unit result and missing seam proof |
| `EXISTS_BROKEN` | Present but fails at a named seam | Concrete failure or contract mismatch |
| `STUB` | Shape exists without the required behavior | Located placeholder, skeleton, or fake |
| `MISSING` | No relevant abstraction was found | Two search strategies with boundaries named |

| Need | Meaning | Minimum evidence |
|---|---|---|
| `REQUIRED` | A named consumer or contract needs it, or it maps to `kernel.md`'s minimal-necessity reasons — the accepted goal, a named falsifier, a safety boundary, or a required lifecycle obligation | Named consumer or contract, or one of the four named reasons |
| `NO_OBSERVED_CONSUMER` | None of the REQUIRED reasons was found inside declared boundaries | Two searches plus the boundary where they stopped |
| `UNKNOWN` | Need was not established | Missing search or an open boundary named |

`NO_OBSERVED_CONSUMER` is a removal candidate, never removal authority.

Worked case: a safety-boundary surface with no observed consumer classifies
`REQUIRED`, the same tier `kernel.md`'s execution-tier mapping reaches, because a
safety boundary is one of the four named reasons and does not depend on finding a
consumer.

This audit's `disproof_hook` runs at the search tier: it can conclude only that
two searches inside the named boundary found no consumer, never that none
exists. `kernel.md`'s without-it observation runs the same primitive at the
execution tier and can conclude a surface is unnecessary.

## Procedure

1. Name the affected journey and the smallest relevant search boundary.
2. Trace only its applicable layers: entry, contract, handler, domain behavior,
   persistence or projection, and readback. Record a location or `MISSING`.
3. Before writing `MISSING` or `NO_OBSERVED_CONSUMER`, use two search strategies
   and state what was searched, excluded, or remains unknown. Include external,
   dynamic, manual, compatibility, and dormant consumers when they can apply.
4. Classify the relevant layers on both axes. Unit tests can prove logic, not
   wiring. Every non-runtime claim gets one command or observation that could
   disprove it.
5. Choose the smallest supported route: recover the seam, use the working
   mechanism, build what is proven missing, present a removal candidate to the
   scope owner, or escalate an incompatible recovered design.

## Receipt

Record one bounded receipt in the work item; do not create a parallel ledger.

```yaml
reverse_recovery:
  trigger: <proposed addition, replacement, removal, or missing claim>
  boundary: <journey and search boundary>
  layers:
    - surface: <name>
      location: <file:line | MISSING>
      completeness: <tier>
      need: <value>
      evidence: <short evidence>
      disproof_hook: <command or observation>
  decision: <recover | use | build | removal_candidate | redesign>
```

The audit proposes. Captain or the declared scope owner decides removal,
redesign, profile change, or added scope.
