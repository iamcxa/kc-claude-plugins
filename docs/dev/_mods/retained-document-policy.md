---
name: retained-document-policy
description: "Portable rules for retained documents that stay current without historical or mutable-state upkeep"
version: 0.1.0
---

# Retained Document Policy

## Why this exists

The expensive documentation failures are often not missed updates. They are
sentences that were true when written, needed no author to be wrong, and went stale
on their own. No behavior change necessarily triggers a maintenance obligation;
time alone can make a mutable snapshot false.

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

## Stage obligations

| Stage | Obligation |
|---|---|
| `backlog` | None. |
| `shape` / runtime `ideation` | When the task adds or removes a retained document, name which rule the change is under and what the per-section overlap check will cover. |
| `build` / runtime `implementation` | Apply Rules 1–3 and 6–8 to every retained document the task touches. A selected route without `shape` performs the addition/removal classification before its first edit. For an addition or deletion, execute Rule 4. For a deletion, also execute Rule 5 and record where each block landed. |
| `prove`, `verify-deliver`, or `verify` / runtime `validation` | Spot-check the checks. Take claims from the changed documents and run the check each one names; a claim whose named check does not run, or does not distinguish true from false, is a finding. For an addition or deletion, repeat Rule 4 independently. For a deletion, also attempt Rule 5 independently — try to find a block the implementer missed. |
| `release` / `done` | None. |

No receipt, bound project-context authority, prescribed filename, or diagram tool is
required. The stage worker applies the policy and the validator checks it.

## Non-goals

- No linter, documentation site, diagram tool, generated prose, watcher, lifecycle
  hook, or background job.
- No general documentation refresh unrelated to the approved behavior change, and no
  authority to retrofit this policy across documents no task touches.
- No authority to delete a document. Removing one from the set is a scope decision
  and stays with whoever holds scope.
- No authority to create a task, schedule work, expand scope, or pause delivery beyond
  the workflow's existing validation verdict and stage-return mechanism.

Automation may be proposed later only after repeated measured drift shows that the
stage obligation is insufficient. Adoption of this mod does not authorize it.

## Adoption

1. Vendor this file under the workflow's `_mods/` directory.
2. Add its local path to each profile's applicable shape, build, and verification
   stage as a typed conditional reference. Bind `retained_document_change`; do not
   load the file when that trigger is false.
3. Apply Rule 4 once across the existing document set before adding anything. The
   first pass is where a set discovers what it already duplicates.
