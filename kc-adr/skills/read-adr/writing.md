# Writing an ADR

For an agent that has reached home 5 in `SKILL.md`.

1. Only a person's ruling is an ADR, in the person's own words (the `**Words:**` line). No words, no ADR: ask the coordinator.
2. The number is the one the task reserved (`ADR: NNNN` in its `## Number guards` section), or, in a repo whose tasks reserve none, the one `## Where the tools are` gives. Invent none otherwise; ask the coordinator.
3. Write one file `docs/adr/NNNN-short-title.md` in the format of the ADR template.
4. Check it with the ADR linter, requiring that number. Report a non-zero exit; do not work around it.
5. In a repo that runs kc-dev-flow-2 the coordinator reserves numbers with the number reserver. You do not run it.

## Where the tools are

This plugin ships the ADR template and the ADR linter. `<kc-adr>` is the folder two levels above this file's folder, the one that holds `skills/`; take it from the path you read this file at, not from a search.

- ADR template: `<kc-adr>/references/adr-template.md`
- ADR linter: `python3 <kc-adr>/scripts/adr_lint.py docs/adr --require NNNN`
- Number reserver, only in a repo that runs kc-dev-flow-2: `python3 <package>/scripts/number_guards.py reserve --kind adr --task <task>`

Numbering: where no number was reserved for you, one writer at a time adds an ADR, and its number is one above the highest on the base branch; under kc-dev-flow-2, use `number_guards.py reserve` instead.

Resolve `<package>` (needed only for the reserver) in this order, never as a literal path (`${CLAUDE_PLUGIN_ROOT}` is this plugin's root, not kc-dev-flow-2's):

1. The `Package root:` line in your dispatch notes or in the loaded kc-dev-flow-2 skill header.
2. The installed copy: on Claude Code the `installPath` of `kc-dev-flow-2@kc-claude-plugins` in `~/.claude/plugins/installed_plugins.json`; on Codex the version directory under `~/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/`.
3. Neither: there is no reserver; number as above.

The reserver's path is written against kc-dev-flow-2 0.28.0. Read `version` in `<package>/.claude-plugin/plugin.json`; if it differs, still use the file and report "written against 0.28.0, found X".
