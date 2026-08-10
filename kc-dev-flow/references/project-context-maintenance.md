---
name: project-context-maintenance
description: "Portable stage obligations that keep authoritative product and architecture context aligned with approved delivered behavior, and rules for what the documents carrying it may contain"
version: 0.2.0
---

# Project Context Maintenance

## Why this exists

Project context is the stable explanation of what a product is, how it is shaped,
and which constraints must survive individual tasks. Work-item state explains what
is being changed now. Both can be correct in isolation while drifting apart: code
lands a new public contract, the task closes, and the next worker still plans from an
obsolete product or architecture description.

The kernel should require coherent authority without knowing a repository's document
names. The workflow README should bind local authority without re-implementing a
portable update procedure. Launchers should load policy, not contain product-specific
documentation logic. This mod owns the small stage obligation between those layers.

**It owns two halves, and they are separately adoptable.**

*Part 2* is the obligation above: when a task changes a described behavior, the
context change lands with it.

*Part 1* is what a retained document may contain, and it exists because the
expensive documentation failures are not missed updates. They are sentences that
were true when written, needed no author to be wrong, and went stale on their own.
Part 2 cannot reach those: no task changed the behavior the sentence described, so
no classification fires. Time did.

Part 1 needs no bound project-context authority and issues no receipt, so a
repository may adopt it alone. Part 2 requires both. Declaring one is not a
statement about the other.

---

# Part 1 — What a retained document may contain

Every rule below reduces to one move: **prefer a document that cannot go stale over
a document someone must keep fresh.**

## Rule 1 — a retained document is in the present tense

A retained document states what is the case. It carries no roadmap, no in-flight
work, no "coming in the next release", and no snapshot of a mutable system's current
value.

The test, applied before a sentence is added: **would this need rewriting after the
next merge or deploy?** If yes, it is work-item state, not documentation.

Work in motion belongs in the work-item store, where its status changes without a
prose edit. That is not a demotion — it is the only place a changing fact can live
without an author being responsible for noticing it changed.

*The failure shape this prevents: a status section that accumulated two false
statements without anyone touching it, in a document whose other sections were
accurate, so nothing signalled that part of it had stopped being true.*

## Rule 2 — a contract records rules; records live with the work

A document that states obligations may carry the incident that bought each rule,
because a rule with no failure scenario beside it reads as arbitrary and the next
reader simplifies the hole back in. That incident is part of the rule.

A free-standing chronological log attached to no rule is not. It is a record, and
records belong in the work-item store, the debrief, or wherever that repository
keeps history.

The distinction is checkable: **remove the passage and ask whether a rule becomes
unexplained.** If nothing becomes unexplained, it was a record.

## Rule 3 — every claim names a check, and the check is cheap

A claim in a retained document names the command, file, or line that would show it
false. "I checked" is not a check and neither is the author.

Prefer a check the reader can run in one line over a value the author measured. A
document that says *how to find out which version is deployed* stays true forever; a
document that says *which version is deployed* is a snapshot with a date on it.

## Rule 4 — no second copy of a live claim

Before a document is added to a set, and before one is deleted from it, check the set
**per section** rather than per file. Two documents may each be individually correct
and still disagree the moment one is updated.

A file-level "does this look like a duplicate" pass is not this check. It reports
clear on a file whose sections are duplicated one at a time.

## Rule 5 — before deleting, find each block's second home

Deletion is the preferred repair when a document has stopped being true. It is also
how evidence disappears.

So, per block and not per file: locate the same claim elsewhere, using **two search
strategies**, because one tool with one pattern is a sample. A block with no second
home is **relocated, not deleted** — moved rather than copied, so there is one copy
and it is the one a reader can find.

Frozen records — dated debriefs, handoffs, closed work items — that reference the
removed document are **left as written**. They record what was true then. The
correction is a new dated entry, never an edit to history.

*The failure shape this prevents: a deletion whose author had checked the file and
found it redundant, while two of its blocks existed nowhere else.*

## Rule 6 — written for the reader, not about the document

A retained document opens with what the reader can do, not with when it was written,
on what revision, or by whom. Provenance is evidence about the document; it belongs
in the work item that produced it.

Two consequences: **headings say what a reader is trying to do**, not what the
section is categorically; and **cross-references name their target**, because a bare
section number tells a reader nothing and silently rots when a section is added.

Where part of a document could not be verified — a command the author had no
credential to run, a system they could not reach — say so once, in place, rather
than letting the reader assume the whole was exercised.

## Rule 7 — a diagram's form follows its subject, and it is rendered before it ships

| Subject | Form |
|---|---|
| Messages between parties in an order that matters | sequence diagram |
| Components and what connects to what, no time axis | flowchart or graph |
| The states one thing moves through | state diagram |
| A directory or tree | plain text — a flowchart of a tree is worse than the tree |

A diagram is **rendered before it is committed**, not read as source. Rendering
proves it parses; comparing it against the code proves it is right. Both are
required, and the first will surface layout defects that hand-drawn ASCII hides — a
node connected to nothing reads as an item in a list and as an error in a graph.

## Rule 8 — repair in place before rewriting

When a document's structure and reasoning are sound and only its claims have gone
stale, repair the claims. A rewrite discards the parts that were right along with
the parts that were not, and re-derives judgments already made and paid for.

Rewrite when the document's *subject* is wrong — when it describes something that no
longer exists, or was written for a reader who no longer arrives.

## Part 1 stage obligations

| Stage | Obligation |
|---|---|
| `backlog` | None. |
| `ideation` | When the task adds or removes a retained document, name which rule the change is under and what the per-section overlap check will cover. |
| `implementation` | Apply Rules 1–3 and 6–8 to every retained document the task touches. For a deletion, execute Rule 5 and record where each block landed. |
| `validation` | Spot-check the checks. Take claims from the changed documents and run the check each one names; a claim whose named check does not run, or does not distinguish true from false, is a finding. For a deletion, attempt Rule 5 independently — try to find a block the implementer missed. |
| `done` | None. |

No receipt, no bound authority, no prescribed filename or diagram tool. Part 1 is
applied by the stage worker and checked by the validator.

---

# Part 2 — Keeping the bound context aligned with delivered behavior

## Rule

**Every approved task classifies its effect on the bound project context. When the
task changes a described product behavior, architecture boundary, public contract,
scope decision, or durable constraint, the approved context change lands in the same
delivery slice and fresh validation checks the changed claim against the delivered
behavior.**

Use one of two classifications:

- `none` — the task changes no claim made by the bound project context. Name the
  relevant described surface or explain why none is involved.
- `update` — name the bound authority, the routed claim locator that becomes stale,
  and the replacement claim already authorized by the task.

The classification is not permission to change product direction. Scope and
irreversible decisions remain with their existing authority.

## Inputs

- The repository's single bound `project_context` locator.
- The affected claim locator, when the bound authority explicitly routes to a deeper
  document.
- The approved work item, including its affected behavior and contract boundary.
- Any product or architecture ruling the work item already cites.

If the repository has not bound a project-context authority, this mod is not ready to
run. Binding the existing authority comes first; creating a new context document is
not the fallback.

## Part 2 Stage obligations

| Stage | Obligation |
|---|---|
| `backlog` | None. A cheap seed does not perform context analysis. |
| `ideation` | Record `none` or `update`. Name the described surface or routed claim, the approved replacement when applicable, and the check that will validate the classification. |
| `implementation` | Apply the approved context change with the behavior. A bounded defect that skipped `ideation` performs the same classification before its first edit and may only document the already-approved mechanical correction. If the stale claim extends beyond that correction, record the stale claim and return the slice to the task's approving authority for reclassification instead of writing a replacement. |
| `validation` | Execute the recorded `planned_check` against fresh behavior or runtime evidence. For `update`, check the landed context claim against the delivered behavior. For `none`, confirm that the delivered behavior changes no claim in the bound authority, starting from the named surface and not limited to it. Presence of changed prose is not proof. Record the evidence or return the slice when the authority remains stale or contradicts delivery. |
| `done` | No new analysis. For every classification, the existing receipt must contain fresh `validation_evidence`; for `update`, it must also point to the landed context change. |

Repositories may store the receipt in the work item or stage report. This mod does not
prescribe a filename, provider, or extra state store.

## Receipt

```yaml
project_context:
  impact: none | update
  authority: <single bound locator>
  claim_locator: <routed claim locator or none>
  surface: <described surface or none>
  stale_claim: <claim or none>
  approved_change: <replacement claim or none>
  landed_change: <pending | landed change reference | none>
  planned_check: <check able to falsify none or update>
  validation_evidence: <pending | fresh validation reference>
```

For `none`, `stale_claim`, `approved_change`, and `landed_change` are `none`;
`surface` names what must remain unchanged or is `none` when the planned check proves
that no described surface is involved. For `update`, implementation replaces the
pending `landed_change` with a reference inside the bound authority. For both
classifications, validation executes `planned_check` and replaces pending
`validation_evidence` with evidence that can fail.

## Ownership

- Product and architecture owners authorize changed claims.
- The implementation worker updates only claims already changed by approved scope.
- A fresh validator checks correspondence; it does not finish missing product work or
  invent the intended documentation.
- The project-context authority remains the source of truth. This receipt records the
  maintenance result and never becomes a competing context document.

## Non-goals

- No automatic rewriting, generated prose, watcher, lifecycle hook, or background
  job. The responsible stage worker or validator writes each field.
- No linter, documentation site, or diagram tool. Part 1 is applied by people at the
  stages that declare it.
- No mandatory filename, document format, tracker, or documentation site.
- No second product-context document, decision ledger, or mirrored task state.
- No general documentation refresh unrelated to the approved behavior change, and no
  authority to retrofit Part 1 across documents no task touches.
- No authority to delete a document. Removing one from the set is a scope decision
  and stays with whoever holds scope.
- No authority to create a task, schedule work, expand scope, or pause delivery beyond
  the workflow's existing validation verdict and stage-return mechanism.

Automation may be proposed later only after repeated measured drift shows that the
stage obligation is insufficient. Adoption of this mod does not authorize it.

## Adoption

**Declare the parts you need. They are independent.**

For Part 1 alone:

1. Vendor this file under the workflow's `_mods/` directory.
2. List it on `ideation`, `implementation` and `validation`, naming Part 1.
3. Apply Rule 4 once across the existing document set before adding anything. The
   first pass is where a set discovers what it already duplicates.

For Part 2, additionally:

4. Confirm the repository has bound `project_context` under the
   `kernel.md` Authority model. If it has not, Part 2 is not ready to run —
   binding the existing authority comes first, and creating a new context
   document is not the fallback.
5. List this mod on every stage with a non-`None` Part 2 obligation.
6. Exercise one `none` task and one `update` task before proposing automation.

A repository declaring Part 1 only records that Part 2 is not adopted, so the
omission reads as a choice rather than an oversight.
