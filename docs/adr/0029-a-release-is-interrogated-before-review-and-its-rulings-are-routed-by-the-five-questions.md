# 0029. A release is interrogated before it is reviewed, and a ruling made before its tasks exist is routed by the five questions

Date: 2026-10-22

## Status

Accepted

## Context

One adopter's release ran `review-release` first, and its task split rested on answers to which the interrogation then added nine open questions (the task's release-preparation intake, 2026-10-21). kc-journey-map's `interrogation.md` ran a Claude and a Codex worker and sent every decision to "the project's decision record", which in a kc-dev-flow-2 repository has no number route before a task exists. kc-adr's `read-adr` (`Where new information goes`) already ranks where a ruling lives: the task file, the story map, an instruction file, or an ADR. Two POCs on five task snapshots found `gpt-6-astra` with the reviewer lens, `gpt-6.1-sol` with it and sol plain within one of 13 key items of each other (6, 6, 5).

## Decision

**Words:** 「可以，照 kc-adr 那套 5 問規則」 (D1), 「就不做」 (D2), 「那就保留 sol，因為 astra 比較貴」 (D4) — Captain, 2026-10-22, chat, batch-5 sitting; 「可以」 at the ideation gate of `new-work-starts-from-a-story-map`, 2026-10-22, accepting D5 option (a) as recommended.

**Options considered:**
- `review-release` interrogates the release first, ranks the decisions only the Captain can settle and asks them one at a time, then walks and splits (chosen); walking first, as that adopter did, was not chosen
- A ruling made before any task exists is the map question's `answer:` and `source: {kind: release, ref: "<journey>/<release-id>", words, date}`, a `journey-map-question` MINOR 1.0.0 to 1.1.0 (chosen, D1); keeping it in the review record was not chosen
- A ruling that later work must respect becomes an ADR linked from the question (chosen, D1); the first task filed on that story drafts it from `source.words`, its number is reserved at that task's implementation dispatch, and its pull request replaces `answer:` with `doc:` (chosen, D5 option a); a reservation held by the review record (D5 option b) was not chosen
- One Codex stranger, `gpt-6.1-sol`, high effort, with the engineering-reviewer lens, plus a plain run where a decision is hard to reverse, and no Claude run (chosen, D4); Codex plus a Claude sonnet run was not chosen
- No seed hold on the `Release review:` line, only a question at the `dev` entry (chosen, D2); a seed check that holds a task without the line was not chosen

**Recommended:** D1 the review record, D2 a seed hold, D4 Codex plus a Claude sonnet run, and D5 option (a). The Captain chose differently on D1, D2 and D4.

A release is interrogated and its decisions are asked before it is walked or split, and the order is kept by `journey-review.mjs check`. A pre-task ruling has one home by kc-adr's five questions: the map question for this slice or one task he settles now, an ADR for a ruling later work must respect, and nothing in the review record. Later work that prepares a release follows this order and routing.

## Consequences

Until the task that lands an `ADR owed` ruling merges, the ruling's only home is the map, so an ADR-title reader does not list it; no script checks that the later `answer:` to `doc:` swap happened. Reopen when a release's first task ships without the swap, or when a prepared release's ruling is found in neither the map nor an ADR. Release preparation needs `codex`; a session without it stops with `interrogation not run: <reason>`. The cap of 10 asked per sitting and the tie to Codex model names are unmeasured and edited by hand.
