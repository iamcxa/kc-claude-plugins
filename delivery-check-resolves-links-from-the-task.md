---
title: The delivery check resolves a report's relative Markdown links against the task folder, not the shell's current directory
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

`delivery_gate.py question` and `check` read a relative `.md` path named in the gate text or the validation report from the task's own folder, so the result does not depend on where FO runs the command.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering FO's batch 15 retrospective ask 「要為這個路徑解析的缺陷開一張待辦嗎？」.
- Bite: at the batch 15 validation gate of delivery-question-requires-worktree-clause (2026-11-06), `delivery_gate.py question` run from the repository root printed "Captain steps record fails: message S5: unrecorded command or link '/plugin marketplace add iamcxa/kc-claude-plugins'": the report names `validation/README.md`, and the check opened the repository's root README.md instead. Run from the task folder, the same text printed "gate text complete" (FO runs, 2026-11-06).
- Upstream first: `delivery_gate.py` `inspect_steps` (the `markdown` path list and `Path(...)` resolution) and `captain_step_problems`.
- Non-goals: changing which links count as steps.

## Budget
- One package PR; the workflow word budget does not rise.

## Stop condition
- The same gate text and report give the same verdict whether `question` runs from the repository root, the state checkout or the task folder; a replay of the batch 15 case passes from the repository root.

## FO alignment

Alignment: not needed: a resolution bug in an existing check; the rule it applies does not change.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
