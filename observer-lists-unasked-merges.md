---
title: The observer lists each merge in its window that no task's saved merge ask carries
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

At archive, the observer reports every PR merged in its window whose number and merged head match no saved `merge/ask-N.json` in any state checkout it can read, so an unasked merge is found after the fact without a pre-tool hook.

## Scope

- Source: the Captain 「可以」 (chat, 2026-11-06), answering FO's 「要照這樣做嗎？」, which proposed keeping merge-guard-stops-unasked-merges held and doing first the cheaper after-the-fact check and a look at whether #785 and #727 were asked.
- Bite: fo-feedback round 005 (2026-11-06): journey-map PR #785 merged 2026-11-05 while its task still reads `status: backlog` with no gate decision (FO read of that state file); ops-inbox PR #727 merged 2026-10-27 with the Captain's 「准」 recorded (FO read of its archived gate, 2026-11-06) but with Codex's code review only on an earlier commit. The held merge-guard replay counts (54/30, then 74/10) stay in its task file.
- Upstream first: the merge-guard task's record discovery (state worktrees on `spacedock-state/*`, `*/merge/ask-*.json`); the observer skill; delivery_gate.py's saved ask records.
- Non-goals: blocking any merge; Release, workflow-sync and learning PRs, which carry no task ask (the observer names them as such instead of as violations).

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay over the window that holds #785 lists #785 as merged with no ask record, lists a task PR with a matching record as carried, and names Release and sync PRs separately.

## FO alignment

Alignment: needed at ideation; which state checkouts the observer reads and how a Release PR is named are his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
