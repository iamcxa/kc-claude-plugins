---
title: A pre-build story interrogation, replayed on batch 3, asks ahead of time the decisions and P1 gaps that batch 3 actually hit, and shows which model and role mix asks them
variant: kc-dev-flow-2
profile: poc
merge: local
status: validation
gates:
    version: 1
    records:
        - id: gate:interrogation-replay-on-batch-3-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:interrogation-replay-on-batch-3-poc-backlog-1
              briefing:
                id: briefing:interrogation-replay-on-batch-3-poc:backlog:attempt-1:revision-1
                digest: sha256:a5555d361feb6b200d07e23e6376f9a6c371f11ad3e624453d9cd0f43abaa7f6
                room-ref: ./interrogation-replay-on-batch-3-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:interrogation-replay-on-batch-3-poc:backlog:1
                briefing: briefing:interrogation-replay-on-batch-3-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-20T08:18:08.275168Z"
                decision: approve
                reason: 'Captain approved in chat (「准」) after the gate briefing: profile poc, the one-task budget and the falsifier as written'
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-20T08:18:17Z
worktree: .worktrees/spacedock-ensign-interrogation-replay-on-batch-3-poc
---

## Scope

- Source: the Captain, 2026-10-20: 「對，雙模型，且等級與角色應該要混合……claude 是否該用特殊角色進來問答？codex 如何確保用的是足夠聰明的模型？codex 是否也可以，或是也該套入特殊角色？我感覺這個階段可以省去批次問答的時間與設計階段的一些問題？有過去的經驗可以挖出來比較的嗎？」; 「特殊角色是 agent profile + skill 所以理論上 codex 可以接 skill」; 「可以開這個 poc」.
- Riskiest assumption: a story interrogation run before a batch starts asks a material share of the questions the batch later stopped on (Captain decisions surfaced at ideation, and P1 or roborev High findings that were design gaps), so moving it earlier saves Captain sittings and repair cycles. Evidence today: two runs on one release (kc-journey-map `references/interrogation.md`: Codex asked 12 of 17 later-hit questions, Claude sonnet 4 of 17; both missed three concurrency issues).
- Decision this POC informs: the interrogation design inside new-work-starts-from-a-story-map (dev2 workflow), and which model and role each interrogator uses.
- Method: kc-journey-map's interrogation prompt and isolation rules, run on the code snapshot each batch-3 task started from (`git archive <base>`; no history), against that task's seed Scope as the "story". Arms, same prompt: (1) Claude sonnet, default effort (today's interrogation); (2) Claude Opus with the kc-dev-flow-2:engineering-reviewer skill's lens; (3) Codex at an explicitly pinned model and high effort; (4) the same Codex with the kc-dev-flow-2:engineering-reviewer skill. Answer key, read from the archived tasks only after the arms ran: every Captain decision (D-items, amendments) and every P1 or roborev High that was a design gap.
- Falsifier: across the arms, fewer than 25% of the answer key items are asked in substance by any arm; or the best arm's hits come with more than three ungrounded questions per hit.
- Budget: start with one task (captain-question-load: two D-items, one amendment, two P1s and a roborev High); report cost and hits; extend to the other batch-3 tasks only on the Captain's word. Stop point: the one-task report, or the falsifier firing.
- Non-goals: changing kc-journey-map or kc-dev-flow-2; picking a production design.

## FO alignment

Alignment: not needed before implementation; the Captain asked for this POC and the one-task budget is stated.

## Stage Report: implementation

- DONE: Run the four interrogator arms in the task Scope on captain-question-load only: snapshot the kc-claude-plugins code at that task's base (find it in the archived task under the dev2 state checkout, _archive/captain-question-load.md and its dispatch records; base 18dbf490) with `git archive <base> | tar -x`, no history; use kc-journey-map's interrogation prompt (kc-journey-map/skills/kc-journey-map/references/interrogation.md at origin/main) with the task's seed Scope (its first committed version) as the story; arm 2 and arm 4 add the kc-dev-flow-2:engineering-reviewer skill's lens to the same prompt; pin Codex's model and effort explicitly with flags you first confirm in `codex exec --help`; audit each event stream for reads outside the snapshot
  All four arms ran to exit 0 (71, 208, 166, 213 s). Snapshot is 18dbf490, 1377 files; seed is state commit 41654262. Claude: `--model sonnet` / `--model opus --effort high`; Codex: `-m gpt-6.1-sol -c model_reasoning_effort="high"` (`-m` confirmed in `--help`; effort has no flag there, so it goes through the documented `-c` override and its application is unverified). Audit: 0 reads outside the snapshot in 18, 23, 27 and 23 calls; the reference Claude command exposed MCP tools, so I added `--strict-mcp-config` (tool list became Glob, Grep, Read).
- DONE: Only after all arms ran, build the answer key from the archived task (its Captain decisions D1, D2, amendments 1 and 2, the Codex P1s and the roborev High that were design gaps) and score each arm: key items asked in substance (quote the question and the key item), ungrounded questions, cost (tokens or reported cost per run, stated as measured or not), wall time; check the falsifier
  Key read after the answers were saved: 7 items K1 to K7. Strict hits 1, 1, 2, 4 of 7 (arm 1 to 4); ungrounded questions 0 of 90 by a mechanical symbol/quote check plus 4 spot checks. Cost: Claude imputed list price 0.291 and 1.920 USD, Codex tokens only (USD not measured). Falsifier not fired (union 57%, best arm 57%; 0 ungrounded per hit). One task, n=1 per arm, one rater.
- DONE: A report saved as interrogation-replay-on-batch-3-poc/report.md in the dev2-poc state checkout, with the four arms' raw question lists, the scoring table and a recommendation for which arm or mix to use, and whether to extend to the other batch-3 tasks
  `interrogation-replay-on-batch-3-poc/report.md` (raw lists, scoring table, quotes, recommendation: arm 4 as primary, extension to the other batch-3 tasks only on the Captain's word with arm 3 as noise control); full answers, both prompts and `run.sh` in `interrogation-replay-on-batch-3-poc/raw/`.

### Summary

The falsifier did not fire: Codex with the engineering-reviewer lens asked 4 of 7 key items, the others 1, 1 and 2; K5 (a hold opt-out) was asked by none. Limits: one task, one run per arm, my own key and scoring, and an 11-item partial column that I did not use for the falsifier. No repository file, branch, commit or PR was created; the temp directory `/tmp/replay-w0OHE1` is left for validation and the removal command is in the report. `comment_ratio.py HEAD HEAD`: exit 0, 0 code lines, 0 comment lines, 0.0% (no diff, base ad44f0cb = HEAD). `number_guards.py check`: exit 0, PASS no findings, migration guard skipped (no migrations-path).
