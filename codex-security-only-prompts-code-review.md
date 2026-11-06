---
title: When Codex posts only a security summary, the codex reader names the code-review request as the next step
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

When Codex has posted only its security-review summary on a PR head, codex_review.py (or pr_watch.py) prints a next line that asks FO to request `@codex review`, so a merge ask is not prepared on a head with no code review.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering 「要開這 4 張嗎？」 after fo-feedback round 005 (.notes/fo-feedback/round-005.md, closed 2026-11-06).
- Bite: ops-inbox PR #727 merged 2026-10-27 with Codex's code review only on an earlier commit d7eeeef26 (unresolved findings) and only a security review on the merged head 5dee91fb7 (Codex review-state comment, read by FO 2026-11-06); kc-paseo-plugins lost about 10 minutes per PR on #71 #72 #73 #75 waiting on exit 4 (operator report); Bridge outcome gap 7 (_l3-dogfood/OUTCOME.md, a94f9cd).
- Upstream first: kc-dev-flow-2 extensions/codex codex_review.py (exit 4 "not reviewed") and scripts/pr_watch.py.
- Non-goals: requesting the review automatically (a PR comment stays FO's step).

- Batch 16: the Captain 「可以，就這樣」 (chat, 2026-11-06), answering 「這批做 2、3、4、5、9 這 5 張，可以嗎？」, which named this task.

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay of a security-only head prints the code-review next line; a head with a code review prints none.

## FO alignment

Alignment: needed at ideation; the design choice is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
