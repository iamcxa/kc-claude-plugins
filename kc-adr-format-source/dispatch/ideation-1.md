Dispatched: from 8bfac961ddb0167acff2005e256493dfc7942bc5
Model: sonnet

## Checklist

Design kc-adr's side of the narrowed packaging ruling: the exact paths in kc-adr for the ADR template, `scripts/adr_lint.py` and `AdrLintTests`. They are byte-identical to dev2's files at base 8bfac961ddb0167acff2005e256493dfc7942bc5, except the template's "the worker or FO" becomes "the recommender". Show exactly how dev2's copy will be generated from them later, so the dev2 FO's sync script and byte compare can rely on stable paths.
Show the exact `writing.md` change: `## Where the tools are` points at kc-adr's own template and linter, keeps the number reserver under kc-dev-flow-2, and adds the single-writer numbering sentence. Note the risk that the template wording change affects dev2's own lint or tests, and how the AC-2 run will catch it.
Give AC-1..AC-3 reproducible evidence clauses and list decisions for the Captain. Run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/design_surfaces.py check <task>`. Write no repository file, branch or commit.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's state file and folder).
Coordination: the dev2 FO owns task `kc-adr-tools-with-dev2-copy`, which covers the sync script, dev2's copies and the byte compare in scripts/version-parity-check.sh (its amendment 1 records the Captain's narrowed ruling). Do not design or edit dev2 files. Read that task for the agreed split.
Evidence for the ruling: the chief-engineer advice is summarized in this task's body; `scripts/number_guards.py` stays whole in dev2.
