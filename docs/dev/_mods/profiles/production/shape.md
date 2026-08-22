# Production Shape

Working perspective: staff engineer and delivery lead.

## Mission

Define the production outcome, architecture and lifecycle ownership, failure
policy, rollout, and release boundary.

## Conditional shape references

```json
{
  "schema": "kc-dev-flow-conditional-references/v1",
  "references": [
    {
      "path": "../../reverse-recovery-audit.md",
      "trigger": "brownfield_capability_change",
      "receipt": "reverse_recovery"
    },
    {
      "path": "../../journey-slicing.md",
      "trigger": "multi_slice_required",
      "receipt": "journey_slices"
    },
    {
      "path": "../../retained-document-policy.md",
      "trigger": "retained_document_change",
      "receipt": null
    },
    {
      "path": "../../project-context-maintenance.md",
      "trigger": "project_context_claim_may_change",
      "receipt": "project_context"
    }
  ]
}
```

## Required output

- accepted journey, constraints, non-goals, and exact owners;
- applicable lifecycle and specialist-risk obligations;
- rollback or forward-recovery policy;
- falsifiable acceptance and release checks.

Stop when the smallest operable route is decision-ready. Escalate scope,
irreversibility, and accepted residual risk to the Captain.

## Journey statement

The accepted journey is a step-by-step account of what a person does and what
happens behind each step, in the order it happens. Three rules bind it:

- **Mark every step OBSERVED or DESIGNED.** Observed means someone watched it run
  on the real components. Designed means written and not yet exercised. A
  demonstrated step and a designed step must not read alike.
- **Name programs, not roles.** Say which process acts, and which file or stream
  carries the fact. "The caller" and "the client" hide the seam that breaks.
- **Describe the unhappy paths in the same terms as the happy one.** Abandonment,
  no answer, death, timeout. A journey that describes only success hides the risk
  surface it was written to expose.

Declare alongside it the observable semantics this work may change — command
grammar, stored formats, authority, runtime behaviour. A small diff that changes
an undeclared semantic is a boundary breach, and a size signal cannot catch it.
