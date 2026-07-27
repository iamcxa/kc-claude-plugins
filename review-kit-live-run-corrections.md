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
run that **returned**. An empty output file is the normal in-flight state, and nothing tells the
reader so.

Proposed, near the Step 4-Codex dispatch block:

> Codex takes 2–7 minutes on a mid-size diff and writes its output only on completion. **An empty
> output file means still running, not failed.** Check process liveness before concluding failure;
> never re-dispatch on file size alone.

This composes with a hazard this repo has already recorded elsewhere: `ps` is sandbox-filtered on
the maintainer's machine, so "no process visible" is also not evidence of death. Liveness is
judged by artifact mtime or a task notification.

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
