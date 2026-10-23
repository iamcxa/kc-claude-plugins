---
title: Every worker dispatch runs at a reasoning effort chosen by rule (highest, high or medium), and the host is shown to honour it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「開，可能特別關注在最高，高，中等這三級」 (chat, 2026-10-23), answering FO's 「要開這張任務嗎？我建議開，而且先做驗證那一步。」 after his 「現在是怎樣決定派 ensign 的推理等級的」.
- What exists (FO read, 2026-10-23): the workflow README `stages.defaults.model: sonnet` sets the model; `spacedock dispatch build --help` (0.27.2) lists no effort or reasoning option; the spacedock ensign agent file (0.27.3) declares no reasoning; FO does not set the Agent tool's effort on dispatch, so ensigns run at the host default, whose value is unverified; kc-dev-flow-2 agent files declare `reasoning: xhigh` (chief-engineer, engineering-reviewer) and `reasoning: high` (observer, design-director), and their text says "If the host ignores the frontmatter field, explicitly request the highest available reasoning level", so whether the host honours the field is also unverified. The model rule (ideation sonnet by default, opus when a decision is hard to reverse) lives in FO practice, not in the package.
- First step, a test before any rule: on the current Claude Code host, read what effort a dispatched subagent actually runs at with and without an agent-file `reasoning:` field and with and without the dispatch's effort setting, and what the default is; the same for a Codex-hosted worker if available.
- Shape asked for: a rule that picks one of three levels, highest, high or medium, per dispatch (by stage, profile, special role or hard-to-reverse decision), carried where the dispatch can set it, and recorded in the dispatch record beside `Model:`.
- Upstream first: Spacedock dispatch build and its model resolution; Claude Code's Agent tool effort parameter and agent-file frontmatter; Codex reasoning effort settings.
- Non-goals: changing which model a stage uses.

## FO alignment

Alignment: needed at ideation; the rule mapping work to the three levels is his.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
