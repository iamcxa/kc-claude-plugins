---
title: The journey-map interrogation's Codex stranger on the user's default model (gpt-6-astra, high, engineering-reviewer lens) asks the key questions as well as the pinned gpt-6.1-sol
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:interrogation-astra-vs-sol-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:interrogation-astra-vs-sol-poc-backlog-1
              briefing:
                id: briefing:interrogation-astra-vs-sol-poc:backlog:attempt-1:revision-1
                digest: sha256:6ef8383f7f43b26c086a10d0d0bda0dba892691226ca3300cff070f466ac740b
                room-ref: ./interrogation-astra-vs-sol-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:interrogation-astra-vs-sol-poc:backlog:1
                briefing: briefing:interrogation-astra-vs-sol-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T18:39:58.881816Z"
                decision: approve
                reason: Captain 「可以但我還是不太確定，你說的是故事地圖套件的qa問答部分嗎？」 (chat, 2026-10-22), answering FO question put before it (quoted in the gate question); FO then confirmed it is the kc-journey-map interrogate mode. This briefing binds that answer after the fact.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-21T18:40:25Z
worktree: .worktrees/spacedock-ensign-interrogation-astra-vs-sol-poc
---

## Scope

- Source: the Captain, 2026-10-22, on new-work-starts-from-a-story-map D4 (which interrogators a release preparation runs): 「我在想是否應該預設跑 astra、high、套 ER 觀點？」, then 「可以」 to FO's proposal to rerun the closed POC's five tasks with astra before deciding.
- What exists: dev2-poc task interrogation-replay-on-batch-3-poc (archived, passed) ran Codex `gpt-6.1-sol` at high effort with and without the engineering-reviewer lens over five batch-3 tasks, with answer keys, blind files and scores (`blind/scores.md`, `answer-keys.md`, `raw/run-ext.sh`); the lens arm hit 6 of 13 tier-1 items strict. `gpt-6-astra`, the user's Codex default in `~/.codex/config.toml`, was never compared.
- The run: one arm, `codex exec -m gpt-6-astra -c model_reasoning_effort="high"` with the lens prompt, on the same five snapshots and prompts, isolation and blinding as that POC; scored against the same answer keys by a scorer blind to the arm.
- Bar: report astra's tier-1 strict hits beside sol lens (6/13) and sol plain (5/13), ungrounded questions, and tokens and wall time per run; a difference within one item is read as no difference.
- Budget: one arm, five runs, one scoring pass; stop there.
- Non-goals: Claude arms; changing kc-journey-map.

## Acceptance criteria

**AC-1** The astra arm ran on the five snapshots with the pinned flags. Evidence: the five rollouts each carry `"model":"gpt-6-astra"` and `"effort":"high"`. Falsifier: a rollout on another model or effort.

**AC-2** Scores are blind and comparable. Evidence: a scorer that does not know the arm scores astra against the closed POC's answer keys with its rubric; the report tables astra beside sol lens and sol plain. Falsifier: a score assigned with the arm known.

## FO alignment

Not needed before implementation. The Captain asked for this run (「可以」, 2026-10-22) after FO stated its arm, tasks and comparison, restated above. Release review: not needed: the task belongs to no release.
Surfaces: none
Visible change: none

## Stage Report: implementation

- DONE: Run one arm, `codex exec --sandbox read-only --skip-git-repo-check --cd <snap> --json -m gpt-6-astra -c model_reasoning_effort='"high"' -o <answer> -` with the lens prompt, on the same five task snapshots and prompts the closed POC used (its raw/run-ext.sh and extension.md), with the same isolation; save each answer and event stream under the task folder; confirm each rollout carries "model":"gpt-6-astra" and "effort":"high" (AC-1)
  Five runs, exit 0 each, saved in `interrogation-astra-vs-sol-poc/raw/<task>/`. Rollouts for all five hold only `"model":"gpt-6-astra"` and `"effort":"high"`; prompts differ from the closed POC's arm 4 only in snapshot path (diff, 5/5); isolation audit over 82 commands found 0 outside-snapshot paths, `..`, `~`, or `git` commands. Details in `report.md`.
- DONE: Write the five answers as blind files under the task folder (no arm or model name in a file name or body) for a separate blind scorer, and a short report.md with tokens, wall time and commands per run beside the closed POC's arm-3 and arm-4 totals; do not score the answers yourself
  `blind/<task>-Z.md` x5 plus `blind/READER.md`; grep for astra/gpt/codex in blind/ finds nothing. `report.md` tables astra 3,703,502 in / 30,404 out / 82 commands / 1,070 s summed beside arm 3 (3,204,452 / 33,847 / 68 / 957) and arm 4 (3,647,778 / 38,714 / 86 / 1,149). No answer was read against the keys.

### Summary

The astra arm ran on the five closed-POC snapshots with the arm-4 lens prompt and pinned flags; all pins verified from the rollouts. Answers are in `blind/` for a blind scorer (AC-2 is the scorer's step, not done here). Snapshots were deleted after the runs; no code was changed (roborev not run: no repository diff).
