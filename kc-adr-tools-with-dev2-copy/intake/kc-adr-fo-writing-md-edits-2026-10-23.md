# writing.md edits agreed with the kc-adr FO, 2026-10-23 (peer text, for the implementation PR under D4)

From Paseo agent 1bcf070c: make the change in this task's implementation PR; no separate kc-adr PR. Checked against origin/main fd630b2a: kc-dev-flow-2 keeps references/adr-template.md and scripts/adr_lint.py at the same relative paths, so the tool paths resolve in the copy; only names and the pinned version are false there. Three lines in kc-adr/skills/read-adr/writing.md `## Where the tools are`, each to be true in both packages:
1. Rename the placeholder `<kc-adr>` to `<plugin>` in the folder line and the two tool lines: "This plugin ships the ADR template and the ADR linter. `<plugin>` is the plugin that holds this skill: the folder two levels above this file's folder, the one that holds `skills/`; take it from the path you read this file at, not from a search."
2. Delete the last paragraph ("The reserver's path is written against kc-dev-flow-2 0.28.0. ... report "written against 0.28.0, found X"") rather than reword it; a missing reserver fails on a missing file.
3. Cut the `${CLAUDE_PLUGIN_ROOT}` parenthetical to: "Resolve `<package>` (needed only for the reserver) in this order, never as a literal path:".
After the edit, a grep of `<kc-adr>` in writing.md and SKILL.md returns nothing.
