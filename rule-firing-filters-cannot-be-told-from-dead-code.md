---
id: j6hgvgsnmw16k3dr0fb0v5kp
title: "A filter that never runs and a filter that works look identical to this suite"
status: backlog
source: "Found 2026-08-25 while verifying main after PRs #285, #286 and #290 merged. Running the pre-merge and post-merge scripts over the same window returned byte-identical output on a window holding 57 relay turns, which is what exposed it."
product: kc-team-ops
sprint:
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## Problem

`rule-firing-report.sh` extracts user turns with `select((.isMeta // false) | not)`
before `drop.awk` sees anything. On this machine every parallel-session relay turn
carries `isMeta: true` — 247 of 247 — so the relay filter added in PR #286 and extended
later that day is unreachable here. It drops nothing, and dropping nothing is
indistinguishable from working.

Two independent measurements say so. All 247 relay turns in the local corpus have
`isMeta: true`. And the pre-merge script and the post-merge script, run over the same
window (`--since 2026-08-20`, 237 sessions), both returned 545 human turns and zero
relay leaks — while that window holds 57 relay turns by direct count.

The adopter's report behind issue #288 measured 553 relay turns entering the human
population on their corpus. Both readings can be true: the field is set by the harness,
so the same script has different behaviour on two machines. Nothing in the script, the
suite, or the report says which case a given run is in.

The general defect is larger than the relay filter. Every fixture in
`rule-firing-report.test.sh` is written without `isMeta`, so **no** assertion in that
suite can separate "this filter matched" from "this input never reached the filter".
The relay filter is simply the first case where the difference mattered, and it was
caught by running the real corpus, not by the suite.

## Work profile receipt

## Accepted outcome and non-goals

Two outcomes, and the second is the load-bearing one.

Record the harness divergence where a reader of a run will meet it: a run whose corpus
carries `isMeta` on relay turns is not measuring what a run without it measures, and the
report should say which case it is rather than leaving the operator to infer it.

Give the suite at least one fixture pair that fails when a filter is unreachable — the
same turn with and without `isMeta` — so a future filter cannot pass by never running.

Non-goal: removing the `isMeta` exclusion or the relay filter. The exclusion is correct
for the turns it was written for, and the relay filter is correct on harnesses that do
not set the field. Neither is the defect; the inability to tell them apart is.

Non-goal: rewriting PR #286's merged claims. That is a record correction, not product
work.

## Acceptance evidence

## Measurement
