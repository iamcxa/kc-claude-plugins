---
title: The journey-map interrogation's Codex stranger on the user's default model (gpt-6-astra, high, engineering-reviewer lens) asks the key questions as well as the pinned gpt-6.1-sol
variant: kc-dev-flow-2
profile: poc
merge: pr
status: backlog
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
