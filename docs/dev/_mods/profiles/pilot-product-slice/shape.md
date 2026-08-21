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

- one accepted journey, explicit non-goals, and the observable semantics this
  work may change;
- persistence, recovery, and data-safety boundaries;
- task-specific acceptance checks able to falsify the slice;
- a file-level `where it touches` table;
- the stop numbers implementation halts on.

Stop when one implementation route is sufficient. Do not design for broad scale
or production operations.

## Journey statement

The accepted journey records each actor or runtime component's action and the
resulting behaviour, in the order it happens. Three rules bind it:

- **Mark every step OBSERVED or DESIGNED.** Observed means someone watched it run
  on the real components. Designed means written and not yet exercised.
- **Name the acting program, not a role.** Say which process acts and which file
  or stream carries the fact.
- **Describe the unhappy paths in the same terms as the happy one.** Abandonment,
  no answer, death, timeout.

Declare alongside it the observable semantics this work may change — command
grammar, stored formats, authority, runtime behaviour — or state that it changes
none.

## Where it touches

Name the files this work changes as a table of path, lines now, and lines after.
It answers where, not how big.

`lines now` is counted in the current tree — an opened file, a resolved
reference. `lines after` is this item's estimate. Mark a count inherited from a
sibling item or a reviewer's remark unverified until checked against the current
tree.

The table is diagnostic and holds no gate; the shared core already fixes that
LOC and file counts are diagnostic signals, never pass/fail gates. Reconcile it
against the journey in both directions, and take the stop numbers below from
it.

## Stop numbers

Name the counts at which implementation stops and reports rather than
continuing, each with its metric and the base it is measured against: changed
files, changed lines, and one named area most likely to run away. Take them from
the `where it touches` table.

They are stop conditions, not budgets. The shared core fixes what a crossing
does and who resumes the work.
