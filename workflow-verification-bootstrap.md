---
id: te82apnehg989v4enz9e6wf6
title: Workflow verification bootstrap
status: implementation
source: commission seed (lean SD workflow, 2026-07-24)
started: 2026-07-24T05:26:29Z
completed:
verdict:
score: 0.7
worktree: .worktrees/spacedock-ensign-workflow-verification-bootstrap
issue:
pr:
design:
---

## Problem

Stand up this plugin monorepo's mechanical floors. Unlike a code repo, the
floor here is STRUCTURAL, not coverage: (1) audit what structural checks
already exist (marketplace sync tooling, sanitize-check, .githooks, CI
workflows) and wire a blocking plugin-structure lint — plugin.json manifest
validity and version consistency, marketplace manifest agreement, skill
frontmatter validity — fail-closed: a plugin directory missing required
manifest fields must go red, never silently skipped. (2) Initialize
`docs/dev/ledger.csv` with the measurement header. (3) Decide diff-coverage
feasibility for the thin executable layer (scripts/, hooks) and record the
determination either way.

## Scope disposition

Captain scope questions were skipped (small-scope reason, per the ideation
discipline's skip clause): the Problem paragraph above is verbatim
captain-authored scope from the commission seed, not agent-inferred, and the
ideation checklist the first officer dispatched further pins the three
concrete deliverables (fail-closed lint, ACs, ledger bookkeeping). The audit
below surfaced exactly one real open judgment call — diff-coverage tooling
selection — which is recorded as an explicit backlog deferral rather than
decided silently.

## Reverse-recovery audit

Run against `origin/main` fetched fresh this session
(`01bc8e324a7d1a41ffc91c927c46712715343df6`, PR #51 "adopt split-root
state"), **not** the working branch. The working branch in this checkout
(`iamcxa/audit-kc-pr-review-agent-native-...`) has diverged and lags
`origin/main` by 4 commits (`a0f50f4`, `536be3e`, `4b8dc32`, `01bc8e3`) —
auditing it would have understated what already exists. All evidence below
was read via `git show origin/main:<path>` / `git ls-tree origin/main`, and
the branch-protection claim was cross-checked live against the GitHub API,
independent of any file in the repo.

| # | Capability | State | Evidence |
|---|---|---|---|
| 1 | Plugin version sync (release manifest / `plugin.json` / marketplace entry / Codex manifest) | **WORKING** | `scripts/version-parity-check.sh` (full file) compares all 4 sources per plugin. Wired as the only step (with `release-metadata.test.sh`) in `.github/workflows/marketplace-parity.yml:29-38`, triggered on every `pull_request` + `push:main` with **no path filter** (`marketplace-parity.yml:17-19`, comment at `:1-15` states this is intentional so the required check never sits "pending"). Confirmed **live**, independent of repo source: `gh api repos/iamcxa/kc-claude-plugins/branches/main/protection` → `required_status_checks.contexts == ["version parity (plugin.json / marketplace.json / codex / README)"]`, matching the job `name:` at `marketplace-parity.yml:26`. Also documented at `CLAUDE.md:23`. |
| 2 | Plugin-directory enumeration is fail-closed (a dir with `.claude-plugin/plugin.json` not listed in `marketplace.json`, or vice versa, must fail) | **EXISTS_BROKEN** (seam defect inside check #1, not a whole-check failure) | `scripts/version-parity-check.sh:30` derives the plugin set **exclusively** from `marketplace.json`'s `plugins[].name` (`PLUGINS=$(python3 -c "...json.load(open('$MARKETPLACE_JSON'))['plugins']...")`) — never from a filesystem scan of `*/.claude-plugin/plugin.json`. Today's 6 marketplace entries (`e2e-pipeline, kc-plugin-forge, kc-nightwatch, kc-hyperfocus, kc-team-ops, kc-pr-flow`) match the 6 on-disk plugin dirs 1:1 — zero current drift — but a 7th dir added without updating `marketplace.json` runs through **zero** checks and the required job still reports green. This is precisely the gap the original AC-1 named ("Falsified by: ...the check silently skips unknown plugin directories"). |
| 3 | marketplace.json entry ↔ `plugin.json` cross-consistency (name, version) | **WORKING** | Subsumed by check #1's same comparison loop (`version-parity-check.sh` MK/PJ columns). |
| 4 | marketplace.json schema validity + install resolvability | **STUB** | `scripts/marketplace-verify.sh` L0-L2 (full file) is correct and runnable standalone, documented as a pre-merge gate at `CLAUDE.md:20` — but `git grep -n "marketplace-verify.sh" .github/workflows/` returns **zero hits**: no workflow invokes it. Manual-only; requires the `claude` CLI + a real plugin install per plugin, which is why it isn't in the required (no-path-filter, ~7s) job. |
| 5 | Skill frontmatter validity (`SKILL.md` YAML frontmatter has required fields) | **MISSING** | Proof of absence, multi-strategy: (a) `git grep -n 'SKILL.md' origin/main -- '*.sh' '*.py' '.github/workflows/*.yml'` → 0 script/workflow hits (only prose mentions inside `kc-plugin-forge/*.md` docs describing a *different* tool's runtime behavior). (b) `git grep -niE 'frontmatter' origin/main -- scripts/ .github/workflows/` → 0 hits. (c) The closest same-purpose capability, `plugin-dev:plugin-validator` (`kc-plugin-forge/docs/getting-started.md:109`, `README.md:153`), is a **third-party marketplace plugin's LLM agent** — not this repo's code, not deterministic, not installed by default ("not found \| Install the plugin-dev marketplace plugin"), not wired to any workflow. Confirmed across 35 `SKILL.md` files repo-wide (`git ls-tree -r --name-only origin/main \| grep -E 'skills/.*/SKILL\.md$' \| wc -l`) that `name` + `description` is the uniform, load-bearing frontmatter shape (e.g. `e2e-pipeline/skills/e2e-flow/SKILL.md:1-3`; also relied on by `kc-plugin-forge-help/SKILL.md:32` to build its own skill index). Greenfield permitted for this one check only. |
| 6 | Sanitize-check (leak-pattern grep for public plugin files) | **WORKING**, manual tool | `kc-plugin-forge/skills/kc-plugin-forge-sanitize-check/SKILL.md`, documented pre-merge gate at `CLAUDE.md:19`. Not CI-wired by design (pre-publish/interactive), not one of this task's 3 named checks — listed for inventory completeness only. |
| 7 | `.githooks/pre-commit` | **WORKING**, narrow scope | Runs biome lint + `npm test` only when staged files match `^e2e-pipeline/` (`.githooks/pre-commit` full file). Not a general plugin-structure gate; out of this task's scope. |
| 8 | Diff-coverage tooling for `scripts/`, hooks | **MISSING** | `git grep -niE 'diff-cover\|codecov\|kcov\|bashcov\|coverage'` across `*.yml/*.sh/*.json` in `origin/main` → every hit is either a comment/UI string or the literal JSON field `"coverage"` inside `kc-pr-flow`'s own typed review-receipt schema (semantically unrelated). No coverage-instrumentation tooling exists anywhere in the repo. |

**Conclusion:** two of the task's three named checks already exist and one
(#1/#3, version sync) is a live, confirmed, required CI gate. Scope narrows
to: **repair** the seam defect in #2 (fail-closed enumeration) and **build**
the genuinely missing #5 (skill frontmatter lint) — both wired into the
*existing* required job rather than a new one, and the diff-coverage
question (item 3 of the Problem) gets a determination, not new tooling, per
the appetite below.

## Proposed approach

Two behaviors, both landing inside the already-required
`marketplace-parity.yml` job (job `name:` stays untouched, so the live
branch-protection required-check identity — see audit row 1 — is preserved;
see "Spike" below for why this is safe without a dry-run):

1. **Repair row 2** — extend `scripts/version-parity-check.sh` (or a small
   sibling script it calls) to derive the plugin set from **both**
   `marketplace.json` and a filesystem scan of `*/.claude-plugin/plugin.json`,
   and fail with a named-directory message on any asymmetry.
2. **Build row 5** — add `scripts/skill-frontmatter-lint.sh` (name
   provisional, implementation may adjust): for every `*/skills/*/SKILL.md`,
   parse the YAML frontmatter block and fail if it is missing, malformed, or
   missing a non-empty `name` or `description`. Also fail if a `skills/*`
   subdirectory exists with no `SKILL.md` at all (a stub skill dir). Add this
   as a new step in the same CI job.

Both follow the repo's existing `*.test.sh` pass/fail-harness convention
(pattern: `scripts/release-metadata.test.sh`) for their own tests.

## Design determination

`trivial-pass` — no UI, contract, schema, or user-facing surface is touched;
this is internal CI/lint tooling plus a doc-diff to `CLAUDE.md`'s internal
contributor-facing table. No wireframe/API-shape decision applies.

## Appetite

~90 minutes of implementation time (this ideation stage's own effort is
separate and already spent). **Pre-registered scope cut**: the two behaviors
above are ordered by value — build row 5 (skill frontmatter lint, closes a
MISSING gap) is P0; repair row 2 (enumeration fail-closed) is P1. If the
session is about to exceed budget, cut P1: defer the enumeration repair to a
follow-up backlog task (it improves an already-partially-working check
rather than closing a zero-coverage gap) and ship P0 alone, recording the cut
in the implementation stage report — never compress the RED→GREEN loop or
skip a test to land both inside the budget.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is
**criteria that pass without delivering value**: the frontmatter lint only
checks that `name` and `description` are present and non-empty, so a
`SKILL.md` with a well-formed-but-garbage description (or a malformed
`allowed-tools`/other field the lint doesn't inspect) still passes green
while contributing to the exact class of structural drift this task exists
to catch.

## Spike

No spike needed: the required-check identity is GitHub's
`required_status_checks.contexts` string, which is bound to the job's static
`name:` field (`marketplace-parity.yml:26`), not its step list — confirmed
live via `gh api .../branches/main/protection` (see audit row 1). Adding
steps to the existing `parity` job preserves the required-check identity as
long as implementation does not rename or restructure the job. This is a
proven mechanism (read directly off the live branch-protection state, not
assumed), so no separate dry-run spike is needed before implementation.

## Acceptance criteria

**Baseline (today):** of the 3 structural-check categories named in this
task's Problem, 1/3 (plugin version sync) has 100% CI enforcement and is a
live required check; 2/3 (skill-frontmatter validity, plugin-dir enumeration
fail-closed) have 0% CI enforcement despite one of them (enumeration) living
inside an otherwise-working script. **Target:** 3/3 at enforced-in-the-same
required-check status, with the pre-existing 1/3 unregressed — a
plausible failure mode is implementation breaking the existing check while
wiring the new ones, which would move this baseline the wrong way (3/3 down
to 2/3 or worse).

**AC-1 — Skill frontmatter lint blocks the required CI check on a malformed or incomplete `SKILL.md`.**
Verified by: on a scratch branch, delete the `description:` field (or the whole frontmatter block) from one `SKILL.md`, push, and observe the live `version parity (plugin.json / marketplace.json / codex / README)` required check go red in a real GitHub Actions run, citing the broken file's path in its output. Falsified by: the probe passes, or the check inspects only a subset of the repo's 35 `SKILL.md` files (e.g. skips a plugin), or exits 0 on a `skills/*` directory with no `SKILL.md` at all.

**AC-2 — Plugin-directory enumeration is fail-closed.**
Verified by: on a scratch branch, add a throwaway plugin directory with a valid `.claude-plugin/plugin.json` but no `marketplace.json` entry (and, separately, a `marketplace.json` entry with no matching on-disk directory), push, and observe the required check go red, naming the unlisted/orphaned directory. Falsified by: either probe passes silently (check exits 0 despite the asymmetry).

**AC-3 — The pre-existing version-parity / marketplace-consistency check (audit rows 1 and 3) keeps passing on current `main` state and remains the live branch-protection required check after this task's changes land.**
Verified by: `scripts/version-parity-check.sh` exits 0 unmodified on the merged state, and `gh api repos/iamcxa/kc-claude-plugins/branches/main/protection` still reports `required_status_checks.contexts == ["version parity (plugin.json / marketplace.json / codex / README)"]` post-merge. Falsified by: the check is removed/renamed in branch protection, or a deliberately bumped-but-unpropagated `plugin.json` version passes.

**AC-4 — `docs/dev/ledger.csv` exists (created at implementation — see "Ledger bootstrap" below) with a header byte-identical to this README's Measurement Ledger schema.**
Verified by: `head -1 docs/dev/ledger.csv` diffed byte-for-byte against `docs/dev/README.md`'s fenced schema line (`task_id, slug, dispatches, rework_rounds, wallclock_hours, tokens_if_known, diff_coverage, escaped_defects_7d`). Falsified by: header drift (reordered/renamed/extra/missing column) or a missing file.

**E2E-first:** satisfied without a skip. AC-1 through AC-3 are each verified by driving the real flow this task exists to protect — a push triggering a live GitHub Actions run evaluated against live branch protection — not a local dry-run of the script in isolation. This is a CI/config-only task (no full-stack or browser-drivable surface), so no browser/CLI-service E2E applies beyond that.

## Test plan

- `scripts/skill-frontmatter-lint.test.sh` (new, following the
  `release-metadata.test.sh` pass/fail-harness pattern): fixtures for (a)
  valid `SKILL.md` passes, (b) missing frontmatter block fails, (c) missing
  `description` fails, (d) missing `name` fails, (e) a `skills/*` dir with no
  `SKILL.md` fails, (f) a plugin with a `skills/` dir absent entirely passes
  trivially (not a defect — not every plugin has skills).
- A fixture (new `.test.sh`, or an addition to an existing one) proving
  enumeration fail-closed: a scratch plugin dir with `plugin.json` but no
  marketplace entry fails; a marketplace entry with no on-disk dir fails.
- Full local run of `scripts/version-parity-check.sh` and the new lint script
  against the actual repo tree once wired, as the stage-exit regression
  check (matching the repo's "scoped in the loop, full run at the exit"
  convention).
- The AC-1/AC-2/AC-3 real-CI-run probes described above (pushed to a scratch
  branch, observed, then reverted/discarded — not merged).

## Doc diff

`CLAUDE.md`, "Pre-merge gates" table (currently at lines 19-21):

Before:
```
| Release config + version parity guard | `scripts/version-parity-check.sh` (CI: `marketplace-parity.yml`, required check) | Validates every resolved `extra-files` path and JSONPath target, then compares the release manifest / `plugin.json` / `.codex-plugin/plugin.json` / marketplace entry. As a required check it **blocks merge on invalid propagation config or real version drift** (including the Release PR). |
```

After (amend the existing row + add one new row):
```
| Release config + version parity guard | `scripts/version-parity-check.sh` (CI: `marketplace-parity.yml`, required check) | Validates every resolved `extra-files` path and JSONPath target, then compares the release manifest / `plugin.json` / `.codex-plugin/plugin.json` / marketplace entry — including that every on-disk plugin directory (`*/.claude-plugin/plugin.json`) has a matching `marketplace.json` entry and vice versa (fail-closed on an unlisted directory). As a required check it **blocks merge on invalid propagation config, real version drift, or an unregistered plugin directory** (including the Release PR). |
| Skill frontmatter lint | `scripts/skill-frontmatter-lint.sh` (CI: `marketplace-parity.yml`, required check) | Validates every `*/skills/*/SKILL.md` has parseable YAML frontmatter with a non-empty `name` and `description`. **Blocks merge on a malformed or incomplete skill manifest.** |
```
Implementation applies this diff verbatim (adjusting the script name if it
differs from the provisional one above); validation verifies the CLAUDE.md
table and the behavior it describes landed together.

## Ledger bootstrap

`docs/dev/ledger.csv` is **not** created in this ideation stage. Ideation
has no dedicated worktree (`docs/dev/README.md` frontmatter:
`stages.defaults.worktree: false`, and `ideation` doesn't override it), and
the code checkout available to this stage is currently on an unrelated
feature branch (`iamcxa/audit-kc-pr-review-agent-native-...`, diverged from
`origin/main` — see audit preamble) — writing a repo infra file there would
land it on the wrong branch or strand it if that branch is abandoned. This
mirrors the doc-diff convention already established by this README
("ideation proposes ... implementation applies ... validation verifies"):
this section fully specifies the file for implementation to create verbatim
in its dedicated worktree, off trunk.

File: `docs/dev/ledger.csv`
Header (byte-identical to `docs/dev/README.md`'s Measurement Ledger schema,
confirmed via direct read of that line):
```
task_id, slug, dispatches, rework_rounds, wallclock_hours, tokens_if_known, diff_coverage, escaped_defects_7d
```
No data row lands with the header — per this README's own Measurement Ledger
section, a row is appended when a task reaches `done` (or is abandoned after
implementation started), which is this task's own terminal stage, not
ideation or implementation. AC-4 above verifies the header only.

## Diff-coverage feasibility determination

**Decision: not now — defer tooling selection to a follow-up backlog task.**
Audit row 8 proves no coverage-instrumentation tooling (kcov, bashcov,
codecov, or equivalent) exists anywhere in this repo today. Evaluating and
wiring one (runner package install, threshold calibration for a give-or-take
10-file `scripts/` tree, deciding whether `.githooks/pre-commit`'s
biome/npm-test lane needs its own instrumentation) is itself a judgment call
that would blow this bootstrap's ~90-minute appetite. Near-term substitute:
this task's own new tests
(`skill-frontmatter-lint.test.sh`, the enumeration fixtures) follow the
repo's existing `*.test.sh` pass/fail-assertion convention
(`release-metadata.test.sh`), which is the current rigor signal for
`scripts/` and remains so until the backlog task picks a coverage tool.

## Out of scope

- **`marketplace-verify.sh` L0-L2 CI wiring** (schema + install validation)
  — deferred. Requires the `claude` CLI and a real per-plugin install in CI;
  heavier than the current required job's ~7s design budget
  (`marketplace-parity.yml` comment), and audit found zero current drift it
  would catch that isn't already caught. Track as a separate backlog task if
  a schema-validity incident ever occurs.
- **Expanding `.githooks/pre-commit` to cover the new lints** — deferred.
  Pre-commit today is narrowly scoped to `e2e-pipeline/` by an explicit prior
  design choice; broadening it touches every contributor's local commit path
  and is a decision the captain should make explicitly, not a side effect of
  this bootstrap.
- **Diff-coverage tooling selection** — deferred to backlog; determination
  recorded above with reason.
- **Sanitize-check CI wiring** — untouched. It is a pre-publish/interactive
  tool by its own SKILL.md's design, not a general structural CI gate; no
  evidence found that it was ever intended to be one.

## Implementation dispatch sizing

**ONE worker session**, ~75-90 minutes, sized under the ~90-minute split
threshold. Two independent behaviors (AC-1 skill-frontmatter-lint;
AC-2 enumeration repair), each a complete RED→GREEN loop in the same
session per the repo's implementation-stage discipline (never tests in one
dispatch, code in the next), followed by the CLAUDE.md doc diff and the
`docs/dev/ledger.csv` bootstrap (mechanical, no RED/GREEN needed — a static
file). The pre-registered scope cut under "Appetite" (drop P1/AC-2 first)
applies if the session runs long; do not split into parallel worktree lanes
for two behaviors this small and this sequentially related (both land in
the same CI job).

## Stage Report: ideation

- DONE: Reverse-recovery audit against fresh origin/main with file:line evidence and five-state classification
  8-row table above; fetched `origin/main` fresh (`01bc8e3`), confirmed working-branch divergence, cross-checked branch-protection required-check identity live via `gh api repos/iamcxa/kc-claude-plugins/branches/main/protection`. 2 existing capabilities (rows 1/3) WORKING, 1 seam-level EXISTS_BROKEN (row 2), 1 manual STUB (row 4), 1 genuinely MISSING with multi-strategy proof of absence (row 5, and row 8 for diff-coverage).
- DONE: ACs are mechanically executable structural checks scoped to this repo with fail-closed semantics
  AC-1 through AC-4 above, each with Verified-by (real-CI-run probes, not local-only) and Falsified-by lines; a value baseline (1/3 → target 3/3 enforced categories) precedes them per the end-value AC requirement.
- DONE: Ledger bootstrap and ideation bookkeeping land together
  Header text confirmed byte-identical to `docs/dev/README.md`'s schema line and fully specified for implementation (see "Ledger bootstrap" — file creation deliberately deferred to implementation's worktree, not written here, because ideation has no worktree and the available checkout is on an unrelated diverged branch; see rationale in that section). Appetite + pre-registered scope cut, design determination (`trivial-pass`, reasoned), and doc diff (CLAUDE.md table, before/after) all recorded in the sections above.

### Summary

Audited the repo's existing structural-check surface against a freshly
fetched `origin/main` (not the locally-diverged working branch) and found
the task's Problem was already 1/3 solved: plugin-version-sync is a live,
GitHub-API-confirmed required CI check. Narrowed implementation to two
behaviors — repair a fail-open enumeration gap in the existing check, and
build the genuinely-missing skill-frontmatter lint — both wired into the
same already-required job so no branch-protection reconfiguration is
needed. Ledger bootstrap is fully specified here but its file write is
deferred to implementation's dedicated worktree, since ideation has none and
the current checkout sits on an unrelated branch. Diff-coverage tooling
selection is explicitly deferred to a backlog task with reasoning, not
decided silently.
