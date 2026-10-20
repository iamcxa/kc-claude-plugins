---
title: A pre-build story interrogation, replayed on batch 3, asks ahead of time the decisions and P1 gaps that batch 3 actually hit, and shows which model and role mix asks them
variant: kc-dev-flow-2
profile: poc
merge: local
status: backlog
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
