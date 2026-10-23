Control arm (no duty wording) for the replay, run 2026-10-22 on the three tasks the repeat used (39 declines).
Same prompts as ../prompts/ with three edits: the first line no longer points to duty.md; "as the duty wording says" is gone; the closing line gives the output YAML and one clause for each of the three rulings. Everything else is identical, including the two host declaration files and the waiver sentence that treats them as the declaration path.
Run as three fresh general-purpose agents on model sonnet, one per prompt; subagent_tokens 79,158 + 82,942 + 110,257 = 272,357. One run per task. rulings.tsv holds the rulings only; the evidence text was not kept (same as run 2).
Reproduce: copy this folder's prompts to /tmp/dd-control/prompts, and ../ (host/, pics) to /tmp/dd-replay as in ../README.md.
../count_citations.py counts how many of the 31 run-1 overrules cite a declared prop, slot or hook (the figure in the design).
