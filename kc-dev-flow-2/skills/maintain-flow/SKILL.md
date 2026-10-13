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

Run `python3 kc-dev-flow-2/scripts/lint-skills.py` from the repository root. Before each push
of a package change, run `python3 kc-dev-flow-2/extensions/roborev/roborev_gate.py --repo
<worktree> --base <merge base>` and fix what it reports inside the change: a maintainer
change is not dispatched through FO, so no implementation stage runs it.
When changing lint behavior, run `python3 kc-dev-flow-2/scripts/test_lint_skills.py`
and add a mutation only for a material failure the check is meant to catch.
Use an available Agent Skills specification validator for broader authoring
format checks; the bundled CLI reuses the repository's basic frontmatter check
and validates declared routing structure and package script paths, not the full
standard or agent behavior.

An optional tool joins as an extension: a folder `kc-dev-flow-2/extensions/<name>/` holding
its scripts, their tests and an `EXTENSION.md` in the shape of the existing ones. The workflow
mentions extensions only in its `## Extensions` section and the README's `extensions:` list,
so a repository that lists none is unchanged.

## Behaviour replay

A change that claims a worker will act differently is shown before release, because
wording tests prove only that the text is there. Pick a closed adopter task whose record
holds the old behaviour, and build its dispatch twice with
`python3 kc-dev-flow-2/scripts/replay_dispatch.py build`: once at the last release tag
and once at the change, from the same state and code commits, with a checklist that
names no rule under test. Run each as a fresh worker on the same model, once on the
release and at least twice on the change; `--inject` adds the FO record a rule
depends on, such as a decline. The helper adds the line naming `main` as the completion
recipient to the scope notes; `--no-completion-line` builds the arm without it. Report a table of runs by outcome, then run
`python3 kc-dev-flow-2/scripts/replay_dispatch.py cleanup`. A rule only FO acts on cannot be replayed: a fresh FO
answers scenario questions from the README alone, including one where the rule must not
apply. A replay that contradicts the claim stops the change; after two rewordings that
still fail, take a structural option to the Captain instead of a third.

## Observe adopters

FO grading its own work misses what an outside reader finds, so after each release the
maintainer reads the first task each adopter archives on it. Where the adopter lists
`learn`, that task's `observer.md` is the report; otherwise dispatch
`kc-dev-flow-2:observer` with that adopter's state checkout, the slug and its README.
Before counting a rule as broken twice, read the other tasks' `observer.md` files too;
`python3 kc-dev-flow-2/scripts/decision_ledger.py <state> --summary` adds the counts of
rulings, delegated decisions, overrides and later amendments per area. Find every
reported quote in git before acting on it and retract one that is not there. Send each
confirmed finding to the FO that owns the task, with the quote and the ruling it needs,
and record the ruling it gets. A rule broken in two tasks becomes a package change: a
script check with a mutation test when the rule is objective, otherwise a rewording
shown by Behaviour replay. Read the adopters' workflow sync PRs too: their external
review reads the package text as a reviewer outside the package does.

Report the exact changed files, static results, replay table and untested behavioral claims.
Do not infer permission to register/install the bundle, execute SD stages,
install hooks, launch experiments, post externally or commit from a lint pass.
