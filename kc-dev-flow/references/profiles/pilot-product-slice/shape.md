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
