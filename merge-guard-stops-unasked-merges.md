---
title: A gh pr merge that no task's saved merge ask carries is stopped for the Captain, on Claude and on Codex
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:merge-guard-stops-unasked-merges:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-guard-stops-unasked-merges-backlog-1
              briefing:
                id: briefing:merge-guard-stops-unasked-merges:backlog:attempt-1:revision-1
                digest: sha256:2efdd5c216871bf4e2d6790a5df495093f1e61803f3f789039b79a219fc110fc
                room-ref: ./merge-guard-stops-unasked-merges/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-guard-stops-unasked-merges:backlog:1
                briefing: briefing:merge-guard-stops-unasked-merges:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-05T17:17:58.121514Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-06), answering 「決定：「合併前擋下沒人問過的合併」這張用 Pilot，照任務寫下的範圍、預算與停止條件進入構想嗎？核准即接受：構想階段先在隔離的 Claude 和 Codex 環境證明兩邊都擋得住（不動你自己的設定），如果某一邊只能用 deny 擋，那條路線另外問你。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain's 「好」 to question 13 of the batch-4 sitting (2026-10-20), on FO's recommendation 「我建議開這張任務，範圍是兩邊都做，第一步先做 POC。」; recorded as Amendment 3 of fo-write-rules-checked (D7).
- Bite: Release PR iamcxa/kc-claude-plugins#672 merged 2026-10-20T03:07:06Z on a delivery question that did not name it (observer report of special-role-calls-fire-when-needed). No state records a Release PR merge, so no task-reading check reaches it.
- Facts read 2026-10-20: Claude Code user settings run `defaultMode` auto with no ask or deny rule and no allow rule naming `gh pr merge`; Codex CLI 0.162.1 lists `hooks` as stable (`codex features list`), and `~/.codex/rules/default.rules` holds `prefix_rule(pattern=["gh", "pr", "merge"], decision="allow")`.
- First step, a POC before any design: prove on each host that a pre-tool hook (Claude `PreToolUse`, Codex `pre_tool_use`) or a Codex prefix rule actually stops a `gh pr merge` for the Captain under the mode he runs (auto on Claude). If an `ask` does not prompt, the route is `deny`, a new question for him.
- Guard shape to test (from fo-write-rules-checked `### Deferred to the D7 guard task`): allow a merge only when a task's newest `merge/ask-N.json` carries that PR and its saved `head` equals the `--match-head-commit` value (kc-dev-flow-2 0.26.0 already saves both), otherwise ask. It must not defer to a permission prompt.
- Upstream first: ADR 0003 (an adopter-owned hook, not package-shipped); Spacedock merge guard; the deferred `Merges:` line design and both engineering-reviewer reads in fo-write-rules-checked/reviews/.
- Non-goals: changing the Captain's own Claude or Codex settings without his word; the `Merges:` line itself unless the POC shows the guard needs it.

- Added 2026-11-06: the facts above are from 2026-10-20; the worker re-reads both hosts' current hook and rule behavior before relying on them. The proof runs in isolated Claude and Codex state (a throwaway HOME), never in the Captain's own settings.
- Batch 15: the Captain 「可以」 (chat, 2026-11-06), answering 「第 15 批做這 2 張，可以嗎？其他 4 張要退休或擱置，我下一題再問你。」, which named this task.

## Budget
- Ideation carries the proof on both hosts; implementation is one package PR, or none if the proof shows the guard belongs outside the package (ADR 0003). The workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- On each host, in isolated state under the mode the Captain runs, a `gh pr merge` that no task's newest `merge/ask-N.json` carries (PR and `--match-head-commit` head) is stopped before it runs and a matching one proceeds; or the design names the host that cannot stop it and the route it needs from the Captain.

## FO alignment

Alignment: needed before ideation; the POC result decides between an ask route and a deny route, and a deny route is his call.
Surfaces: none
Visible change: none
Outside this repository's surfaces: the Captain's Claude Code and Codex user-level hook or rule files on each machine.
Release review: not needed: workflow maintenance, on no journey map.
