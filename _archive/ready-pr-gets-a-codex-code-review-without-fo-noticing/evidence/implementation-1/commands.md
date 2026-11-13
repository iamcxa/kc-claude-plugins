# Candidate evidence

Candidate: `1c8a29faf402ef6d7018c298f59bad58d38cfb1d`; base: `6a1eaf837bd6087cd0b8b665dc19beaed3c44dff`. All commands ran in the assigned worktree with `PYTHONDONTWRITEBYTECODE=1`; Python commands used `-B`.

- AC-5: `git show HEAD:kc-dev-flow-2/extensions/codex/EXTENSION.md | rg -n -F -- 'when FO marks a PR ready, it comments `@codex review` on the PR once.'` — exit 0, `ac5-candidate.log`.
- Mutation: Python removed the complete added line in a scratch copy with an empty `PYTHONPYCACHEPREFIX`; `rg -n -F` for the same sentence on that copy exited 1 as expected, `falsifier-candidate.log`. No behavior test or retained test was added.
- `python3 -B kc-dev-flow-2/scripts/lint-skills.py` — exit 0, `lint.log`. It ran on the candidate bytes before commit; the post-commit diff against HEAD was empty.
- `python3 -B <package>/scripts/adr_lint.py docs/adr --since 6a1eaf837bd6087cd0b8b665dc19beaed3c44dff` — exit 0, `adr-lint.log`.
- `python3 -B <package>/scripts/number_guards.py check --workflow-dir <workflow> --task <task>` — exit 0 twice: first fetch warning `number-guards-candidate.log`, then refreshed state `number-guards-fresh.log`.
- `python3 -B <package>/scripts/comment_ratio.py 6a1eaf837bd6087cd0b8b665dc19beaed3c44dff HEAD --workflow-dir <workflow>` — exit 0, `comment-ratio.log`.
- `python3 -B <package>/scripts/doc_impact.py 6a1eaf837bd6087cd0b8b665dc19beaed3c44dff 1c8a29faf402ef6d7018c298f59bad58d38cfb1d` — exit 0, `doc-impact.log`; no listed documents.
- `python3 -B <package>/scripts/design_surfaces.py check <task>` — exit 0, `design-check.log`.

`<package>` is the dispatch's installed package root, `<workflow>` is the dispatch's workflow directory and `<task>` the state entity file. Extension whitespace word count before/after: 325 / 343; lint's exact budget applies to workflow.md, unchanged at 6099 / 6099.
