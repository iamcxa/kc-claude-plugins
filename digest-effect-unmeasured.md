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
pr:
mod-block:
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

## Acceptance evidence

A scoring rule fixed before the runs, an A/A control that passes, and a verdict with its runs
preserved. The verdict authorizes delivery or deletion of
`iamcxa/dev-flow-fresh-failure-digest`; it does not authorize a redesign.

## Measurement

Repeated-failure rate on the corpus, digest present versus absent, against the A/A control's noise
floor. A difference smaller than that floor is no difference.
