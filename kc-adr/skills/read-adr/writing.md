# Writing an ADR

For an agent that has reached home 5 in `SKILL.md`.

1. Only a person's ruling is an ADR, in the person's own words (the `**Words:**` line). No words, no ADR: ask the coordinator.
2. The number is the one the task reserved (`ADR: NNNN` in its `## Number guards` section). Invent none; no such section means ask the coordinator.
3. Write one file `docs/adr/NNNN-short-title.md` in the format of the ADR template.
4. Check it with the ADR linter, requiring that number. Report a non-zero exit; do not work around it.
5. The coordinator reserves numbers with the number reserver. You do not run it.

## Where the tools are

Today the ADR template, linter and number reserver are files of the kc-dev-flow-2 package, and this skill ships no copy of them:

- ADR template: `<package>/references/adr-template.md`
- ADR linter: `python3 <package>/scripts/adr_lint.py docs/adr --require NNNN`
- Number reserver: `python3 <package>/scripts/number_guards.py reserve --kind adr --task <task>`

Resolve `<package>` in this order, never as a literal path (`${CLAUDE_PLUGIN_ROOT}` is this plugin's root, not kc-dev-flow-2's):

1. The `Package root:` line in your dispatch notes or in the loaded kc-dev-flow-2 skill header.
2. The installed copy: on Claude Code the `installPath` of `kc-dev-flow-2@kc-claude-plugins` in `~/.claude/plugins/installed_plugins.json`; on Codex the version directory under `~/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/`.
3. Neither: stop. A repo without kc-dev-flow-2 has no writing tools.

This paragraph is written against kc-dev-flow-2 0.27.0. Read `version` in `<package>/.claude-plugin/plugin.json`; if it differs, still use the files and report "written against 0.27.0, found X".
