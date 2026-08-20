---
id: jpyvk5rv2z7rr5vfydzfvaxb
title: "kc-dev-flow: measure whether the recent-failure digest changes agent behavior, before it ships"
status: backlog
source: "Captain ruling, 2026-08-20 — a PR exists to merge, not to open. The digest slice on iamcxa/dev-flow-fresh-failure-digest is built and gated but unmeasured, and merging an unmeasured improvement claim is how the mechanism it replaces shipped. Blocks improvement-loop-never-ran from delivery."
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr: local-merge:no-delivery-measurement-only
mod-block:
archived: 2026-08-20T10:12:07Z
---

## Problem

`improvement-loop-never-ran` built a recent-failure digest and proved it reachable: the loader
refuses an unvendored copy, and four contract-test assertions each fail with their own message
under mutation. None of that says an agent that loads the digest performs better than one that
does not.

The distinction is the whole point of the task that produced it. The mechanism being retired was
specified, CI-covered on one half, and never once useful. Shipping its replacement on the strength
of "the wiring works" would repeat that exactly, one layer up.

Two facts bound the work:

- **The instrument exists and is itself unvalidated.** `kc-pr-flow/scripts/review-ablation.sh` is
  an A/B harness with A/A' control arms, built for this question. It is parked with no accepted
  A/A verdict at roughly $264 per verdict, and its own `--arms` defect once dropped a middle arm
  and returned a plausible verdict for a comparison nobody asked for. Its corpus and spans table
  are bound to the review skill, so it is not a drop-in.
- **The digest's content is repository-specific.** Its 12 entries come from four debrief records
  in this repository. A corpus has to be tasks where those failure modes could plausibly recur, or
  the A/B measures nothing.

## Work profile receipt

## Accepted outcome and non-goals

A verdict that can come back negative, fixed before the runs. If the digest does not change
behavior, that is a result and the slice does not ship — the branch is deleted and the transport
stays retired on `main` only if a separate decision says so.

Open questions the shape stage owns:

1. Whether to validate and reuse the parked ablation harness, or build a smaller instrument scoped
   to this question. The harness's own defect history argues for validating whatever is used.
2. What the corpus is. Candidate seed: the session that built the digest violated entry 12 while
   the entry sat unloaded, which is one natural case, not a corpus.
3. What "better" means, stated as a scoring rule before any run. Fewer repeated failures is the
   claim; a proxy that cannot come back negative is not a measurement.
4. Whether the cost is worth it at all. A negative answer here is legitimate and cheap: it would
   mean deleting the branch and leaving the transport in place, which is a smaller loss than
   shipping an unmeasured mechanism.

Non-goals: changing the digest's design before there is a verdict, and re-litigating the retire
decision, which rests on zero executions rather than on the digest's value.

## Verdict

**Do not ship.** The task's own design put Step 0 in front as a kill switch, and it fired: with
no measurable headroom there is nothing for an A/A control or an ablation to resolve, so
Steps 1 and 2 were never run and the 480-run estimate was never spent. Branch
`iamcxa/dev-flow-fresh-failure-digest` is deleted.

This closes the question `improvement-loop-never-ran` was blocked on. That task's retirement
half proceeds on its own evidence as PR #260; nothing replaces the retired transport.

## Step 0 result — no measurable headroom

Ran 2026-08-20. Six probes, authored blind by a separate model from the four raw debrief
records with the digest withheld, each with a deterministic grep check. Baseline only — no
digest, Sonnet 5, isolated fixture directories, standing user configuration loaded.

| Probe | Failure it looks for | Baseline failure rate |
|---|---|---|
| p1 | A change made everywhere except the untested runtime consumer | 0/9 |
| p2 | A duplicate side-effect path left intact behind the obvious fix | 0/9 |
| p3 | An assertion that holds in both worlds and proves nothing | 0/9 |
| p4 | A machine-local absolute path baked into a test | 1/9 |
| p5 | `--paginate` added without combining the per-page arrays | 0/9 |
| p6 | Merged-and-green treated as accepted | 0/9 |

55 runs, 53 pass, 1 fail, 1 no-work. The one failure was a first run that hardcoded the
fixture path; every later run copied the fixture into the repository instead.

The instrument was validated in both directions before any run, which is the step the parked
ablation harness never had: an untouched fixture returns `NOWORK` on all six probes, and a
hand-written correct solution returns `PASS` on all six. Two check defects surfaced during
that validation and were fixed — two probes are reverse-polarity, so a run that did nothing
scored `PASS` until a did-work guard was added; and one did-work guard passed on a word that
appears in the fixture's own type declaration rather than on the behavior it was meant to
detect.

Two of the six probes target failures that are in the debrief records and **absent from the
digest**, which is its own finding: hand-curation of twelve entries is not what an independent
reader extracts from the same four records.

### Why there is no headroom

The disciplines these probes test are already in the agent's standing configuration — the
user-level `CLAUDE.md` carries the sampling-absence rule, the unit-tests-do-not-prove-wiring
rule, root-cause discipline, and trace-the-path. The digest would re-deliver guidance that is
already loaded on every session. That is a specific reason for the null result, not an absence
of one.

### Bound on this result

Six probes, not twelve entries; one model at one effort; one configuration. It does not show
that a recent-failure digest is worthless in general. It shows that **for the failure classes
these four records actually contain, this agent in this configuration already applies the
named check**, so a digest carrying them has nothing left to add.

## Acceptance evidence

A scoring rule fixed before the runs, an A/A control that passes, and a verdict with its runs
preserved. The verdict authorizes delivery or deletion of
`iamcxa/dev-flow-fresh-failure-digest`; it does not authorize a redesign.

## Measurement

Repeated-failure rate on the corpus, digest present versus absent, against the A/A control's noise
floor. A difference smaller than that floor is no difference.
