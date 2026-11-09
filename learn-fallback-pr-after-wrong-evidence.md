---
title: The learn skill states a bounded hand-PR fallback when a delivery is closed for wrong evidence
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「同意」 (chat, 2026-11-09), answering FO's #811 recommendation: no supersede step now; state a bounded fallback that a hand PR changing only learning.md may follow when a delivery PR is closed for wrong evidence, citing the closed job id and the corrected evidence with its command and date, merge by the Captain; and address why the evidence was wrong.
- Bite: iamcxa/kc-claude-plugins issue #811 (an adopter, 2026-11-08): a completed learn `add` proposal quoted a count from an earlier review pass (18) where a verified recount said 15; `release` was refused ("delivery is open, merged or closed; release refused") and a new evaluation of the same task was refused, so the only route was closing the Draft PR and losing a still-valid Practice.
- Verified 2026-11-09 at origin/main: `job_key` in `kc-dev-flow-2/scripts/learning.py` hashes only the workflow and the task id, so one job per archived task; no package text allows or forbids a hand edit of learning.md.
- Related: backlog task counts-name-the-run-that-produced-them (a count names the command or run that produced it), which would cover learn's evidence counts.
- Non-goals: a supersede command; changing job identity.

## Budget
- One package PR to the learn skill text and its tests; workflow word budget unchanged.

## Stop condition
- The learn skill states when the hand-PR fallback applies and what the PR must cite, and a check or test fails when that text is removed.

## FO alignment

Alignment: not needed; the Captain chose the direction in chat.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
