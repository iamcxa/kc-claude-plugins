# kc-claude-plugins

Public marketplace repo containing six plugins: `e2e-pipeline`, `kc-plugin-forge`, `kc-nightwatch`, `kc-hyperfocus`, `kc-team-ops`, `kc-pr-flow`. Each plugin keeps its own `CLAUDE.md` for plugin-internal conventions. This file documents **repo-wide rules** that apply to PRs touching any plugin or the marketplace manifest.

## Plugin Versioning & Release — release-please (MANDATORY)

Versioning, tagging, and changelogs are owned by **release-please** (monorepo manifest mode, one independent component per plugin — see `release-please-config.json` + `.release-please-manifest.json`). **Do not hand-bump versions in a feature PR.** A feature PR touches only its plugin's files (`<plugin>/**`) using Conventional Commits; the version bump is proposed automatically.

### How a release happens

1. **Feature PR** — implement under `<plugin>/`, Conventional-Commit scoped to that plugin (`feat(<plugin>): …` / `fix(<plugin>): …`). **No version edits**, no marketplace / codex manifest edits for versioning. Squash-merge to `main`.
2. **Release PR (automatic)** — on push to `main`, `.github/workflows/release-please.yml` opens/updates a Release PR that, per changed plugin, bumps the version across `<plugin>/.claude-plugin/plugin.json`, `<plugin>/.codex-plugin/plugin.json`, and that plugin's `.claude-plugin/marketplace.json` entry (**version string only** — the bespoke marketplace `description`/`keywords` are never touched), and writes `<plugin>/CHANGELOG.md`.
3. **Merge the Release PR** — release-please cuts the `<plugin>-vX.Y.Z` tag + GitHub Release. A `RELEASE_PLEASE_TOKEN` PAT is required so the bot-opened Release PR fires the required status checks — see the comment in `release-please.yml`.

Version lives in **one canonical place per plugin** (`<plugin>/.claude-plugin/plugin.json`, tracked by the manifest); the codex manifest + marketplace entry are propagated by release-please, and the README no longer carries per-plugin version badges (marketplace.json / tags / Releases are the source).

### Pre-merge gates (apply to feature PRs and the Release PR)

| Gate | Skill / Script | Why |
|------|---------------|-----|
| Sanitize-check | `Skill: kc-plugin-forge:kc-plugin-forge-sanitize-check <plugin>` | Public plugins must not leak internal org markers / secrets / paths. BLOCK class halts publish; REJECT class triggers incident response (rotate credential + scrub history). |
| Marketplace schema + installability | `scripts/marketplace-verify.sh` (L1 + L2) | Schema validates `marketplace.json`; install test confirms each plugin is resolvable from a clean `HOME`. Catches `source` typos and orphaned entries before publish. |
| Version parity guard | `scripts/version-parity-check.sh` (CI: `marketplace-parity.yml`, required check) | Backstop that release-please wrote `plugin.json` / `.codex-plugin/plugin.json` / marketplace entry consistently, and catches accidental manual drift. As a required check it **blocks merge on a real mismatch** (including the Release PR), so release-please must propagate the version to every tracked source — including each Codex-enabled plugin's `.codex-plugin/plugin.json`. |

### Post-merge — LOCAL install sync (run from the **main workspace**, NOT a Conductor / feature-branch worktree)

release-please owns versioning + tagging in the cloud, but it **cannot touch your machine's local install**. After the Release PR merges, mirror `main` into the author's local plugin installs so dispatched subagents read current references:

| Action | Why |
|--------|-----|
| Local install rsync (`~/.claude/plugins/local/<plugin>`) | Subagents read references from local install; stale local = agents see old state. |
| Codex local install (`~/.codex/local-plugins/<plugin>`) | Codex CLI parallel of the above. See **Codex install conventions** below. |
| Clear stale cache (`~/.claude/plugins/cache/local/<plugin>`) | Forces cache rebuild on next plugin load. |

Run the local-sync subset via `Skill: kc-marketplace-sync <plugin>` from the main workspace (`$KC_WORKSPACE` on this machine; wherever you cloned `kc-claude-plugins` elsewhere). The skill's tagging / marketplace / README steps are **superseded by release-please** — only its local-install steps remain relevant.

**Codex install conventions** — two layouts coexist on a typical machine and both are valid:

| Layout | Path | Use case |
|--------|------|----------|
| Rsync copy (recommended for new plugins) | `~/.codex/local-plugins/<plugin>/` | Snapshots `main` post-merge. Defeats the "subagent sees uncommitted state" failure mode by definition. |
| Symlink to source | `~/plugins/<plugin>` (with `~/.agents/plugins/marketplace.json` entry; documented in `kc-plugin-forge/README.md`) | Live-edit during plugin development. Skips the rsync but loses the "main only" guarantee. |

Codex resolves both via `~/.agents/plugins/marketplace.json` `source.path` (relative to `$HOME`). The `kc-marketplace-sync` skill writes to the rsync layout; older plugins (e.g. `kc-plugin-forge`) still ship the symlink convention. Migration is optional; do not break working symlinks.

If you skip the post-merge local sync, the author's machine serves stale subagent references — symptoms include "the new skill change isn't taking effect" until the next `/kc-marketplace-sync` run.

## Commit / PR Conventions (per user-preferences)

- **Commit format**: `<type>(<plugin-or-scope>): <description>` — types: `feat / fix / docs / chore / refactor / test / style / perf / ci`. Scope is plugin slug (e.g. `feat(e2e-pipeline):`, `chore(kc-pr-flow):`) for plugin-local changes, or `readme / scripts / marketplace` for repo-wide changes.
- **Stage explicitly** — never `git add .`; always name touched files. Pre-commit hooks honor this.
- **Versioning is release-please-owned** — do not hand-bump versions in a feature PR (see "Plugin Versioning & Release"). release-please propagates the version across `<plugin>/.claude-plugin/plugin.json`, `<plugin>/.codex-plugin/plugin.json`, and the `.claude-plugin/marketplace.json` entry; `version-parity-check.sh` guards that the three stay consistent.
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
