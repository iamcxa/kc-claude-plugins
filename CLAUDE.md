# kc-claude-plugins

Public marketplace repo containing seven plugins: `e2e-pipeline`, `kc-plugin-forge`, `kc-nightwatch`, `kc-hyperfocus`, `kc-team-ops`, `kc-pr-flow`, and `kc-dev-flow`. Plugins may keep their own `CLAUDE.md` for plugin-internal conventions. This file documents **repo-wide rules** that apply to PRs touching any plugin or the marketplace manifest.

## Plugin Versioning & Release — release-please (MANDATORY)

Versioning, tagging, and changelogs are owned by **release-please** (monorepo manifest mode, one independent component per plugin — see `release-please-config.json` + `.release-please-manifest.json`). **Do not hand-bump versions in a feature PR.** A feature PR touches only its plugin's files (`<plugin>/**`) using Conventional Commits; the version bump is proposed automatically.

### How a release happens

1. **Feature PR** — implement under `<plugin>/`, Conventional-Commit scoped to that plugin (`feat(<plugin>): …` / `fix(<plugin>): …`). **No version edits**, no marketplace / codex manifest edits for versioning. Squash-merge to `main`.
2. **Release PR (automatic)** — on push to `main`, `.github/workflows/release-please.yml` opens/updates a Release PR that, per changed plugin, bumps the version across `<plugin>/.claude-plugin/plugin.json`, `<plugin>/.codex-plugin/plugin.json`, and that plugin's `.claude-plugin/marketplace.json` entry (**version string only** — the bespoke marketplace `description`/`keywords` are never touched), and writes `<plugin>/CHANGELOG.md`.
3. **Merge the Release PR** — release-please cuts the `<plugin>-vX.Y.Z` tag + GitHub Release. A `RELEASE_PLEASE_TOKEN` PAT is required so the bot-opened Release PR fires the required status checks — see the comment in `release-please.yml`.

New components inherit the repository's explicit `initial-version: 0.1.0`
policy. Cross-repository adopters must pin only an actually published tag after
the Release PR merges; never prepare a final dependency pin from a predicted
release version.

Version lives in release-please's component manifest and is propagated to `<plugin>/.claude-plugin/plugin.json`, the Codex manifest, and the marketplace entry. In `extra-files`, plugin files are package-relative (for example `.claude-plugin/plugin.json`), while repo-root files require a leading `/` (for example `/.claude-plugin/marketplace.json`). The README no longer carries per-plugin version badges (marketplace.json / tags / Releases are the source).

### Pre-merge gates (apply to feature PRs and the Release PR)

| Gate | Skill / Script | Why |
|------|---------------|-----|
| Sanitize-check | `Skill: kc-plugin-forge:kc-plugin-forge-sanitize-check <plugin>` | Public plugins must not leak internal org markers / secrets / paths. BLOCK class halts publish; REJECT class triggers incident response (rotate credential + scrub history). |
| Marketplace schema + installability | `scripts/marketplace-verify.sh` (L1 + L2) | Schema validates `marketplace.json`; install test confirms each plugin is resolvable from a clean `HOME`. Catches `source` typos and orphaned entries before publish. |
| Release config + version parity guard | `scripts/version-parity-check.sh` (CI: `marketplace-parity.yml`, required check) | Runs a pinned release-please fixture for the first version/tag after a feature commit, validates every resolved `extra-files` path and JSONPath target, then compares the release manifest / `plugin.json` / `.codex-plugin/plugin.json` / marketplace entry — including that every on-disk plugin directory (`*/.claude-plugin/plugin.json`) has a matching `marketplace.json` entry and vice versa (fail-closed on an unlisted directory). As a required check it **blocks merge on bootstrap-policy drift, invalid propagation config, real version drift, or an unregistered plugin directory** (including the Release PR). |
| Skill frontmatter lint | `scripts/skill-frontmatter-lint.sh` (CI: `marketplace-parity.yml`, required check) | Validates every `*/skills/*/SKILL.md` has parseable YAML frontmatter with a non-empty `name` and `description`. **Blocks merge on a malformed or incomplete skill manifest.** |

### Post-merge — LOCAL install sync (run from the **main workspace**, NOT a Conductor / feature-branch worktree)

release-please owns versioning + tagging in the cloud, but it **cannot touch your machine's local install**. After the Release PR merges, mirror `main` into the author's local plugin installs so dispatched subagents read current references:

| Action | Why |
|--------|-----|
| Local install rsync (`~/.claude/plugins/local/<plugin>`) | Subagents read references from local install; stale local = agents see old state. |
| Codex local install (`~/.codex/local-plugins/<plugin>`) | Codex CLI parallel of the above. See **Codex install conventions** below. |

Run `Skill: kc-plugin-forge:kc-plugin-release` from the main workspace
(`$KC_WORKSPACE` on this machine; wherever you cloned `kc-claude-plugins`
elsewhere), then use its packaged post-release sync helper. The helper only
copies local installs; it has no version, tag, changelog, or marketplace
authority. Its boundary is enforced by
`kc-plugin-forge/scripts/plugin-release-contract-check.sh`.

**Codex install conventions** — two layouts coexist on a typical machine and both are valid:

| Layout | Path | Use case |
|--------|------|----------|
| Rsync copy (recommended for new plugins) | `~/.codex/local-plugins/<plugin>/` | Snapshots `main` post-merge. Defeats the "subagent sees uncommitted state" failure mode by definition. |
| Symlink to source | `~/plugins/<plugin>` (with `~/.agents/plugins/marketplace.json` entry; documented in `kc-plugin-forge/README.md`) | Live-edit during plugin development. Skips the rsync but loses the "main only" guarantee. |

Codex resolves both via `~/.agents/plugins/marketplace.json` `source.path`
(relative to `$HOME`). The packaged helper writes to the rsync layout; older
plugins (e.g. `kc-plugin-forge`) may still use the symlink convention. Migration
is optional; the helper refuses to replace a working symlink.

If you skip the post-merge local sync, the author's machine serves stale
subagent references. A common symptom is that a newly released skill change
does not take effect locally.

## Commit / PR Conventions (per user-preferences)

- **Commit format**: `<type>(<plugin-or-scope>): <description>` — types: `feat / fix / docs / chore / refactor / test / style / perf / ci`. Scope is plugin slug (e.g. `feat(e2e-pipeline):`, `chore(kc-pr-flow):`) for plugin-local changes, or `readme / scripts / marketplace` for repo-wide changes.
- **Stage explicitly** — never `git add .`; always name touched files. Pre-commit hooks honor this.
- **Versioning is release-please-owned** — do not hand-bump versions in a feature PR (see "Plugin Versioning & Release"). release-please propagates the component manifest version across `<plugin>/.claude-plugin/plugin.json`, `<plugin>/.codex-plugin/plugin.json`, and the `.claude-plugin/marketplace.json` entry; `version-parity-check.sh` guards the config and all tracked values.
- **Default PR mode**: Draft. Convert with `gh pr ready` after CI green.
- **Output language**: Chinese for explanations to user; English for `SKILL.md`, agent `.md`, hooks scripts, commit messages, PR body. Match per-plugin conventions when they differ.
- **An absolute claim names its enforcement point** — "exactly", "only", "always", "never", "cannot", "byte-for-byte" in a reference, a code comment, or a commit message must cite what makes it true, or be rewritten as the bounded claim the code supports. Full rule: `kc-dev-flow/references/kernel.md` § Outcome discipline, "an absolute names its enforcement point or becomes a bounded claim"; this repository's own coverage notes are in `docs/dev/README.md` § Proof Policy. It is here too because nothing downstream checks a claim in a commit message or a code comment — both get read (a reviewer skims comments in a diff; `kc-pr-review` parses issue IDs out of commit messages), but neither has a gate that would test an absolute in them, so the writing moment is effectively the only one.

## Per-Plugin CLAUDE.md (deeper conventions)

Plugin-internal rules (trigger conditions, internal agent registry, shared-config paths, etc.) live in each plugin's own `CLAUDE.md`:

- `e2e-pipeline/CLAUDE.md`
- `kc-hyperfocus/CLAUDE.md`
- `kc-nightwatch/CLAUDE.md`
- `kc-plugin-forge/CLAUDE.md`
- `kc-pr-flow/CLAUDE.md`

`kc-team-ops` does not currently have a CLAUDE.md.
