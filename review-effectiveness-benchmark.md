---
title: Review quality has no numerator — nothing measures findings, false positives, or per-review time
status: backlog
source: cross-model sprint review 2026-07-27, which found the highest-value work for the four stated goals was both unscheduled and unfiled
design:
id: 623pj0g8rjk7qehz8jk8a90m
---

The captain's goals for this kit are: find more real defects and fewer false ones, spend fewer
tokens per review, take less wall-clock per review, and be more agent-native. Three of those four
are ratios or rates over a review. **None of them can be computed today.**

`docs/dev/ledger.csv` records `dispatches, rework_rounds, wallclock_hours, tokens_if_known,
diff_coverage, escaped_defects_7d` — all per *task*, i.e. per unit of development work. Nothing
records, per *review*: how many findings it produced, how many survived adjudication, how many
were false positives, how long the review itself took, or what it cost. So "the review kit got
better" is currently an unfalsifiable claim, and every optimisation to it is argued rather than
measured.

`benchmark-full-rerun-control` (qe) covers half of one goal — it builds a trustworthy **denominator**
for token claims, and its own body says it "should land before any work that claims a token win".
This entity is the **numerator**: without it, a token reduction and a quality regression are
indistinguishable from a token reduction alone.

Two measurements already in hand show why arguing does not substitute. `qh` shipped at 6
dispatches / ~1M tokens and moved a CI job from 512–598s to 488s — real, but a CI number, not a
review number, and nobody can say whether any review got faster. The cross-model reviewer put the
kit's own cost at roughly 140K tokens for the minimum tier (3 agents), ~200K for Standard (5),
~240K for Full, plus ~35K pre-scan and 50–80K for the optional Codex pass, which means fan-out
dominates and the 1193-line pattern corpus `learned-pattern-selection` targets is second-order.
Both facts change what is worth doing, and both were invisible until someone went looking.

## The hard part, and why this is not a trivial slice

Measuring recall needs ground truth: which defects a PR *actually* contained. Three candidate
sources, none free, and ideation must pick before anything is built:

- **Historical PRs with known outcomes** — a defect later fixed, reverted, or filed as an incident
  is ground truth after the fact. Cheap to collect, but biased toward defects that escaped, which
  is the opposite of what a review is graded on.
- **Injected defects** — reproducible and precise, but measures detection of *synthetic* faults,
  and this repo has already recorded that mutation evidence proves coupling rather than target
  selection.
- **Adjudicated panels** — a human or a fresh model decides per finding. Highest fidelity, and the
  most expensive; it also risks grading the kit against the same class of judge that produced the
  findings.

A fourth issue is corpus stability: `corpus-fixture-for-reproducible-acs` (24) records the same
failure on the e2e side, where measured ACs referenced 3286 absolute paths under one machine's
home directory and therefore could not be reproduced by anyone else or by CI.

## Scope

A paired benchmark that runs the current kit and one alternative configuration over the **same**
PR corpus, and reports per review: findings emitted, findings surviving adjudication, false
positives, tokens, and wall-clock. The alternative is a parameter, not a commitment — the first
useful comparison is probably Standard tier against a leaner path, since the cross-model review
argued the dominant cost is fan-out rather than context size.

Explicitly **not** in scope: deciding what the leaner path should be. This entity produces the
instrument, not the verdict.

**AC-1 — One PR corpus, two configurations, one table.**
Verified by: a committed result table naming the corpus, both configurations, and per-review findings / adjudicated-true / false-positive / token / wall-clock figures, reproducible by a second person from the repo alone. Falsified by: numbers that cannot be regenerated, or a corpus that lives outside the repo.

**AC-2 — The adjudication rule is written down before the runs, not after.**
Verified by: the ground-truth source and the adjudication procedure committed ahead of the first measured run, with the count of findings whose verdict was ambiguous reported rather than silently resolved. Falsified by: a rubric authored or amended after seeing results.
