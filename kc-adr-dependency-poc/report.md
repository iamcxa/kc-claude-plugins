# kc-adr dependency POC: report

Date 2026-10-21. Hosts: Claude Code 2.1.305, codex-cli 0.162.1. Task: kc-adr-dependency-poc (profile poc).

## Ruling

Recommended arm: **run-time resolution** (a dev2 script finds the installed kc-adr and checks a version range it reads from one file). It is the only arm that meets all four bar items on both hosts. Claude Code's native dependency is a real, working add-on there, but Codex has none. A symlink fails on Codex and never checks versions on Claude. Wrap-not-move (today's tools stay in dev2) stays a safe fallback because it needs nothing from kc-adr.

## Result table (bar: installs / update reaches dev2 / absent refuses loudly / incompatible version caught)

Every cell was observed in a real install unless marked (doc) or (not observed).

| Arm | Host | Installs | kc-adr update reaches dev2 | Absent kc-adr refuses loudly | Incompatible version caught |
|---|---|---|---|---|---|
| A native dependency | Claude | yes: `install dev2-native` printed `(+ 1 dependency: kc-adr)`; kc-adr got `"auto": true` | yes, but only by `claude plugin update kc-adr`; `update dev2-native` said "already at the latest version" and left kc-adr alone. Auto-update of dependencies is (doc), not observed (it runs only in an interactive session) | partly: after `uninstall kc-adr` (printed `warning: required by dev2-native`) `claude plugin list` shows dev2-native `✘ failed to load`, `Error: Dependency "kc-adr@poc-mk" is not installed`. The whole plugin disappears; a live model session was not run | yes, at install and update: `has conflicting version requirements (no version satisfies all of: ^3.0, ^1.0)`; `is installed at 2.0.0, which does not satisfy: ^1.0`; `update kc-adr` stopped at 1.2.0 while 2.0.0 existed (`highest tag satisfying ^1.0 from dev2-native`) |
| A native dependency | Codex | **no mechanism.** A `dependencies` array in `.codex-plugin/plugin.json` was accepted silently; `codex plugin add dev2-native` installed only dev2-native, `codex plugin list` kept kc-adr `not installed`. Codex's own schema (`codex app-server generate-json-schema`, types PluginDetail, PluginSummary, PluginInterface) has no dependency field; the Codex plugin docs list none | n/a | n/a | n/a |
| B symlink | Claude | yes. Same-marketplace symlink is copied as a real directory (docs: allowed "between plugins within one marketplace") | no: kc-adr 2.1.0 left dev2's copy at 2.0.0 and `update dev2-symlink` said "already at the latest version"; only a dev2 version bump (0.1.1) re-copied | no: kc-adr is bundled, so absence is never seen | no |
| B symlink | Codex | installs, but the symlink is **dropped silently**: `vendor-kc-adr` is absent from `~/.codex/plugins/cache/.../dev2-symlink/0.1.0` | n/a | n/a | n/a |
| C run-time resolution | Claude | yes (dev2 and kc-adr are independent plugins) | yes: kc-adr 2.3.0 to 2.4.0 via `update kc-adr`, dev2 untouched, resolver returned the new path | yes: exit 3, `kc-adr is not installed (needed: 2.1.0 <= version < 3.0.0). Claude Code: claude plugin install ...  Codex: codex plugin add ...` | yes: exit 4, `no installed kc-adr is in the supported range 3.0.0 <= version < 4.0.0; found: 2.4.0 (...)`; the same for a ceiling of 2.0.0 |
| C run-time resolution | Codex | yes | yes: `codex plugin marketplace upgrade` replaced the installed kc-adr cache directory (2.2.0 to 2.3.0, 2.4.0 to 2.5.0); no `plugin add` needed | yes: exit 3, same message | yes: exit 4, same messages |
| D wrap (control) | Claude, Codex | yes, both | n/a: dev2's own scripts; dev2 version bump only | n/a: nothing to be absent | n/a: no coupling, so nothing to check |

Layouts the resolver was run against (kc-adr 2.x stand-in):
- Claude marketplace cache from a git marketplace: found through `installed_plugins.json` (`installPath` is `cache/<marketplace>/kc-adr/<version>`; a tag-resolved dependency gets `1.2.0-<sha>` as the directory name, so a path glob is unreliable; the index is authoritative).
- Claude folder marketplace (the `~/.claude/plugins/local` style): `installPath` is a cache copy, but `claude plugin list` says "Read from: <source folder>" and the docs say the plugin loads in place. After editing the source to 2.5.0 the resolver still returned the 2.4.0 cache copy. Known gap.
- Codex git marketplace: `~/.codex/plugins/cache/<marketplace>/kc-adr/<version>`.
- Codex `~/.agents/plugins/marketplace.json` + `~/.codex/local-plugins/kc-adr`: `codex plugin add kc-adr@kent-local` installs into `cache/kent-local/kc-adr/<version>`; the resolver also checks `local-plugins/kc-adr` directly and picked it (2.6.0) before the re-add. `codex plugin marketplace upgrade` did not refresh it ("All configured Git marketplaces are already up to date"); only `plugin add` again did.
- Host separation matters: the resolver looks only at the host it runs on (decided from its own path). With both hosts' roots searched, a Claude session would find the Codex copy and hide a missing Claude install.

## Version floor and a CI job that tests the two together

The floor and ceiling live in one file next to the resolver (`kc-adr-range`, two numbers: floor inclusive, ceiling exclusive). A CI job needs no install: clone kc-adr at each tag and point `KC_ADR_ROOT` at it. Run locally against real tags, range 2.1.0 to 3.0.0 exclusive: kc-adr 1.2.0 exit 4, 2.0.0 exit 4, 2.1.0 exit 0, 2.5.0 exit 0, 3.0.0 exit 4. Cost per PR: not measured. Claude's native range lives in `plugin.json` (`"dependencies":[{"name":"kc-adr","version":"^2.1"}]`), a second copy of the same fact; a check that the two agree would be needed if both are kept.

Codex has no constraint: it follows the marketplace HEAD (`marketplace add` offers `--ref`; pinning by ref was read in `--help` only, not run). So on Codex a kc-adr 3.0.0 release makes dev2 refuse after the next upgrade; only the run-time ceiling guards that.

## Tag naming risk for the native arm (read from files, not run)

Claude resolves a constraint against git tags named `<plugin>--v<version>` (docs: plugin-dependencies, "Create a release tag"). This repository's release-please cuts `<plugin>-vX.Y.Z` (root CLAUDE.md; `kc-dev-flow-2/README.md` "kc-dev-flow-2-vX.Y.Z"). I tested only with `--v` tags. For a relative-path plugin with no matching tag the docs say the install uses the marketplace's current copy and checks the range at load. Using the native arm here needs either `claude plugin tag` alongside release-please or that behavior accepted. Not run.

## What a move would change (the four adopters)

Verified by `git grep` at each checkout's HEAD or origin/main, 2026-10-21:
- kc-claude-plugins `docs/dev2/README.md`: 5 lines name `number_guards`, `adr_lint` or `adr-template` (plus `kc-dev-flow-2/references/sd/workflow.md` 5, `skills/implementation/principles.md` 3, `skills/validation/principles.md` 1).
- subspace-relay: `docs/dev2/README.md` 5, `docs/dev2-poc/README.md` 5, `docs/adr/README.md` 1.
- qnow (checked in the qnow-adopt-dev2 checkout): `docs/dev2/README.md` 5, `docs/dev2-poc/README.md` 5.
- carlove-v1: no git checkout found under `~/conductor`, not verified.
Each adopter README carries the release marker `<!-- kc-dev-flow-2 X.Y.Z x-release-please-version -->`; none declares a kc-adr pin today.

If the ADR tools moved under run-time resolution: the lines `python3 <package>/scripts/adr_lint.py ...` become `python3 <package>/scripts/kc_adr.py run adr_lint.py ...` (or the kc-adr package root of the loaded kc-adr skill), the template path moves to kc-adr, the sync of the adopter workflow README carries that text, and each adopter machine installs one more plugin per host. Under wrap-not-move none of these change.

What a split of `number_guards.py` would need (read from its docstring, not run): `reserve` takes the next number from the base tip and every other task file in the state checkout, and `check` rules R4/R5 read the task's `## Number guards` section; both inputs are dev2 task files. kc-adr could own the ADR half only if the task-file reservation contract is stated as an input it accepts, with one owner of the reservation file (ADR 0002 names one file for ADR and migration numbers).

## Isolation used

A `mktemp` directory under `/tmp` held: `HOME`, `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, a stand-in marketplace (a git repo of throwaway plugins named kc-adr, dev2-native, dev2-symlink, dev2-resolve (+ old/new range variants), dev2-wrap), and a `$HOME/.gitconfig` that rewrites `https://github.com/` and `git@github.com:` to a `file://` bare repo (Claude refuses `git://` and cannot take a `file://` URL directly; a folder source loads in place). A local `git daemon` and `http.server` used while finding that route were stopped. The whole directory and the scripts directory were deleted after the probes. Nothing in this repository, any adopter, or any installed plugin was edited. After the probes `~/.claude/plugins/known_marketplaces.json`, `installed_plugins.json`, `~/.claude/settings.json` and `~/.codex/config.toml` held no probe entry (grep count 0) and their modified times predated the probes.

One slip: a chained command ran once with `HOME` unset to the probe directory, so `claude plugin marketplace add /mk` ran against the real config; it answered `Path does not exist` and wrote nothing (same grep and times above).

## Unanswered

- A live model session was not run (isolated config has no login), so what a worker sees when dev2 fails to load, or when the resolver exits 3, is observed only through `claude plugin list` and script output.
- Auto-update of a dependency, a disabled-but-installed kc-adr (the resolver does not check enabled state), cross-marketplace dependencies, Codex `--ref` pinning and Windows were not run.
- The stand-in resolver (about 90 lines, stdlib Python) is throwaway and was deleted; this report holds its rules, not its code.
