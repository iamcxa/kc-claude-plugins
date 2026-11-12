---
title: Agents in a dev2 workflow write to each other in English, and only words addressed to the Captain follow his language
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「我想改成agent間通訊一律英文，跟我對話才以我的語言為主，要改哪裡？至少dev2內agent對話必須以英文溝通，避免誤解且增進token效率」 (chat, 2026-11-13).
- Bite (FO read 2026-11-13): in the route trial of that day every Codex worker's completion report and every validator question to FO came back in Chinese. `git grep -n -iE 'language|chinese|english'` over `references/sd/workflow.md`, the stage skills and the `paseo` and `peers` extensions on origin/main at 8125e6d51 found no language rule; the workers followed the Captain's global instruction to reply to him in Chinese and treated a completion report as a reply to him.
- Done outside the package the same day, on his approval 「你改，改完給我看差異（建議）」 (host question dialog): one sentence added to each of his two global instruction files. That reaches his machine only.
- Outcome: the package states it where a worker and an FO read it, so an adopter on another machine gets the same rule.
- Open for the design: which file is the one home (workflow template, the dispatch text, or the two messaging extensions); whether task files and stage reports are covered or only messages; whether anything checks it.
- Non-goals: the language FO uses with the Captain; quoted Captain words, which stay as written.
- Unmeasured: the token saving he names; no number is claimed.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- A worker dispatched with the candidate text, on a host whose global instructions say to reply in Chinese, writes its completion report and its questions to FO in English.

## FO alignment

Alignment: not needed before ideation: his words state the outcome; where it lives is compared in the design.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
