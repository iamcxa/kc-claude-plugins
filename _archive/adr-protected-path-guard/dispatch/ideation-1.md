Dispatched: from 0701aa8debd45b3fe7eab7e930141319d52f3aa2
Model: sonnet

## Checklist

Design the kc-adr change at main 0701aa8debd45b3fe7eab7e930141319d52f3aa2: (1) the optional template field in `kc-adr/references/adr-template.md` that lists the files an ADR protects (name, format, where it sits; it must not break `adr_lint.py` on ADRs without it); (2) the exact pointer format a site carries (`see docs/adr/NNNN-…md`, comment syntax per language or language-neutral) and how the linter finds it; (3) the `writing.md` text for the writer; (4) the two linter checks: a listed file exists and carries a pointer to that ADR, and no file points at an ADR whose Status is `Superseded by NNNN`. Show exact text and the check's algorithm.
Check the sibling adopters for an existing ADR-to-code mapping before designing: the repositories under /Users/kent/conductor/repos and /Users/kent/conductor/workspaces named carlove* and subspace-relay* (grep their docs/adr and scripts); say what you checked and found.
Give AC-1..AC-3 reproducible evidence clauses (AC-3's agent run: one per host in a fictional repo; say which harness you reuse, e.g. dev2-poc `_archive/adr-code-pointer-poc/harness/` on branch spacedock-state/dev2-poc) and list decisions for the Captain (field name, pointer format, how pointers are found). Note how this interacts with dev2 task `kc-adr-tools-with-dev2-copy` (dev2's byte-identical copy of `adr_lint.py`). Run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/design_surfaces.py check <task>`. Write no repository file, branch or commit.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's state file and folder).
Fictional data only for any agent-run design; nothing from a private decision repository.
