---
id: 6122k1dp3x9g5wvnyegnhdaz
title: "AC1 asks a keyword search a question only a human read can answer"
status: backlog
source: "Captain ruling 2026-08-25 after a codex adversarial pass. Found while checking whether issue #288 counts as the defect AC1 was written to detect; the search AC1 prescribes returns empty while that issue sits open."
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

AC1 in `kc-rules-review-dogfood-defects` decides whether the skill-defect reporting
slot delivered in PR #290 is worth keeping. It prescribes
`gh issue list --repo iamcxa/kc-claude-plugins --search kc-rules-review --state all`.

Issue #288 is exactly the case AC1 exists to detect — an adopter ran the skill, found
a script defect, and filed it here. The string `kc-rules-review` appears zero times in
that issue's title and body; the reporter named the file that was broken,
`rule-firing-report.sh`. The prescribed search returns empty.

So AC1 reports "no defect ever reached this repository" while the defect sits open.
That reading would retire a working feature, because this entity's own falsifier says
the slot is ceremony if the next adopter-found defect still arrives as a pasted report.

## Work profile receipt

## Accepted outcome and non-goals

Replace AC1's keyword search with a time-window enumeration the operator reads:
list the issues created after the run, and pass only when one of them describes a
kc-rules-review skill or script defect **and** its body carries the skill version and
the local-patch state. The falsifier is unchanged.

Non-goal: adding a provenance marker to the issue body. A codex adversarial pass judged
a marker VIABLE-WITH-CHANGES as an index but not as evidence — "human filing changes
transport, not evidentiary value" — and this repository carries three open issues, so
enumeration costs nothing that an index would save. Revisit only when issue volume
makes enumeration impractical; that is a measurable trigger, not a guess.

Non-goal: changing what the slot itself asks for. What issue #288 supplies beyond the
slot's fields — a measured before/after table and a sampling conclusion — is a separate
question about the slot's format.

## Acceptance evidence

## Measurement
