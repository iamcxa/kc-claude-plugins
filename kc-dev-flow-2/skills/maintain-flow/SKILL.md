---
name: maintain-flow
description: Maintain the kc-dev-flow-2 static stage skills and profile references, and check declared routing without executing a development workflow.
---

# Maintain flow

Invocation: `kc-dev-flow-2:maintain-flow`

Read the [framework](../../README.md) and the affected skill's routing table.
Put cross-stage profile principles in their one shared reference, stage-common
practices in principles.md, and differences in that stage's profiles directory.
Preserve exact variant namespaces and the POC ideation skip; avoid copying a
shared rule into each profile or adding unused automation scaffolding.

Run `python3 kc-dev-flow-2/scripts/lint-skills.py` from the repository root.
When changing lint behavior, run `python3 kc-dev-flow-2/scripts/test_lint_skills.py`
and add a mutation only for a material failure the check is meant to catch.
Use an available Agent Skills specification validator for broader authoring
format checks; the bundled CLI reuses the repository's basic frontmatter check
and validates declared routing structure, not the full standard or agent behavior.

Report the exact changed files, static results and untested behavioral claims.
Do not infer permission to register/install the bundle, execute SD stages,
install hooks, launch experiments, post externally or commit from a lint pass.
