---
name: engineering-judgment
description: "Optional portable policy for independent engineering synthesis, reviewer adjudication, risk trade-offs, and advisory recommendations"
version: 0.1.0
---

# Engineering Judgment

This optional mod supplies professional engineering judgment without creating a
workflow role, provider integration, or second gate system. A repository activates
it by vendoring the file and declaring it on the stages where judgment is required.

Mechanical receipts establish bounded facts about declared inputs. They do not
decide whether a technically possible direction is necessary, maintainable, or
professionally sound. This mod turns those facts and primary evidence into a
reviewable recommendation while preserving existing authority.

## Inputs

Use the smallest evidence packet that can settle the question:

- the decision or disputed claim and the exact revision under review;
- the accepted outcome contract, constraints, non-goals, and captain rulings;
- governing contract and primary-source behavior at the relevant code or runtime
  path;
- applicable `PASS | FAIL | UNKNOWN | UNAVAILABLE` receipts with their bound
  inputs and evidence references;
- reviewer findings with citations, conflicting positions, and available
  verification;
- value, delivery risk, reversibility, durable maintenance cost, and the result
  that would reverse the recommendation.

Missing evidence stays missing. Green mechanical status may support a
recommendation, but it does not substitute for engineering judgment.

## Procedure

1. **Bind the question.** State the decision, accepted value, exact revision,
   material constraints, and whether the proposed action is reversible.
2. **Adjudicate before escalating.** Check each disputed finding against the
   governing contract and primary-source behavior. Reviewer confidence and labels
   carry no authority. Record each finding as `supported`, `unsupported`, or
   `unresolved`, with the evidence and contract clause that control the call.
   A finding recorded as unsupported is not a blocking basis; its supported
   residue, when present, is recorded as a separate finding before entering the
   recommendation.
3. **Perform independent synthesis.** Compare the accepted value, primary
   evidence, receipts, reviewer disagreements, risk, reversibility, and ownership
   cost. A status relay, checklist digest, or author self-attestation is not a
   judgment. Schedule pressure, sunk cost, and an instruction to conclude are
   trade-off inputs rather than substitutes for primary-source adjudication.
4. **Make the trade-off explicit.** Name the risk that matters now, the benefit
   being purchased, the cost and long-term obligation being accepted, and a
   concrete alternative. Technically possible work that is professionally
   unsound receives `costly_no`; feasibility does not imply `proceed`.
5. **Return one recommendation.** Choose `proceed`, `narrow`, `return`,
   `block`, or `costly_no`. Record unresolved dissent and the evidence that
   would change the route instead of hiding disagreement behind confidence.

## Pre-presentation convergence

Before an irreversible, schema, or scope-cut decision is presented to its
captain-owned authority, obtain fresh independent synthesis from context that did
not produce the proposal. Reconcile conflicting findings against the governing
contract and primary evidence, then present one recommendation, its material
dissent, its risk/cost trade-off, and its disproof condition. The captain receives
a decision-ready judgment rather than competing status relays.

This requirement does not transfer the decision. The captain still owns scope and
irreversibility; the repository's declared gate and work-item authorities still
own their state transitions and verdicts.

## Advisory record

```yaml
engineering_judgment:
  question: <decision or disputed claim>
  revision: <exact revision or artifact>
  evidence_synthesis: <primary evidence, receipts, and material limits>
  adjudications:
    - finding: <stable finding reference>
      disposition: supported | unsupported | unresolved
      basis: <governing clause and primary evidence>
  risk_tradeoff: <benefit, risk, durable cost, and alternative>
  recommendation: <concrete next action>
  route: proceed | narrow | return | block | costly_no
  confidence: high | medium | low
  dissent: <material disagreement or empty>
  disproof_condition: <evidence that would change the route>
  authority_boundary: <captain, gate, and work-item owners that retain authority>
```

The record is advisory. Its route is not a gate outcome and does not replace,
rewrite, or synthesize `PASS | FAIL | UNKNOWN | UNAVAILABLE` receipts. A
`block` route recommends that the governing authority keep a boundary closed;
a `costly_no` route recommends declining technically possible but
professionally unsound work. Neither route mutates state.

## Stage obligations

| Stage | Obligation |
|---|---|
| `backlog` | No judgment record is required. |
| `ideation` | Apply this mod when primary evidence or reviewer conflict affects value, risk, reversibility, schema, or a scope cut. Produce the pre-presentation record before asking for the captain-owned decision. |
| `implementation` | No new adjudication is required unless approved premises materially change; return that change to the authority and stage that owns it. |
| `validation` | Adjudicate disputed findings against the exact revision, governing contract, and primary behavior. Return an advisory record to the existing gate or captain-owned authority. |
| `done` | Do not create a retrospective judgment to repair a missing earlier decision. Preserve the accepted record with its evidence. |

## Boundaries

This mod grants no task creation, sprint admission, scheduling, stage advancement,
provider posting, policy edit, merge, or closeout authority. It does not prescribe
a persona, model, agent topology, tracker, delivery provider, thread-reply format,
or orchestration lifecycle.

A recommendation does not waive a non-pass gate receipt, accept a red residual,
change approved scope, or make an irreversible decision. Existing authorities
perform those actions under the kernel and the repository binding.

## Adoption

1. Vendor this file under the repository's workflow `_mods/` directory.
2. Declare it on `ideation` and `validation`, or on a narrower set justified by
   the repository's decision topology.
3. Bind captain, gate, and work-item authority through the existing Local Profile.
4. Exercise one reviewer-conflict case and one technically possible
   `costly_no` case before treating the local procedure as established.
