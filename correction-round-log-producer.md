---
id: kaqymmyr0cahm4jqbtkjg5tz
title: A correction round is answered only because the First Officer says so; the recorder would refuse an unanswered one
status: backlog
source: found 2026-08-23 tracing why `gate record --round` is unusable here; the Captain's challenge — that Spacedock itself is the reader — turned out to be right in the way that matters
product: repo-platform
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## Problem

Three correction rounds ran on one entity in this workflow. In each, a reviewer
raised findings, the Captain rejected, a worker responded, and the First Officer
asserted in prose that every finding had been dispositioned. **Nothing checked
that assertion.** The `### Feedback Cycles` record is written by the same actor
that decides the round is finished.

Spacedock's round recorder carries exactly that check. Before publishing a
round it refuses an unanswered log:

> `round %s is not closed: %s. Nothing was recorded; the room is immutable, so
> an open log would truncate the record permanently.`

`roundLogClosed` (`internal/gates/round.go`) refuses a log whose last entry is a
dangling Annotation, or a verdict demanding a response that was never logged.
That is a check that can fail, standing in for a First Officer's eye.

**What it is not.** There is no downstream consumer. `ValidateRoundFile` has one
caller — `internal/cli/cli.go`, on the line after a successful record, printing
the summary. A GitHub code search for `review-round` returns
`internal/gates/round.go`, the schema, the docs and the skills; `internal/status`
is not among them, so `status --validate` does not consult it either. The value
is the record-time refusal and the immutable, addressable room, not a reader.
Git already makes the prose record tamper-evident; what the room adds is the
`review-round` pointer binding an entity to one round and a divergence refusal
on re-record.

## Dependency

Blocked on folder-form entities (`8gz8mv84sgzvbp1mdd4c3qkj`): `gate record
--round` refuses a flat `<slug>.md` entity unconditionally, filed upstream as
spacedock#755.

## The producer contract, read from source so it is not re-derived

Verified against `internal/gates/review.go` and `round.go` at `main` `bcaa4e0b`.
Two inputs, both caller-supplied; the recorder copies them into the derived room
`review/<stage>/round-<cycle>`.

**`briefing.json`** — the canonical Briefing. `gate prepare` already writes this
object as `gate-briefing.json`; the contract states no Briefing basename is
canonical, and `--round` only requires the literal filename. `verifyRoundArtifacts`
skips any artifact whose URI carries a scheme, and every artifact this workflow
emits is `git-root://...`, so no file needs to be copied into the room.

**`briefing.review.jsonl`** — UTF-8 JSONL ending in a newline, one object per
line, `id` unique, `includes` referencing only earlier ids:

- `{"type":"Annotation","id":…,"briefing":<briefing id>,"by":…,"at":<RFC3339Nano>,"includes":[…]}`
- `{"type":"Resolution",…,"decision":"approve|revise|hold","reason":…,"includes":[…]}`

At least one Resolution; the first is the verdict. A non-`approve` Resolution
needs a `reason` or an included Annotation. The log must end either at an
`approve` verdict or at a later Resolution answering it.

That maps onto a correction round as: reviewer Annotations, the Captain's
`revise` Resolution, disposition Annotations, a closing Resolution.

## Fit note

Unlike its blocking dependency, this item produces a tracked artifact in the
repository — a serializer the First Officer invokes at the point it currently
writes `### Feedback Cycles` — so it is ordinary repository work rather than a
state migration.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
