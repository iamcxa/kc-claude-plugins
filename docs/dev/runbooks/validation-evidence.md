# Validation Evidence Runbook

Load this runbook only when entering or re-entering `validation`. The workflow
README owns the gate predicate; this file gives the stage-specific procedure.

## Bind the review

Record the exact head revision, merge-target revision, task/AC revision, paths
read, and selected policy mods. A stale buffer, base commit, `origin/main`, and
the worktree are different artifacts.

For every review round, name:

- what exact artifact and path it read;
- which AC, claim, or lens it tested;
- the concrete change to that claim that would have produced a finding.

## Evidence block

Write all six lines. Empty means not done. `Lenses:` and `Cross-model:` are never
`N/A`; every permitted `N/A` includes its local reason.

```text
Lenses: <classification; fired lenses, verdicts, finding counts, inputs, falsifiers>
Diff coverage: <measured percent and denominator> | N/A — prose-only diff, no executable surface
Adversarial: <attempt and result> | N/A — no behavioral guard to break
Cross-model: recommended|not_needed — <EM decision; optional pass result if captain approved it>
E2E: <scenario and result> | N/A — <ideation-approved docs/config/CI-only reason>
Origin re-observation: <form below>
```

When an accepted problem or AC came from a consumer or external runtime, use:

```text
Origin re-observation: PASS|FAIL — Reported scenario: <scenario> | Originating runtime kind: <kind> | Re-observation artifact/revision: <artifact and exact revision> | Equivalent-runtime rationale: <matching actor, instrument, delivery path, configuration, and claim-relevant conditions> | Falsifier kind: refusal|mutation|existence-disproof | Result: <observed result>
```

Otherwise write:

```text
Origin re-observation: N/A — no accepted claim originated in consumer or external runtime behavior
```

An unavailable runtime or instrument is missing evidence, not `N/A`.

## Review lenses

Classify the diff, then run every fired lens:

- behavior: acceptance path, errors, validation, fallback, swallowed failures;
- contract/schema: producer and consumer compatibility, migrations, defaults;
- state/concurrency: ownership, interruption, retry, duplicate delivery;
- security/privacy: trust boundaries, credentials, disclosure, destructive scope;
- runtime/platform: OS, locale, clock, pinned tools, timeout margin;
- docs/policy: internal consistency, executable references, authority boundaries;
- delivery: exact-head checks, version propagation, install and release surfaces.

Diff coverage counts coverable changed behavior lines exercised by a failing
test, runtime scenario, or direct falsifier. Prose-only diffs may be `N/A` but
still require adversarial document review.

## Correction rounds

Reject with evidence tied to an AC or fired lens, route to implementation, and
re-enter with fresh context. Rework re-anchors on the source requirement; it
does not optimize for reviewer wording.

At two consecutive rejected cycles on the same gate, the EM selects one
recommendation for the captain when needed: another bounded correction,
ideation reset because the shape is wrong, narrower captain-approved scope, or
stop. Record each round's effort against the ideation appetite/tolerance; never
extend scope or compress verification silently.

Before accepting, map every changed file to an AC. Delete unmapped scope or ask
the captain to authorize it. Preserve accepted measurement and coverage in the
entity, but do not make token availability a delivery predicate.
