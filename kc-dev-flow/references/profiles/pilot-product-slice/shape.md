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
- task-specific acceptance checks able to falsify the slice;
- a file-level `where it touches` table;
- the stop numbers implementation halts on.

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

## Where it touches

Name the files this work changes as a table of path, lines now, and lines after.
It answers where, not how big, so the Captain reads the blast radius without
reading the reasoning behind it.

Build it from sites counted in the current tree — an opened file, a resolved
reference — rather than from an impression of the work. A count carried over
from a sibling work item or from a reviewer's remark is a lower bound until this
item confirms it.

The table is diagnostic and holds no gate; the shared core already fixes that
LOC and file counts are diagnostic signals, never pass/fail gates. What it makes
askable is a file that appears here and nowhere in the journey, or a file the
journey depends on and this table omits. It is also where the stop numbers below
come from.

## Stop numbers

Name the counts at which implementation stops and reports rather than
continuing: a total, a file count, and a trip point for the area most likely to
run away. Take them from the `where it touches` table, so they rest on counted
sites rather than on a feel for the work.

They are stop conditions, not budgets. Without an expected count on record
nothing about the work can look wrong — a change several times its expected
size reads exactly like one that landed as shaped, because nobody wrote down
which was expected. The shared core fixes what a crossing does: stop, record the
observed count against the threshold, and hand back to the First Officer.
