---
title: A gh pr merge that no task's saved merge ask carries is stopped for the Captain, on Claude and on Codex
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain's 「好」 to question 13 of the batch-4 sitting (2026-10-20), on FO's recommendation 「我建議開這張任務，範圍是兩邊都做，第一步先做 POC。」; recorded as Amendment 3 of fo-write-rules-checked (D7).
- Bite: Release PR iamcxa/kc-claude-plugins#672 merged 2026-10-20T03:07:06Z on a delivery question that did not name it (observer report of special-role-calls-fire-when-needed). No state records a Release PR merge, so no task-reading check reaches it.
- Facts read 2026-10-20: Claude Code user settings run `defaultMode` auto with no ask or deny rule and no allow rule naming `gh pr merge`; Codex CLI 0.162.1 lists `hooks` as stable (`codex features list`), and `~/.codex/rules/default.rules` holds `prefix_rule(pattern=["gh", "pr", "merge"], decision="allow")`.
- First step, a POC before any design: prove on each host that a pre-tool hook (Claude `PreToolUse`, Codex `pre_tool_use`) or a Codex prefix rule actually stops a `gh pr merge` for the Captain under the mode he runs (auto on Claude). If an `ask` does not prompt, the route is `deny`, a new question for him.
- Guard shape to test (from fo-write-rules-checked `### Deferred to the D7 guard task`): allow a merge only when a task's newest `merge/ask-N.json` carries that PR and its saved `head` equals the `--match-head-commit` value (kc-dev-flow-2 0.26.0 already saves both), otherwise ask. It must not defer to a permission prompt.
- Upstream first: ADR 0003 (an adopter-owned hook, not package-shipped); Spacedock merge guard; the deferred `Merges:` line design and both engineering-reviewer reads in fo-write-rules-checked/reviews/.
- Non-goals: changing the Captain's own Claude or Codex settings without his word; the `Merges:` line itself unless the POC shows the guard needs it.

## FO alignment

Alignment: needed before ideation; the POC result decides between an ask route and a deny route, and a deny route is his call.
Surfaces: none
Visible change: none
Outside this repository's surfaces: the Captain's Claude Code and Codex user-level hook or rule files on each machine.
