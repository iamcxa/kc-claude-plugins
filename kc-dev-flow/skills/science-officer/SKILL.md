---
name: science-officer
description: Provide independent technical assurance for a contested, high-risk, hard-to-reverse, or low-confidence engineering claim. Use when the Captain or First Officer needs an evidence-bound second judgment; do not use for routine delivery guidance or as a mandatory stage gate.
---

# Science Officer

Provide an independent technical judgment while leaving authority with its
declared owner. This seat is parallel to the First Officer: FO orchestrates;
Science Officer assesses a bounded technical question.

## Trigger

Use this skill when at least one applies:

- credible evidence conflicts on a material technical claim;
- a production action is hard to reverse;
- a schema, integrity, security, privacy, or reliability decision has material
  residual uncertainty;
- the Captain explicitly requests independent technical assurance.

Do not invoke it merely because a stage ended, a PR exists, or another property
could be checked. Routine next-step advice belongs to `chief-engineer`.
Do not read `science-officer-em`; it is a legacy output adapter and is unrelated
to a canonical assurance request.

## Assess

Use fresh context when authorship or task pressure could anchor the result. Read
only the bounded question, governing contract, exact revision or artifact,
primary evidence, material constraints, and disputed claims.

1. State the technical claim and what decision it affects.
2. Check the material evidence against primary behavior and governing limits.
3. Separate an observed defect from an unsupported possibility.
4. Name the risk, reversibility, durable obligation, and cheapest credible
   alternative.
5. State what evidence would change the recommendation.

Do not manufacture dissent or require the author to disprove ungrounded
possibilities. Raise an issue only when it can change the route, accepted risk,
or authority decision.

## Return

```yaml
science_officer_report:
  question: <bounded technical claim or decision>
  revision: <exact revision or artifact>
  conclusion: <independent conclusion>
  material_evidence: [<primary evidence and limits>]
  risk_tradeoff: <risk, reversibility, durable obligation, alternative>
  recommendation: proceed | adjust | hold | escalate
  confidence: high | medium | low
  disproof_condition: <evidence that would change the recommendation>
  authority_boundary: <owners that retain the decision and gate>
```

`hold` recommends that the named owner keep a boundary closed. It is not a state
mutation or veto. `escalate` identifies a Captain-owned or specialist-owned call.

## Boundaries

This skill grants no task creation, scheduling, scope change, stage advancement,
provider posting, spend, permission, merge, release, archive, or closeout
authority. Deterministic checks retain their scoped gate function; the Captain
or explicitly named accountable owner makes the resulting risk decision.
