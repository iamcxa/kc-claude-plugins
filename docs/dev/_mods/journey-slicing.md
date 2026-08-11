# Journey slicing

Version 0.1.0.

A carve is either a piece of the deliverable or a layer of it. This reference is
how to tell them apart before the work starts, and what a first slice owes the
person who will look at it.

It applies wherever an accepted outcome is decomposed into work items — the step
`kernel.md`'s outcome-first route calls **Accepted outcome**, before the
reverse-recovery audit recovers a seam. Repositories opt in through their stage
`Policy mods` list, the same way they adopt the audit.

The prose below is retained close to the wording it was written in, in a
repository that paid for each clause at a gate. Rewriting it into kernel register
would lose what the clauses were bought with.

## Journey before mechanism

Exercise the thinnest end-to-end journey first, then the riskiest mechanism
within it, and it is in this order for a reason. "Riskiest mechanism first" is
satisfied by proving a protocol against a cooperative fixture, which is a real
proof of the mechanism and no proof that anything works. A spike that exercises
the thinnest thing a person can actually do — with no fixture standing in for a
real participant — finds the gaps that only exist between components, and finds
them in the first hour rather than at the gate.

## A walking skeleton has no scope boundary while it carries one

A work item carrying its sprint's walking skeleton writes every part of the
journey crudely, including parts other items will own, behind a flag that keeps
the ordinary path clear of it.

It emits a **shortcut inventory** — every fake, stub, hardcode, fixed value and
skipped validation, each naming the item that replaces it — which becomes those
items' scope.

Asking "is this mine?" during skeleton work is the layered carve returning; the
answer is "yours, crudely."

## A slice that changes no observable behavior is not a slice

If a work item's own body can say that sentence about its scope as a
reassurance, the carve is a layer rather than a piece of the deliverable, and it
can pass every gate while delivering nothing a person can do. Say what
observably changes, or say that the item is scaffolding for a **named** sibling
and cannot be validated alone.

## At most two slices, and the first one is demoed

The first slice lands, the approving authority sees it, and that is the
alignment check before the second finishes the item.

**The test is independent blocking, not size** — *if it can be blocked on its
own, it is an item, not a slice.* An item needing three or more slices is more
than one item. This is the one carve check that needs no judgment and no
reading of the diff: name what would block this piece alone, and if the answer
is a real blocker, re-cut.

Name the demo, and offer it unprompted. A day of decomposition, gates and
ledgers with nothing demoable at the end of it is a reportable outcome, not a
quiet one — progress and demoability are not the same purchase, and status will
show movement either way.

## Checks a reviewer can run

None of these needs a model:

| check | fires when |
|---|---|
| slice count | an item declares more than two slices |
| unnamed scaffolding | an item or PR body matches `not reachable`, `no observable behavio(u)r`, or `scaffolding` without naming the sibling it scaffolds |
| skeleton without inventory | an item marked walking-skeleton carries no shortcut inventory |

The second check enforces text this reference already requires — the named
sibling — rather than adding policy.

## Why the layer carve survives review

A layered carve is not caught by reviewing the code in it. Each layer can be
correct, tested, and well-described while the set of them delivers nothing. The
tell is in the item's own prose, not its diff, which is why the checks above read
bodies rather than code, and why they belong before implementation rather than at
a code review.
