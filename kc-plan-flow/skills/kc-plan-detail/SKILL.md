---
name: kc-plan-detail
description: Decide how to build it. Take value issues and their open questions, get the code facts from the archaeologist, cut sub-issues along what is actually missing, and write them in the format plan-lint reads. Use after kc-plan-value; verification belongs here, not to a later gate.
---

# Plan the detail

Load `references/kernel.md` first. It owns how a claim is made and checked -- asking rather than confirming, citing by symbol with its ref, reading current state before judging it, checking rather than remembering, adding nothing without a reader, and one fact with one home. This file owns only what is left.

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

**Refuse an answer with no command and no ref.** That is the contract; an answer missing
it is not evidence, whoever produced it. The rest of how to ask is in the kernel.

You will get findings back that are `MISSING` on the trunk and present on a
branch. Read them as work not yet done, not as code to relocate. A closed branch
is a record of an attempt.

## Reuse the excavation, and keep it

`kc-plan-value` has already asked this seat about the cut. Start from its answers
rather than re-asking them: what exists, on which ref, classified, is exactly the raw
material for cutting along gaps.

Two things make that reuse real rather than aspirational:

- **The seat does not survive a session.** It is addressable while a session lives and
  unreachable afterwards, whatever the contract implies. Assume you are talking to a
  fresh one and hand it the earlier reports.
- **So the reports have to be written down whole.** `archaeology` carries the command,
  the evidence, the stratum and the stated limits, not a three-field verdict. A
  classification without its command is an opinion, and a finding without its
  `did_not_check` is a bounded search wearing an unbounded conclusion.

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

## Exactly one sub-issue owes a handoff

A value's acceptance is performed by a person, on the branch where the work landed. That
person needs the branch runnable and the run written down: install this, run that, hand
the link to someone, expect to see this.

**That debt belongs to the topmost sub-issue in the stack, and to no other.** Which one
that is comes from the dependency graph, not from who wrote the most. Asking every
sub-issue for a handoff produces the same instructions in several places, and several
copies of one fact is the shape that drifts.

The handoff is not the acceptance. The sub-issue makes it performable; it does not
perform it and does not claim it. This is the same relationship as making a pull request
ready for review rather than approving it.

## An acceptance criterion needs something that can measure it

"Paints in under half a second" reads as precise and was unmeasurable: neither repository
carried any paint instrumentation, no performance budget in CI, no dependency that could
report one. The criterion could not be failed, which means it could not be passed either.

Before writing a number, name what reads it. If nothing does, either the instrument is
the work and belongs in its own sub-issue, or the criterion is a wish and belongs in
conversation.

## Replacing something means saying why it exists

A sub-issue proposing to replace an existing implementation states, first, why that
implementation is the way it is -- from its own source, not from memory.

One proposed swapping a hand-rolled Markdown renderer for a pinned library. The
hand-rolled one carries its rationale in its header: it escapes first and emits only tags
it controls, so no byte of a shared artifact can become live markup. That is a security
decision, and the ticket read as though it were an oversight. A replacement whose ticket
cannot state what it is giving up is a decision disguised as a task.

## An issue in flight is left alone unless the edit changes what someone does

Work that has already started is the one thing this contract can damage rather than
improve. Reformatting it produces a tidier ticket, a changed body under someone's open
pull request, and no difference to what they build.

So the test is not whether it matches the current format. It is whether the person doing
it would act differently after reading the edit. Adding a fact they need, yes. Adding
the sections the linter wants, no.

One session recut a ticket into full format two hours after its author opened two pull
requests against it, and nothing broke, which is why no rule came out of it at the time.
An omission leaves no wreckage to learn from -- that is what makes this rule harder to
arrive at than the others here, and no less real.

## Estimate the technical work, and only for one question

Points on sub-issues, none on the value issue above them. A value issue has no work of
its own -- the building happens beneath it -- so a number there counts its children
twice.

The question the estimate answers is whether the milestone fits before its date. That
is all. It is not a velocity, not a commitment, and not a measure of whoever picks the
work up; the moment it is any of those, it stops being an estimate and starts being a
negotiation.

If the points do not fit the date, say so before the date proves it. Cutting scope is
the captain's decision and needs the arithmetic in front of them.

**Say where the number came from.** `judgement` is a reading of the ticket: it orders
work and cannot promise a date. `calibrated` means a reference class was measured and
the scale moved to fit it. A judged number presented as arithmetic is the false
precision this whole contract exists to refuse -- one plan reported 34 points against a
three-day milestone with nothing behind any of them, and it read like a measurement.

Calibrating needs finished work, so a first plan is always judged. What it costs to
become calibrated is small and specific: for three tickets that finished, record the
change size that landed and the time from starting to reviewable, then move the scale.
The tracker already holds both, and a repository's own merged history gives the
reference class -- in one of them the median change was 61 lines across 3 files and the
top quarter began at 367 lines across 7, which places a ticket far better than any
adjective.

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
- **The accepted outcome is the one sentence whose falsity means the ticket failed.**
  Not a summary of the criteria under it. When it restates three of them, delete
  the restatement rather than the criteria: a reader who has to check whether two
  passages agree is doing the work the format was supposed to save them.
- **Keep the conclusion, drop the record.** Which surfaces are involved belongs in
  the body; the search that found them belongs in the comment thread, because it
  ages at the speed of the codebase. One list of six surfaces named a symbol that
  was renamed the same day the ticket was built against it.
- A `Re-verified:` line carrying the command and an ISO date, **with no colon
  and no issue identifier anywhere in it**. The parser splits the line on `:`
  and reads the last word as the date, so `git show <ref>:<path>` breaks it —
  and so does a branch name containing a ticket id, because the tracker
  silently rewrites that into a link whose URL carries its own colons. Name the
  revision by short SHA and the search by symbol.
- A `Supersedes:` line naming an issue, or `none, searched: <query>`
- **At least one criterion has to name something that runs.** The rule matches the words
  `exit`, `script`, `log`, `run` or `prints` across an issue's criteria, and an issue where
  none of them appears reads as having no runnable acceptance however many criteria it
  carries. This plugin's own fixture failed it with two criteria until someone read the
  linter rather than the list. Do not pad a criterion with the word "run" to pass -- restate
  it as the thing somebody executes, which is what it should have said.
- **The `Re-verified:` line needs at least three words after the colon**, because the parser
  splits on whitespace and reads the last token as the date. A one-word command plus a date
  is two tokens and is refused as a format error, not as a missing line.

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

## Which of these rules a machine checks, and which it does not

Five of this plugin's rules are prose only: who performs an acceptance, the
builder-alone test, exactly one handoff per value, a criterion something can measure,
and stating why an implementation exists before replacing it. Nothing fires on any of
them.

That is not an oversight to fix by inventing five checks. It is the honest state, and it
belongs written down, because the same session that added a mechanical gate for
draft-first went on to add five rules with no gate and called them the same kind of
thing. A rule enforced by memory is enforced by whoever remembers, and a fresh session
carries nobody's corrections.

When one of them fails again, that failure is the evidence for making it mechanical.
Until then, read them.

## Close the loop

```bash
python3 docs/plan-flow/plan-lint.py fetch <project-id> <snapshot.json>
python3 docs/plan-flow/plan-lint.py lint <snapshot.json> [receipt.json]
```

**On a first projection there is no receipt yet, and that is not a failure.** The issues have
to exist before anything can judge them, so the document goes out with
`result: not-yet-linted` and no `receipt`, the projector creates the issues, and the run
after that fills both. Requiring a receipt up front made this loop impossible to finish on
its first pass, which is the shape of every ordering bug in this contract: a step asking
for the output of a step that comes later.

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

## How it reads is a different seat

`kc-plan-flow:kc-write-issue` owns the body. The format rules above are what the linter
reads; that skill is what a person reads, and a sub-issue has to survive both.

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
    command: <the command that produced it; without one the classification is an opinion>
    evidence: <what it returned, in enough detail to be disagreed with>
    stratum: <which ref carries it, and that ref's relation to the trunk>
    did_not_check: [<the question's edges>]
sub_issues:
  - title: <the gap it closes>
    gap: <what the archaeologist found missing or broken>
    accepted_outcome: <the section plan-lint requires, alongside non-goals>
    acceptance: [<"- **AC-1** — …", one string per criterion, bullet included>]
    non_goals: [<…>]
    re_verified: <command then ISO date, no colon and no issue identifier; may live in the thread instead>
    supersedes: <issue, or "none, searched: …">
    depends_on: [<titles of sub-issues under this value that must land first>]
    estimate: <fibonacci points, technical work only>
    estimate_basis: judgement | calibrated
lint:
  receipt: <sha>
  result: PASS | FAIL
  unjudged: [<issues the linter did not examine, and why>]
  known_limits: [<L2-single-cycle | L9-value-issue-has-no-file-surface>]
```

## Boundaries

No merging, no scheduling, no scope change. You write sub-issues and you run the
linter; whether the plan is worth building stays with the captain.
