# kc-claude-plugins

Public marketplace repo containing six plugins: `e2e-pipeline`, `kc-plugin-forge`, `kc-nightwatch`, `kc-hyperfocus`, `kc-team-ops`, `kc-pr-flow`. Each plugin keeps its own `CLAUDE.md` for plugin-internal conventions. This file documents **repo-wide rules** that apply to PRs touching any plugin or the marketplace manifest.

## Plugin Version Bump — Two-Phase Sync (MANDATORY)

When a PR bumps any plugin's version (e.g. `1.5.0 → 1.6.0`), the marketplace must be synced in **two phases** around the merge. Skipping pre-merge gates risks landing leaked secrets or broken `marketplace.json` to public main; skipping post-merge actions leaves the author's local install pointing at the pre-merge state.

### Phase 1 — Pre-merge (run on the feature branch before opening PR for review)

Validation gates. Block the PR if any fails.

| Gate | Skill / Script | Why it must run before merge |
|------|---------------|------------------------------|
| Sanitize-check | `Skill: kc-plugin-forge:kc-plugin-forge-sanitize-check <plugin>` | Public plugins must not leak internal org markers / secrets / paths. BLOCK class halts publish; REJECT class triggers incident response (rotate credential + scrub history). |
| Codex manifest drift | `kc-marketplace-sync` Step 1.5 (drift check section) | `.codex-plugin/plugin.json` must match `.claude-plugin/plugin.json` on `version` / `description` / `keywords` / `license`. `interface.*` block is Codex-specific — do not touch. |
| Marketplace schema + installability | `scripts/marketplace-verify.sh` (L1 + L2) | Schema validates `marketplace.json`; install test confirms each plugin is resolvable from a clean `HOME`. Catches `source` field typos and orphaned entries before publish. |

If all three pass → open Draft PR (per user-preferences workflow), `gh pr ready` after CI green.

### Phase 2 — Post-merge (run from the **main workspace**, NOT a Conductor / feature-branch worktree)

Local state alignment with the squash-merged `main` commit.

| Action | Skill step | Why it must run after merge |
|--------|------------|----------------------------|
| Auto-tag `<plugin>-v<version>` | `kc-marketplace-sync` Step 2.5 | Tag must point at the squash-merge commit on `main`. Tagging a feature-branch commit orphans the tag after squash-merge. |
| Local install rsync (`~/.claude/plugins/local/<plugin>`) | Step 3 | Subagents read references from local install; if it mirrors the feature branch instead of `main`, dispatched agents see uncommitted state. |
| Codex local install (`~/.codex/local-plugins/<plugin>`) | Step 3.1 | Codex CLI parallel of the above. |
| Clear stale cache | Step 4 | Forces cache rebuild on next plugin load. |

Run via: `Skill: kc-marketplace-sync <plugin>` from `$KC_WORKSPACE/kc-claude-plugins` (= `~/Project/kc-claude-workspace/kc-claude-plugins`). The skill auto-routes Phase 2 steps when invoked post-merge.

### Why not collapse into one phase?

- **Pre-merge gates are validation** — must run *before* untrusted state hits `main`.
- **Post-merge actions depend on the merge commit existing** (auto-tag) or mirror `main` into local install — running them pre-merge on a feature branch contaminates local state with uncommitted code.

If you skip Phase 2 after merge, the author's machine ends up serving stale subagent references — symptoms include "the new skill change isn't taking effect" until the next `/kc-marketplace-sync` run.

## Commit / PR Conventions (per user-preferences)

- **Commit format**: `<type>(<plugin-or-scope>): <description>` — types: `feat / fix / docs / chore / refactor / test / style / perf / ci`. Scope is plugin slug (e.g. `feat(e2e-pipeline):`, `chore(kc-pr-flow):`) for plugin-local changes, or `readme / scripts / marketplace` for repo-wide changes.
- **Stage explicitly** — never `git add .`; always name touched files. Pre-commit hooks honor this.
- **Version parity** — when bumping any plugin's version, all three sources must end at the same value:
  - `<plugin>/.claude-plugin/plugin.json`
  - `<plugin>/.codex-plugin/plugin.json` (if Codex-enabled)
  - `.claude-plugin/marketplace.json` entry for that plugin
- **Default PR mode**: Draft. Convert with `gh pr ready` after CI green.
- **Output language**: Chinese for explanations to user; English for `SKILL.md`, agent `.md`, hooks scripts, commit messages, PR body. Match per-plugin conventions when they differ.

## Per-Plugin CLAUDE.md (deeper conventions)

Plugin-internal rules (trigger conditions, internal agent registry, shared-config paths, etc.) live in each plugin's own `CLAUDE.md`:

- `e2e-pipeline/CLAUDE.md`
- `kc-hyperfocus/CLAUDE.md`
- `kc-nightwatch/CLAUDE.md`
- `kc-plugin-forge/CLAUDE.md`
- `kc-pr-flow/CLAUDE.md`

`kc-team-ops` does not currently have a CLAUDE.md.
