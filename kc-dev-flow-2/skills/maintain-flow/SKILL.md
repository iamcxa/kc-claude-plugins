---
name: maintain-flow
description: Maintain the kc-dev-flow-2 static stage skills, profile references and the adopted workflow template (references/sd/workflow.md), keep them from only growing, and check declared routing without executing a development workflow.
---

# Maintain flow

Invocation: `kc-dev-flow-2:maintain-flow`

Read the [framework](../../README.md) and the affected skill's routing table.
Put cross-stage profile principles in their one shared reference, stage-common
practices in principles.md, and differences in that stage's profiles directory.
Preserve exact variant namespaces and the POC ideation skip; avoid copying a
shared rule into each profile or adding unused automation scaffolding.

Every adopter copies `references/sd/workflow.md` as its workflow README, and the
implementation and validation stages inline its `context-sections` into each
dispatch, so its text costs every FO and worker. For each rule added to it,
state in the change: the incident it answers; whether a package script, test or
SD command already enforces it, in which case write one sentence naming that
enforcer instead of restating it; and which existing sentence it replaces, or
that it replaces none. Before adding, look for a sentence to shorten or remove.
Report the file's word count before and after, and the words each worker stage
inlines. `kc-dev-flow-2/scripts/lint-skills.py` refuses a file over its word budget and a passage of
12 or more words that another package file repeats; raising the budget or listing
an overlap is a change that says why.

Run `python3 kc-dev-flow-2/scripts/lint-skills.py` from the repository root.
When changing lint behavior, run `python3 kc-dev-flow-2/scripts/test_lint_skills.py`
and add a mutation only for a material failure the check is meant to catch.
Use an available Agent Skills specification validator for broader authoring
format checks; the bundled CLI reuses the repository's basic frontmatter check
and validates declared routing structure and package script paths, not the full
standard or agent behavior.

Report the exact changed files, static results and untested behavioral claims.
Do not infer permission to register/install the bundle, execute SD stages,
install hooks, launch experiments, post externally or commit from a lint pass.
