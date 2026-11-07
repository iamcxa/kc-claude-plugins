# Rule-reading replay, 2026-11-06

Prompts: `observer-replay-base.prompt.md` (step 5 at origin/main 0.35.0) and
`observer-replay-candidate.prompt.md` (step 5 from `candidate.py`). Records A-C are the three
batch 12/13 decline lines verbatim from their validation briefing-1; D is a constructed decline
with a bite (the observed failure behind archived followup-dispatch-records-checked).
Each arm: one fresh Sonnet general-purpose agent, told to use no tools; prompts identical but for the rule.

| Record | base (1 run) | candidate run 1 | candidate run 2 |
| --- | --- | --- | --- |
| A fo-tries-what-it-asks-the-captain | violation ("files it as a new backlog task") | ok | ok |
| B model-roster-question-needs-both-families | violation | ok | ok |
| C rewritten-criteria-checked-against-captain-words | violation | ok | ok |
| D bite, no task | violation (also asks whether it was Material) | violation ("Only an observed failure naming who it hurts ... makes it a backlog task") | violation (same quote) |
