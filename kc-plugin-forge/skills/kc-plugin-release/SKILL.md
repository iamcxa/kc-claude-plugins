---
name: kc-plugin-release
description: Use when maintaining a kc-claude-plugins feature or release pull request, waiting for its GitHub checks, or synchronizing a released plugin into local Claude Code and Codex installs.
---

# KC Plugin Release

Keep the release handoff narrow and reproducible. In `kc-claude-plugins`,
release-please owns version propagation, tags, changelogs, and marketplace
metadata through `release-please-config.json`, `.release-please-manifest.json`,
and `.github/workflows/release-please.yml`. This skill has no release-mutation
authority.

Resolve `PLUGIN_ROOT` to the directory two levels above this `SKILL.md`.
Claude Code may expose that directory as `${CLAUDE_PLUGIN_ROOT}`; Codex should
use the installed plugin root containing this skill. Do not assume a path under
the user's home directory.

## Feature and release PR checks

For a feature PR or the release-please PR, use the packaged exact-head watcher:

```bash
bash "$PLUGIN_ROOT/scripts/watch-pr-checks.sh" <pr-number> --repo iamcxa/kc-claude-plugins
```

The watcher uses the authenticated `gh` CLI directly, propagates failed checks,
and rejects a result if the PR head changes while checks are running. A missing
host-level monitor is not a reason to bypass the gate.

## Post-release local sync

Only after the release PR is merged and the release exists:

1. Use the non-Conductor main workspace for `kc-claude-plugins`.
2. Update `main` and leave it clean. The helper refuses another branch, a dirty
   source, or a local head that differs from `origin/main` when that ref exists.
3. Run:

```bash
bash "$PLUGIN_ROOT/scripts/post-release-sync.sh" <plugin> --repo <main-workspace>
```

The helper copies the released plugin into both
`~/.claude/plugins/local/<plugin>` and
`~/.codex/local-plugins/<plugin>`. It refuses to replace either destination
when that destination is a symlink.

Do not edit release metadata, manufacture a tag, or rewrite marketplace data
in this step. If release metadata is wrong, repair the release-please
configuration in a separate feature PR and let its release PR publish the fix.
