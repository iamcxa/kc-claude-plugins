---
name: kc-plan-detail
description: Decide how to build it. Take value issues and their open questions, get the code facts from the archaeologist, cut sub-issues along what is actually missing, and write them in the format plan-lint reads. Use after kc-plan-value; verification belongs here, not to a later gate.
---

# Plan the detail

Turn each value issue into sub-issues a person can pick up and build.

**Verification lives here.** Deciding how to build something is the same act as
finding out what is already built, and a reviewer who catches a wrong file later
means two people did the job badly. There is no downstream fact-checking seat and
there should not be one: contested *judgment* goes to
`kc-dev-flow:science-officer`, and that is a different thing.

## Trigger

`kc-plan-value` has produced value issues, milestones and a question list, and
the captain has ruled on the cut.

## Ask before you cut

Send `questions_for_the_archaeologist` to
`kc-plan-flow:code-archaeologist` — one bounded question at a time, and the seat
stays addressable across the session so later questions cost less.

Two rules on how you ask:

- **Ask what is there, never ask for confirmation.** "Where does X live so we
  can move it" is a request to agree with you. "What decides X today, and on
  which ref" is a question.
- **Refuse an answer with no command and no ref.** That is the contract; an
  answer missing it is not evidence, whoever produced it.

You will get findings back that are `MISSING` on the trunk and present on a
branch. Read them as work not yet done, not as code to relocate. A closed branch
is a record of an attempt.

## Cut along the gaps, not along the layers

This is the whole move, and the easiest to get wrong.

Slicing by architecture gives you a CLI sub-issue, a UI sub-issue and a packaging
sub-issue. Each one is real work, none delivers the value alone, and the chain
is serial with no room to parallelise. That is a mental model of the system, not
a decomposition of the problem.

Slice by what the archaeologist found missing. If publish exists nowhere on the
trunk, that is one gap and possibly one sub-issue, whatever number of files it
touches.

Where the layers genuinely cannot land together — different repositories,
different deploys — say so, and check that the milestone above carries the
integration proof `kc-plan-value` required of it. Layered sub-issues under a
milestone with no integration owner is the shape that ships four green tickets
and a broken product.

## Write what the linter reads

`docs/plan-flow/plan-lint.py` judges the result. Its format is not negotiable and
a near miss is silent: an issue carrying seven acceptance criteria reported `0
ACs` because the criteria had no bullet marker.

- Acceptance criteria as a bullet list, each `- **AC-1** — …`. Without the
  bullet marker they are invisible: one issue carrying eight of them read as
  `0 ACs`, then as `8 ACs` once the markers went in, same text otherwise.
- Two sections, both required and both easy to half-satisfy: `## Accepted
  outcome`, and `## Non-goals` as a `- ` list. Supplying only the second gets
  you a complaint about the first.
- A `Re-verified:` line carrying the command and an ISO date, **with no colon
  and no issue identifier anywhere in it**. The parser splits the line on `:`
  and reads the last word as the date, so `git show <ref>:<path>` breaks it —
  and so does a branch name containing a ticket id, because the tracker
  silently rewrites that into a link whose URL carries its own colons. Name the
  revision by short SHA and the search by symbol.
- A `Supersedes:` line naming an issue, or `none, searched: <query>`

The `Re-verified:` line is a paste of what you already ran, not a ceremony
performed afterwards. If you cannot paste one, you did not check.

`Supersedes:` exists because a session once created a duplicate of a ticket that
was already open. It does not make you recognise a duplicate; it makes the search
happen and leaves a trace when it does not.

## Every code sentence carries its receipt

Name findings by symbol, route or behaviour, and name the ref. A line number is
convenience and goes stale silently; a file described as current that lives only
on a closed branch is the same failure one level up.

An acceptance criterion you cannot trace to the captain's words or to a verified
fact is one you invented. Delete it — acceptance criteria are outward-facing
commitments and those are not yours.

## Close the loop

```bash
python3 docs/plan-flow/plan-lint.py fetch <project-id> <snapshot.json>
python3 docs/plan-flow/plan-lint.py lint <snapshot.json> [receipt.json]
```

Run it from the repository root; it resolves
`kc-dev-flow/scripts/linear-admission.py` relative to the working directory.
`LINEAR_API_KEY` must be set for `fetch`.

A `FAIL` is a ticket to fix, not a result to explain. Report the receipt hash
with the plan.

Note what it does not judge: only issues admitted to a cycle are checked, so a
recut that leaves its new issues un-cycled will lint clean while nothing it
produced was examined.

Two of its rules will fail on a plan shaped the way this plugin shapes one, and
neither failure is yours to fix by contorting the plan:

- **The by-product check wants every issue to claim a file nobody else claimed.**
  A value issue names no file, by contract. So value issues fail it and always
  will. The check belongs among sub-issues, which do name surfaces.
- **The single-cycle check admits one cycle of work.** A plan cut into
  milestones across three cycles cannot satisfy it while the previous cycle
  still holds anything.

Report both as limits of the linter with the receipt, and leave the plan alone.

## Return

`kc-plan-detail/v1`, in `schemas/`. Validate with
`schemas/validate-contract.py` before writing anything to the tracker — it
catches the three format traps above without a round trip through Linear.

```yaml
schema: kc-plan-detail/v1
value_issue: <the parent>
archaeology:
  - question: <as asked>
    classification: <the tier it came back as>
    ref: <the ref it was answered against>
sub_issues:
  - title: <the gap it closes>
    gap: <what the archaeologist found missing or broken>
    accepted_outcome: <the section plan-lint requires, alongside non-goals>
    acceptance: [<"- **AC-1** — …", one string per criterion, bullet included>]
    non_goals: [<…>]
    re_verified: <command then ISO date, no colon and no issue identifier>
    supersedes: <issue, or "none, searched: …">
lint:
  receipt: <sha>
  result: PASS | FAIL
  unjudged: [<issues the linter did not examine, and why>]
  known_limits: [<L2-single-cycle | L9-value-issue-has-no-file-surface>]
```

## Boundaries

No merging, no scheduling, no scope change. You write sub-issues and you run the
linter; whether the plan is worth building stays with the captain.
