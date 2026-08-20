---
id: ppzm63snegh3119w8ng4fdxk
title: "Measure the vendored pr-merge extension rule by rule, and cut what has no headroom"
status: backlog
source: "Captain, 2026-08-20, after two wrong wholesale reads of the same file: first that 238 lines were a redundant back-port (deleting them failed 13 assertions), then that a passing contract test meant every rule earns its place (it pins prose, not behaviour). First measured results show both readings were too coarse."
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

`docs/dev/_mods/pr-merge.md` carries a 392-line local extension. Nothing has ever measured
whether its rules change agent behaviour. Two guards exist and neither answers that question:

- `scripts/pr-merge-portable-delivery.test.py` verifies that specific phrases, tables, command
  counts, and orderings are still present. It fires — its four self-mutations are rejected — but
  it **pins prose, not function**. It would pass on prose that is wrong, and it caught a
  deletion because deletion is drift, not because it understands delivery.
- Provenance in the tracker shows most rules trace to live concerns (`exact candidate` 16
  records, `required checks` 14, `draft` 36) while `one unit per PR` traces to **zero**. But
  provenance is not usefulness: the retired failure digest had twelve entries with real
  provenance and measured zero headroom, because the standing configuration already covered
  them.

## First measurement — the rules are not uniform

Six independent baseline runs in a fixture carrying this repository's real PR conventions and
**no extension**, with both controls validated first (untouched stub returns `NOWORK` on all
four rules; a hand-written correct script returns `PASS` on all four):

| Rule | Baseline already produces it | Reading |
|---|---|---|
| `--draft` | **6/6** | Dead weight. `CLAUDE.md` already says Draft is the default PR mode. |
| `chmod 600` on the PR body file | **0/6** | Load-bearing. Without it every run left the body in a world-readable temp file. |
| exact candidate SHA recorded | **0/6** | Load-bearing. Without it nothing binds the reviewed revision to the merged one. |
| `gh pr checks --required` | 2/6 | Partial. |

So the file is neither uniformly redundant nor uniformly earned. Wholesale judgments about it
have been wrong twice; the unit of decision is one rule.

## Work profile receipt

## Accepted outcome and non-goals

Every rule in the extension has a measured headroom number, and rules measuring zero are
deleted. `--draft` is already a candidate on the evidence above; `one unit per PR` is the next,
having neither provenance nor a measurement.

Open questions the shape stage owns:

1. **Which rules are probeable.** Some are deterministic and greppable (a flag, a `chmod`, an
   SHA in the body). Others — "one PR binds exactly one approved delivery unit" — describe a
   judgment with no single observable token. Say which are out of scope rather than inventing a
   weak proxy for them.
2. **What a deletion costs.** `pr-merge-portable-delivery.test.py` asserts the presence of
   several of these phrases. Cutting a rule means cutting its assertion in the same change, and
   that assertion is the only thing standing between the file and silent drift. A deletion has
   to say what now prevents the rule from being needed again.
3. **Whether the harness generalizes.** The probe method used here and for the retired digest
   is the same shape. If it is going to be used a third time it should be a tool in the
   repository rather than a temp directory rebuilt each session.

Non-goals: the full refit against canonical 0.27.0 — that is a three-way merge with the local
delivery contract preserved, and is separate. Changing what the extension asserts about rules
that measure non-zero.

## Acceptance evidence

A headroom number per probeable rule, with both controls validated before any run, and every
zero-headroom rule removed together with its assertion. A rule that survives has a number, not
an argument.

## Measurement

Rules with a measured headroom number, out of the extension's probeable set. Currently 4 of an
unknown total.
