---
title: Three corrections to kc-pr-review from a live run, one of which wastes 140K tokens per hit
status: backlog
source: maintainer feedback from a live kc-pr-review run on DataRecce/recce-cloud-infra #1596, received 2026-07-27 (kc-pr-flow 1.9.1)
design:
id: znbbgryxgzrfmsh61ebaf137
---

Three prose corrections to `skills/kc-pr-review/SKILL.md` from the same live run that produced
`mock-boundary-contract-prescan`. All three edit the same file, so they are one slice rather than
three. Ordered by cost of not doing them.

## 1. An in-flight Codex run reads as a failed one — highest value, smallest edit

`codex exec` takes 2–7 minutes on a mid-size diff and writes its output file **only on
completion**, so the file is 0 bytes for the entire run. The reporter checked size mid-run, read
it as a failed dispatch, re-dispatched, and paid for a full duplicate run — roughly **140K wasted
tokens** in one sitting.

The documented failure mode does not cover this. `SKILL.md:415` says: *"if `codex exec` returns
non-zero, surface one line … and continue"* — verified present at 1.9.1. That is a rule about a
run that **returned**.

**Measured before adopting the reporter's wording, and the measurement changed the fix.** Two
probes of one prompt on this machine, sampling output size every 2s:

| mode | size trace | final |
|---|---|---|
| `codex exec … --json` | `0s=0  4s=405  20s=686  32s=16779  48s=22474` | 22474 B |
| `codex exec …` (plain) | `0s=0 … 14s=0` | 59 B |

The reporter's observation is correct **for the mode this skill prescribes**, and that is the root
cause rather than a documentation gap: `SKILL.md:405-413` invokes `codex exec` with no `--json`,
then tells the reader to "Parse the output for `[SEVERITY] (confidence: N/10) file:line —
description` lines". Plain mode emits only the closing message, so the file really is 0 bytes for
the whole run. With `--json` it is growing within four seconds and the ambiguity does not exist.

Two candidate fixes, and the cheaper one is the worse one:

- **Teach tolerance** — add "an empty output file means still running". Removes this
  misdiagnosis but keeps a dispatch with no progress signal, so the next reader still cannot
  distinguish a wedged run from a slow one.
- **Remove the ambiguity** — switch the prescribed invocation to `--json` and parse findings from
  the terminal `agent_message` event instead of raw stdout. Costs one parsing layer.

The second is preferred, and this repo already holds the argument for it: `mini-dispatch` records
the same lesson on the claude side — plain text "records what the leg *says* it did and nothing
about what it *ran*", and `tool_use`/`tool_result` events are the only execution evidence. `--json`
additionally puts a `thread.started` session id on the first line, which is the precondition for
`codex exec resume` if steering a mid-flight review is ever wanted.

This makes item 1 **not a pure prose correction** like items 2 and 3 — it changes an invocation
and a parse. Ideation decides whether that keeps it in this slice or splits it out.

Either way the liveness note stands, because this repo has an adjacent hazard on record: `ps` is
sandbox-filtered on this machine, so "no process visible" is not evidence of death either.
Liveness is judged by artifact growth or a task notification, never by a single size sample.

## 2. Mutation evidence must name the layer it covers

The reporter mutation-tested three claims before submitting; all three correctly killed their
tests. All three mutations landed **inside the layer already being inspected**. The real defect
was one layer down, in a method no mutation touched.

A clean mutation round on the wrong layer is indistinguishable from a clean round on the right
one, so it does not merely fail to help — it manufactures confidence. Proposed for the Rules
block:

> **Mutation evidence must name the layer it covers.** "The test went red when I mutated the fix"
> proves the test guards *that* line, not that the line is the one that matters. Before accepting
> a mutation round, ask "which layer would have to be wrong for this fix to be worthless?" and
> mutate there. The cheapest form is mutating the collaborator the tests stub. If that is
> impossible because the collaborator is patched away, that impossibility is itself the finding.

The last sentence is the load-bearing one: it converts an obstacle into a detection. It is also
the prose counterpart of `mock-boundary-contract-prescan`, which catches the same class
statically — cut this one whether or not the pre-scan lands, because it covers the cases grep
cannot reach.

## 3. Stacked PRs have a CI blind spot, and the honest version is narrower than the dramatic one

A PR targeting another feature branch matches no `pull_request: branches: [main]` trigger, so its
head carries zero check-runs; workflows omitting `types:` default to
`[opened, synchronize, reopened]`, so GitHub's automatic base retarget on parent merge does not
start a run either.

The reporter initially wrote this up as severe and **had to correct themselves** — merging the
stacked PR down is a push to the parent's head branch, which triggers the parent's own CI, and the
parent targets `main`. The code normally cannot reach `main` ungated. The real residual is only
that the stacked PR is merged on local evidence, with breakage surfacing on the parent.

That self-correction is the more valuable half and should survive into the wording:

> When `baseRefName != main`, note that this PR's own head may have no check-runs. Before
> reporting it, check `gh api repos/<owner>/<repo>/commits/<parent-head>/check-runs` — the parent
> PR usually still gates the combined code. Report the residual, not the worst case, and state the
> merge order.

## Not in scope

§4.5j needs no action. The reporter confirmed it fired correctly against their **own** doc change,
catching two false normative claims ("**Every** GitLab-backed endpoint…", "`detail` … **never**
contains…") that were untrue for four out-of-scope sites. Keep it as a regression reference; do
not touch it in this slice.

**AC-1 — A reader of the Step 4-Codex block can tell an in-flight run from a failed one without re-dispatching.**
Verified by: the dispatch block stating the empty-file-means-running rule and a liveness check that does not rely on file size or `ps`. Falsified by: the block still describing only the non-zero-return case.

**AC-2 — The Rules block requires a mutation round to name the layer it covers.**
Verified by: the rule present, including the patched-away-collaborator clause. Falsified by: mutation guidance that a round confined to the inspected layer would satisfy.
