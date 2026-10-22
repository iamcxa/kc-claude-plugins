---
title: The journey-map interrogation's Codex stranger on the user's default model (gpt-6-astra, high, engineering-reviewer lens) asks the key questions as well as the pinned gpt-6.1-sol
variant: kc-dev-flow-2
profile: poc
merge: pr
status: done
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
        - id: gate:interrogation-astra-vs-sol-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:interrogation-astra-vs-sol-poc-validation-1
              briefing:
                id: briefing:interrogation-astra-vs-sol-poc:validation:attempt-1:revision-1
                digest: sha256:72a8235f541df2315f6ade2d0f5b77ec7199ea18e434af77b693c0f17d4d539b
                room-ref: ./interrogation-astra-vs-sol-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:interrogation-astra-vs-sol-poc:validation:1
                briefing: briefing:interrogation-astra-vs-sol-poc:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-22T00:57:17.702785Z"
                decision: approve
                reason: 'Captain 「結案」 (chat, 2026-10-22), answering FO question put before it (quoted in the gate question). AC-2 is not met as written: the scorer knew the arm because FO named it in the dispatch; the file-opening order and per-score quotes are recorded for a re-score. This briefing binds the answer after the fact.'
              application:
                target-stage: done
                state: consumed
started: 2026-10-21T18:40:25Z
worktree: .worktrees/spacedock-ensign-interrogation-astra-vs-sol-poc
pr: local-merge:061f647f77ea4e18322f31b48666d7b111165ca2
verdict: PASSED
completed: 2026-10-22T01:01:41Z
archived: 2026-10-22T01:01:41Z
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

Correction (FO, 2026-10-22, observer finding): the validation summary's "the Captain kept sol on cost" rests on his words 「按建議**不算**。那就保留 sol，因為 astra 比較貴」 (chat, 2026-10-22), answering FO's report of this POC's result; that ruling is recorded as D4 in dev2 task new-work-starts-from-a-story-map. AC-2 was not met as written because FO's dispatch named the arm and the sol totals; FO's design error, not amended.

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

## Stage Report: validation

- DONE: Score the five blind answers in the task folder's blind/ (files <task>-Z.md, READER.md) against the closed POC's answer keys at .../_archive/interrogation-replay-on-batch-3-poc/answer-keys.md with the same rubric and tier-1 strict rule the closed POC's blind/scores.md used, without opening raw/, report.md, the entity's implementation report, or anything naming the model; record per task and in total the tier-1 strict hits, lenient hits and ungrounded questions
  Scores with quotes in `interrogation-astra-vs-sol-poc/blind/scores-validation-ensign.md`, written before the next item. Tier 1 askable strict, astra: NG 0/2, FW 1/2, CO 2/4, DG 2/2, SR 1/3 = 6 of 13; lenient (strict + partial) 11 of 13 (5 partials: NG1, FW2, CO3, SR1, SR2). Tier 1 late-only 0 of 4. Tier 2 askable 1 of 7 strict (SR8), 3 partial. Ungrounded 0 of 85 (code symbols and paths grepped in git-archive snapshots of the three bases; Story quotes grepped in the key's archived task files).
  Order opened: dispatch file, ensign contract and runtime reference, stage definition, entity lines 1-53 (frontmatter, Scope, Acceptance criteria, FO alignment; the implementation report below it was not read), blind/READER.md, closed POC blind/READER.md, closed POC blind/answer-keys.md, then Z files in the order number-guards, fo-write-checks, chat-only, delivery-gate, special-role, then snapshots and archived task seeds for the ungrounded check; scores file written; only then report.md and the closed POC's blind/scores.md. raw/ was never opened.
- DONE: After scoring, and only then, open report.md and the closed POC's blind/scores.md, table this arm beside sol lens (6 of 13 strict) and sol plain (5 of 13), and give the verdict per the Scope's bar (a difference within one item reads as no difference)
  Verdict: no difference. Astra 6 of 13 equals sol lens (6) and is one above sol plain (5); the bar is one item.

| Tier 1 askable (13 items) | Astra lens (this run) | Sol lens | Sol plain |
|---|---|---|---|
| Strict hits | 6 | 6 | 5 |
| Lenient (strict + partial) | 11 | 11 or 12 | 11 or 12 |
| Ungrounded questions | 0 of 85 | 0 | 0 |
| Questions | 85 | 89 or 91 | 91 or 93 |
| Tokens in / out (5 runs) | 3,703,502 / 30,404 | 3,647,778 / 38,714 | 3,204,452 / 33,847 |
| Wall, summed s | 1,070 | 1,149 | 957 |

  Sol columns: the closed POC's scores.md scored two unlabelled lists, X 5 and Y 6 strict, lenient 11 and 12; the sealed mapping is the task's stated 6 (lens) and 5 (plain), so lenient per arm is read from X and Y without re-mapping here. Tokens and wall from report.md. Per task astra tier-1 strict: NG 0, FW 1, CO 2, DG 2, SR 1, which equals the closed list with 6; the one swap is CO2 (astra) for CO3 (that list).
  Never asked by astra, as by sol: NG2, CO4, SR2 as a threshold, and all four late-only tier-1 items (SR4 to SR7).
- FAILED: AC-2 as written ("a scorer that does not know the arm"; falsifier "a score assigned with the arm known")
  This scorer knew the arm from the dispatch title and knew the sol totals from the checklist before scoring, so AC-2's falsifier literally holds. Kept blind: raw/, report.md, the closed scores.md and the implementation report stayed closed until the scores file was written; every score carries its quote. FO to rule whether that satisfies AC-2.

### Summary

Astra at high effort with the lens scored 6 of 13 tier-1 askable items strict, with 0 ungrounded questions, against 6 for sol lens and 5 for sol plain: no difference by the one-item bar. Scorer variance is about the size of the gap: two calls (DG2, FW1) sit on the hit/partial line and flipping both gives 4, while promoting CO3 and FW2 gives 8. Sample is five tasks, one run per arm, a different scorer from the closed POC, and a second reading of 13 items cannot separate the arms. roborev not run: no repository diff.
