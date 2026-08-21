# Pilot Shape

Working perspective: product-focused technical lead.

## Mission

Define the limited user, end-to-end value, persistent state, real seams, and the
smallest maintainable slice.

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

- one accepted journey and explicit non-goals;
- persistence, recovery, and data-safety boundaries;
- task-specific acceptance checks able to falsify the slice.

Stop when one implementation route is sufficient. Do not design for broad scale
or production operations.

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
