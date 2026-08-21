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

- accepted journey, constraints, non-goals, exact owners, and the observable
  semantics this work may change;
- applicable lifecycle and specialist-risk obligations;
- rollback or forward-recovery policy;
- falsifiable acceptance and release checks;
- a file-level `where it touches` table;
- the stop numbers implementation halts on.

Stop when the smallest operable route is decision-ready. Escalate scope,
irreversibility, and accepted residual risk to the Captain.

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
