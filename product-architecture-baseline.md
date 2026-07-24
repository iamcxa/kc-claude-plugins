---
id: fdkcs3m8jp2wnxh8bfd1cgzq
title: PRODUCT.md + ARCHITECTURE.md baseline
status: validation
source: commission seed (lean SD workflow, 2026-07-24)
started: 2026-07-24T08:52:51Z
completed:
verdict:
score: 0.6
worktree: .worktrees/spacedock-ensign-product-architecture-baseline
issue:
pr:
design: trivial-pass
---

This repo has CLAUDE.md conventions but no PRODUCT.md or ARCHITECTURE.md,
and the workflow's doc-diff clause needs canonical docs to diff against.
Produce lightweight baselines describing the monorepo as it is: what each
plugin ships and for whom (PRODUCT), and the real structure — plugin layout,
marketplace publish flow, hooks/scripts surfaces, versioning scheme
(ARCHITECTURE). As-is only, no aspiration.

**Premise update (reverse-recovery audit, 2026-07-24, audited against fresh
`origin/main` @ 755cf96, current branch HEAD == origin/main, zero diff on
both files):** PRODUCT.md (64 lines) and ARCHITECTURE.md (99 lines) now
exist — landed by the unrelated kc-pr-flow agent-native review track
(536be3e "agent-native shadow review receipts (#48)", a0f50f4 "typed
interactive review lifecycle"), which used *this same workflow's* doc-diff
clause to seed the files as a side effect of documenting its own capability.
This task's premise ("no PRODUCT.md or ARCHITECTURE.md exist") has
collapsed. Classification below (per the three shapes named in the
dispatch) replaces greenfield authoring with gap-repair scope.

## Reverse-recovery audit

Layer: doc-content coverage, not code. Classified against origin/main.

- Both files are **WORKING** for the one capability they cover: the
  `## kc-pr-flow: Agent-native PR review` (PRODUCT.md) and
  `## kc-pr-flow: Agent-native review runtime` (ARCHITECTURE.md) sections.
  Spot-checked: `KC_PR_FLOW_REVIEW_TYPED`, `InteractiveCollationDecision`,
  `ShadowObservation`, `confirmed-blocker-evidence` all resolve to real
  artifacts in `kc-pr-flow/{README.md,CLAUDE.md,docs/review-runtime.md,
  reference/review-runtime.md,skills/kc-pr-review/SKILL.md,
  scripts/review-shadow.test.sh}`. No contradiction found — shape 3
  (docs contradict repo) is ruled out.
- Monorepo-wide coverage is **MISSING**: 5 of 6 marketplace plugins
  (`e2e-pipeline`, `kc-plugin-forge`, `kc-nightwatch`, `kc-hyperfocus`,
  `kc-team-ops` — confirmed via `.claude-plugin/marketplace.json`
  `plugins[].name`) have no PRODUCT.md entry. ARCHITECTURE.md has no
  section for repo layout, marketplace publish flow, hooks/scripts
  surfaces, or versioning scheme — the four surfaces the original seed
  named. Shape 1 (already-satisfied, close as-is) is ruled out: AC-1's
  own text requires monorepo-wide coverage, and 1/6 plugins is not that.
- **Verdict: shape 2 — gap-patch.** Extend the existing files with new
  top-level sections; the existing kc-pr-flow sections are untouched
  (regression-guarded by AC-3 below). Never a parallel rewrite.

## Scope check

Drafted from repo evidence; captain confirms/overrides at the gate —
dispatched async, no live scope Q&A this run. Small-scope reason: AC-1's
own wording plus the already-thorough per-plugin descriptions in
README.md leave little framing ambiguity.

- **Worse without this:** doc-diff clause in future tasks keeps
  diffing against a file that only speaks kc-pr-flow's language —
  every other plugin's behavior changes have no canonical baseline to
  diff against, so the clause silently degrades to a no-op for 5/6 of
  the repo.
- **Time budget:** small batch — target under 90 minutes, one sitting.
- **Cut first if forced:** drop the "Repository layout" prose paragraph
  in ARCHITECTURE.md before dropping the per-plugin PRODUCT.md catalog —
  the catalog is what the doc-diff clause actually needs; the layout
  paragraph is orientation, not a diffable contract surface.
- **Happily NOT doing:** decision-record-depth architecture entries
  (kc-pr-flow's D1-D7 style) for the other 5 plugins — none of them
  currently has a capability complex enough to warrant one, and forcing
  the format would be aspiration, not as-is.
- **Riskiest assumption:** that a one-paragraph-per-plugin PRODUCT.md
  entry is the right depth for "contributors who need to change a
  capability without rediscovering its purpose" — if a future task needs
  deeper per-plugin architecture, this baseline under-serves it and needs
  a second pass (see pre-mortem).

## Design determination

`trivial-pass` — docs-only change (PRODUCT.md, ARCHITECTURE.md); no UI,
API contract, schema, or visual surface affected.

## Proposed approach

Add two new sections to each file (details in Doc diff below), inserted
before the existing kc-pr-flow section so the monorepo-wide overview
reads first and the one deep-dive capability entry reads second:

- PRODUCT.md: `## Repository plugin catalog` — one outcome + audience
  line per marketplace plugin, sourced from README.md's existing
  per-plugin descriptions and each plugin's own CLAUDE.md, re-cast as
  durable outcome statements rather than marketing copy.
- ARCHITECTURE.md: `## Repository layout`, `## Marketplace publish flow`,
  `## Hooks and scripts surfaces`, `## Versioning scheme` — the four
  surfaces the original seed named, each citing the real script/workflow/
  config file that backs the claim.

No spike needed: the only "mechanism" this task exercises is grepping the
repo for the paths and identifiers named in the drafted prose, which was
done during this ideation pass (see file:line citations in Doc diff) —
proven by direct execution, not by assumption.

## Acceptance criteria

**AC-1 — Both files describe the repo as it is, monorepo-wide (not scoped
to one plugin).**
Verified by: every one of the 6 `marketplace.json` plugins has a
corresponding PRODUCT.md entry naming its outcome and audience, and
ARCHITECTURE.md names repo layout, marketplace publish flow, hooks/scripts
surfaces, and versioning scheme — each spot-checked against a real path or
file:line (e.g. `scripts/version-parity-check.sh`,
`.github/workflows/release-please.yml`, `<plugin>/hooks/hooks.json`).
Falsified by: a plugin listed in `marketplace.json` with no PRODUCT.md
entry, or a claim naming a path/behavior that doesn't exist in the repo.

**AC-2 — Monorepo-wide doc coverage moves from a known-bad baseline
toward complete, measurably.**
Verified by: coverage ratio (# plugins with a PRODUCT.md outcome entry) /
(# plugins in `marketplace.json`) reaches 6/6, up from today's 1/6
(kc-pr-flow only, `git show origin/main:PRODUCT.md`); the 4 named
ARCHITECTURE.md surfaces move from 0/4 to 4/4.
Falsified by: the ratio does not reach 6/6 or 4/4 at merge — and this
ratio is the regression signal for the future too: if a 7th plugin is
added to `marketplace.json` without a matching PRODUCT.md entry, the
ratio drops back below 1.0, which is the intended failure signal (this is
the AC that can move the wrong way after this task ships, not just at
merge time).

**AC-3 — The existing kc-pr-flow sections are unchanged (gap-patch, not
rewrite).**
Verified by: `git diff` on the applied change touches only new
`##`-level sections; zero lines inside the existing
`## kc-pr-flow: Agent-native PR review` (PRODUCT.md) or
`## kc-pr-flow: Agent-native review runtime` (ARCHITECTURE.md) sections
are added, removed, or edited.
Falsified by: any diff hunk that touches a line inside either existing
section.

## One-sentence pre-mortem

If this ships exactly per spec and still fails, the most likely cause is
a **hidden assumption**: that a shallow one-paragraph-per-plugin PRODUCT.md
entry serves contributors the same way kc-pr-flow's decision-record-depth
entry does — the two plugins most likely to outgrow that shallow depth
first are `e2e-pipeline` (compiler/runtime split, biggest surface) and
`kc-hyperfocus` (has its own `server/`, MCP surface); if either needs a
capability-level doc-diff before this baseline is revisited, the shallow
entry will look "satisfied" by AC-1/AC-2 while not actually serving that
future task.

## Test plan

Docs-only; no new automated check proposed (see Out of scope). Verification
is the spot-check grep-and-read pass demonstrated in this ideation stage,
repeated by validation against the merged doc content: for each
`marketplace.json` plugin name, `grep -n "^## " PRODUCT.md` finds a
matching heading or catalog line; for each of the 4 named ARCHITECTURE.md
surfaces, the cited path/file exists in the repo tree.

## Doc diff

**PRODUCT.md** — insert after line 3 (intro paragraph), before line 5
(`## kc-pr-flow: Agent-native PR review`):

```markdown
## Repository plugin catalog

This monorepo publishes six plugins through the `kc-claude-plugins`
marketplace (`.claude-plugin/marketplace.json`). Each entry states the
outcome the plugin exists to deliver and who it serves; full skill lists
live in each plugin's own `README.md`. `kc-pr-flow`'s agent-native review
runtime has its own deep-dive entry below this catalog.

- **`e2e-pipeline`** — Map, generate, verify, and run browser/CLI E2E flows
  without hand-maintained selectors, with an LLM-judgment fallback when
  compiled matching can't resolve a step. Serves teams testing a web app
  end-to-end who need both a fast CI-friendly compiled path and
  human-in-the-loop exploration.
- **`kc-plugin-forge`** — One command validates plugin structure, TDD-tests
  skills under pressure, audits `SKILL.md` frontmatter, and smoke-tests in
  an isolated profile before publish. Serves plugin authors in this
  monorepo who want automated quality assurance instead of manual review.
- **`kc-nightwatch`** — Autonomous nightly cycle that runs forge
  validation, harvests improvement signals from journal/Sentry/E2E/git,
  and proposes north-star-aligned changes. Serves maintainers who want
  continuous quality monitoring without manually triggering it.
- **`kc-hyperfocus`** — Detects context pressure, enforces session
  handoff/resume, and caches codebase insight in a local SQLite lake so
  agents don't re-explore from zero. Serves agents (and their operators)
  running long or multi-session work that needs durable cross-session
  context.
- **`kc-team-ops`** — EM triage with a strategic lens, project pulse
  updates, issue decomposition, and structured Linear management, plus an
  on-demand cross-model second opinion via Gemini/`agy`. Serves
  engineering managers running Linear-based triage and reporting.
- **`kc-pr-flow`** — End-to-end PR lifecycle (create → review → resolve →
  announce) with tiered multi-agent review. Serves contributors who want a
  one-command PR workflow with consistent review quality across model
  providers. Its agent-native review runtime is detailed in the dedicated
  entry below.
```

**ARCHITECTURE.md** — insert after line 3 (intro paragraph), before line 5
(`## kc-pr-flow: Agent-native review runtime`):

```markdown
## Repository layout

The repo is a monorepo of six independent Claude Code plugins at top level
(`e2e-pipeline/`, `kc-plugin-forge/`, `kc-nightwatch/`, `kc-hyperfocus/`,
`kc-team-ops/`, `kc-pr-flow/`), each with its own `skills/`, `agents/`, and
(where applicable) `hooks/` directories, plus a repo-level `scripts/`
directory and `.claude-plugin/marketplace.json` manifest. `docs/dev/` holds
the lean ship-flow-style task workflow (split-root state under
`docs/dev/.spacedock-state`) that governs how repo changes are proposed,
built, and verified.

## Marketplace publish flow

`.claude-plugin/marketplace.json` is the published catalog; each plugin
entry names its `source` path, `description`, `version`, and `keywords`.
`scripts/marketplace-verify.sh` validates marketplace schema plus plugin
installability (and optionally skill execution, `--smoke`) in an isolated
temp `HOME`. `scripts/post-install-smoke.sh` runs the full post-install
lifecycle (marketplace add → plugin install → MCP deps → smoke test) per
plugin. `.github/workflows/marketplace-parity.yml` runs on every PR (no
`paths:` filter, so it stays a valid required check) and enforces version
parity plus skill-frontmatter well-formedness before merge.

## Hooks and scripts surfaces

Four plugins ship a `hooks/hooks.json`: `e2e-pipeline`, `kc-plugin-forge`,
`kc-hyperfocus`, `kc-pr-flow`. `kc-nightwatch` and `kc-team-ops` currently
ship no hooks. `.githooks/pre-commit` is an opt-in local pre-commit hook
(`git config core.hooksPath .githooks`) that runs `e2e-pipeline`'s biome
lint + tests only when `e2e-pipeline/` files are staged. Repo-level
`scripts/` holds cross-plugin checks run in CI: `marketplace-verify.sh`,
`post-install-smoke.sh`, `release-metadata.test.sh`,
`release-please-config-check.sh`, `skill-frontmatter-lint.sh` (+ its
test), `version-parity-check.sh`.

## Versioning scheme

Each plugin is an independent release-please component
(`release-please-config.json`, manifest mode, `tag-separator: "-"`,
`include-component-in-tag: true`) tracked in
`.release-please-manifest.json`. On push to `main`,
`.github/workflows/release-please.yml` maintains a Release PR that bumps
the changed plugin(s) across `.claude-plugin/plugin.json`,
`.codex-plugin/plugin.json` (only `e2e-pipeline`, `kc-plugin-forge`,
`kc-pr-flow` ship a Codex manifest), and the matching `marketplace.json`
array entry; merge cuts a `<plugin>-vX.Y.Z` tag, GitHub Release, and
per-plugin `CHANGELOG.md`. `scripts/version-parity-check.sh` is the
machine-enforced backstop asserting all tracked version sources agree.
```

## Out of scope

- Decision-record-depth ARCHITECTURE.md entries (kc-pr-flow's D1-D7 style)
  for the other 5 plugins — no plugin currently has a capability complex
  enough to warrant one; adding one would be aspiration, not as-is.
- A new automated CI check enforcing PRODUCT.md/ARCHITECTURE.md plugin
  coverage — the existing `marketplace-parity.yml` checks version
  consistency, not doc-content coverage, and a new mechanism for a
  one-time backfill would be over-engineering for this task's small
  appetite. Future doc-diff clauses at the ideation gate are the intended
  enforcement point, not a script.
- Rewriting or restructuring the existing kc-pr-flow sections (AC-3 guards
  against this).

## Appetite and implementation dispatch sizing

Small batch: under 90 minutes, one sitting. Sized as **ONE** implementation
worker session — this is a single coherent editing behavior (insert 2 new
section blocks into 2 files per the Doc diff above) with no independent
behavior threads and no code path to test; splitting would only pay
cold-start cost twice for no wall-clock benefit.

## Stage Report: ideation

- DONE: Reverse-recovery audit runs against fresh origin/main, not the workspace branch — classify each against AC-1 and scope as gap-repair, not greenfield.
  Fetched `origin/main` (755cf96); confirmed branch HEAD == origin/main with zero diff on both files (`git diff origin/main -- PRODUCT.md ARCHITECTURE.md` empty). Classified: existing content WORKING for kc-pr-flow only (spot-checked 4 identifiers against 6 real kc-pr-flow files), monorepo-wide coverage MISSING for 5/6 plugins and all 4 named surfaces. Verdict shape 2 (gap-patch) recorded in "Reverse-recovery audit" section; shapes 1 and 3 explicitly ruled out with evidence.
- DONE: AC set carries falsifiable Verified-by / Falsified-by clauses plus a design determination, and at least one AC measures end value against a baseline that can move the wrong way.
  AC-1/AC-2/AC-3 each carry Verified-by/Falsified-by; AC-2 states the current 1/6 and 0/4 baselines and names the regression condition (a future plugin added without a matching entry) as the same measure moving the wrong way. Design determination recorded as `trivial-pass` (docs-only, no UI/contract/schema surface) in its own section — frontmatter `design:` field left untouched per ensign rule; FO/binary owns setting it.
- DONE: Appetite, pre-registered cut, and implementation dispatch sizing recorded in the task body.
  "Scope check" names the pre-registered cut (drop ARCHITECTURE.md's layout paragraph before the PRODUCT.md catalog); "Appetite and implementation dispatch sizing" records small-batch/under-90-minutes and ONE worker session with the splitting rationale.

### Summary

Premise collapsed as the dispatch anticipated: PRODUCT.md/ARCHITECTURE.md already exist on origin/main, scoped entirely to kc-pr-flow's agent-native review capability (verified via spot-check, no contradictions found). Reclassified the task from greenfield authoring to a gap-patch: added a Reverse-recovery audit, Scope check, AC-1/2/3 (with a baseline-based end-value AC), a one-sentence pre-mortem, and a concrete before/after Doc diff extending both files with monorepo-wide coverage (6-plugin PRODUCT.md catalog; repo layout, marketplace publish, hooks/scripts, and versioning sections in ARCHITECTURE.md) — all citing real file:line evidence gathered during this pass. Sized for one implementation worker session, small-batch appetite.

## Stage Report: implementation

- DONE: Apply the ideation-approved doc diff from the entity body: PRODUCT.md plugin catalog reaches 6/6 marketplace plugins and ARCHITECTURE.md gains the 4 named surfaces, every claim citing a real path or file:line that exists in the tree (AC-1, AC-2).
  Applied the exact Doc diff blocks verbatim into the worktree at `.worktrees/spacedock-ensign-product-architecture-baseline/{PRODUCT.md,ARCHITECTURE.md}`, committed as `f28bdd2` on `spacedock-ensign/product-architecture-baseline`. Before writing, re-verified every cited path/file against the tree (not just trusted the ideation pass): all 6 `marketplace.json` plugin dirs exist; hooks.json present in exactly `e2e-pipeline`, `kc-plugin-forge`, `kc-hyperfocus`, `kc-pr-flow` (absent in `kc-nightwatch`, `kc-team-ops`, matching the claim); `scripts/{version-parity-check,marketplace-verify,post-install-smoke,release-metadata.test,release-please-config-check,skill-frontmatter-lint,skill-frontmatter-lint.test}.sh` all present; `.github/workflows/{release-please,marketplace-parity}.yml` present, and `marketplace-parity.yml`'s header comment confirms "Runs on EVERY pull request — intentionally no `paths:` filter"; `release-please-config.json` has `include-component-in-tag: true` and `tag-separator: "-"`; `.codex-plugin/plugin.json` present only in `e2e-pipeline`, `kc-plugin-forge`, `kc-pr-flow` (matching the claim); `.githooks/pre-commit` greps staged paths for `^e2e-pipeline/` before running biome lint. Post-apply: `grep -n "^## " PRODUCT.md` shows 2 headings (catalog + kc-pr-flow), and all 6 plugin names (`` `e2e-pipeline` ``, `` `kc-plugin-forge` ``, `` `kc-nightwatch` ``, `` `kc-hyperfocus` ``, `` `kc-team-ops` ``, `` `kc-pr-flow` ``) are found in PRODUCT.md; `grep -n "^## " ARCHITECTURE.md` shows the 4 new surfaces (Repository layout, Marketplace publish flow, Hooks and scripts surfaces, Versioning scheme) plus the existing kc-pr-flow heading — 4/4 and 6/6 reached.
- DONE: Existing kc-pr-flow sections untouched: the applied diff adds new `##`-level sections only — zero lines inside the two existing kc-pr-flow sections are added, removed, or edited; verify with `git diff` before committing (AC-3).
  `git diff --stat` on the commit shows only insertions (`ARCHITECTURE.md | 49 +++...`, `PRODUCT.md | 36 +++...`, `2 files changed, 85 insertions(+)`, 0 deletions). `git diff | grep '^-'` (excluding the `---` file headers) produced zero lines. Additionally diffed each file's kc-pr-flow section body byte-for-byte against `origin/main` (`diff <(git show origin/main:PRODUCT.md | sed -n '5,$p') <(sed -n '41,$p' PRODUCT.md)` and the ARCHITECTURE.md equivalent from line 54) — both report identical, confirming the pre-existing sections are untouched beyond shifting down by the inserted line count.
- DONE: Appetite is <90 minutes: if about to exceed it, apply the pre-registered cut; stage report is self-contained for a fresh validator (what was produced, where, how to re-run the spot-check).
  Completed well inside the 90-minute appetite (verification-heavy but mechanical single-session edit); the pre-registered cut (dropping ARCHITECTURE.md's "Repository layout" paragraph) was not needed — full diff applied as specified. Re-run instructions for a fresh validator: `cd` to the repo root (or this worktree), run `grep -n "^## " PRODUCT.md ARCHITECTURE.md` to see all headings, `git diff origin/main -- PRODUCT.md ARCHITECTURE.md` to see the full additive diff, and `git diff --stat origin/main -- PRODUCT.md ARCHITECTURE.md` to confirm 0 deletions across both files.

### Summary

Applied the ideation-approved Doc diff verbatim to both files after independently re-verifying every cited path/file against the actual tree (all citations held — no drift since ideation). PRODUCT.md gained a "Repository plugin catalog" section (6/6 marketplace plugins); ARCHITECTURE.md gained 4 new sections (Repository layout, Marketplace publish flow, Hooks and scripts surfaces, Versioning scheme — 4/4 named surfaces). Confirmed via `git diff --stat` (85 insertions, 0 deletions across both files) and a byte-for-byte diff of each kc-pr-flow section against `origin/main` that the existing kc-pr-flow content is fully untouched (AC-3). Committed as `f28bdd2` on branch `spacedock-ensign/product-architecture-baseline` in the worktree; not pushed (per ensign scope — CODE branch push/PR is a later-stage concern).

## Stage Report: validation

- DONE: Reproduce each AC's Verified-by first-hand in the worktree (never the implementer's self-report): AC-1/AC-2 — every marketplace.json plugin has a PRODUCT.md catalog entry (6/6) and all 4 named ARCHITECTURE.md surfaces exist (4/4), spot-checking each claim's cited path/file against the real tree; AC-3 — git diff against origin/main shows 0 deletions and the two existing kc-pr-flow section bodies are byte-identical to origin/main.
  PASS on all three, reproduced fresh (not implementer self-report). `grep -n "^## " PRODUCT.md ARCHITECTURE.md` in the worktree shows all 6 `marketplace.json` plugin names (`e2e-pipeline`, `kc-plugin-forge`, `kc-nightwatch`, `kc-hyperfocus`, `kc-team-ops`, `kc-pr-flow`) present in PRODUCT.md, and all 4 named surfaces as ARCHITECTURE.md headings. `git diff --stat origin/main -- PRODUCT.md ARCHITECTURE.md` = "2 files changed, 85 insertions(+)" — 0 deletions, confirmed with `git diff | grep '^-'` (only `---` file headers, no content deletions). `diff <(git show origin/main:PRODUCT.md | sed -n '5,$p') <(sed -n '41,$p' PRODUCT.md)` and the ARCHITECTURE.md equivalent (origin line 5 vs current line 54) both report zero differences — the two kc-pr-flow sections are byte-identical.
- DONE: As-is accuracy sweep: the new prose makes factual claims about scripts, workflows, hooks, and versioning — verify a sample of the load-bearing ones against the actual files (e.g. marketplace-parity runs on every PR with no paths filter; release-please tag scheme; which plugins carry hooks.json / .codex-plugin) and name any claim that overstates or drifts from what the file actually does.
  All named examples confirmed: `marketplace-parity.yml`'s own header comment states "Runs on EVERY pull request — intentionally no `paths:` filter"; `release-please-config.json` has `tag-separator: "-"` and `include-component-in-tag: true`; `hooks.json` present in exactly `e2e-pipeline`/`kc-plugin-forge`/`kc-hyperfocus`/`kc-pr-flow`, absent in `kc-nightwatch`/`kc-team-ops`; `.codex-plugin/plugin.json` present only in `e2e-pipeline`/`kc-plugin-forge`/`kc-pr-flow`. Extended the sweep to PRODUCT.md's plugin-outcome prose: `kc-hyperfocus`'s "local SQLite lake" claim confirmed at `kc-hyperfocus/README.md:204` ("Database: SQLite via `bun:sqlite`... FTS5"); `e2e-pipeline`'s "compiled path + human-in-the-loop" claim confirmed via `e2e-pipeline/docs/architecture.md`'s pipeline diagram (FLOW feeds both COMPILE→TEST and TEST directly, the latter resolved by the LLM-driven `e2e-test-runner` agent, not a compiled script). No overstated or drifted claim found among the citations checked.
- DONE: Converge by naming residuals: report PASS/FAIL per AC with actual command output; findings that are not fixable defects of this diff are named residuals with an acceptance reason, not new rounds.
  Ran an independent cross-model review per the validation stage-def's cross-model gate. `codex review` hit its usage-credit limit ("You've hit your usage limit... try again at Jul 29th, 2026"); fell back to `agy`/Gemini via `kc-team-ops:gemini`. Gemini returned `MODEL_GATE=PASS` with two `[P2]` findings, both verified against the tree (not fabricated): (1) ARCHITECTURE.md's Versioning scheme sentence says `.claude-plugin/plugin.json` without an explicit `<plugin>/` prefix — there is no root-level `plugin.json` (only per-plugin ones), so while "the changed plugin(s) across" disambiguates it in context, a literal reading could mislead; (2) ARCHITECTURE.md's Repository layout sentence claims every plugin has its own `agents/` dir, but `kc-plugin-forge` has no `agents/` directory (confirmed: only `.claude-plugin/`, `.codex-plugin/`, `docs/`, `hooks/`, `reference/`, `skills/`, `smoke-tests/`). Named as residuals, not fixed: both live in the "Repository layout" paragraph the ideation stage itself flagged as "orientation, not a diffable contract surface" and the pre-registered cut-first item — neither affects AC-1/AC-2/AC-3's pass/fail (no plugin missing a catalog entry, no surface missing, no kc-pr-flow line touched). Acceptance reason: cosmetic precision gap in non-contract orientation prose, below the bar the task's own scope check set for this paragraph.

### Summary

All three ACs PASS with evidence reproduced first-hand in the worktree: 6/6 PRODUCT.md plugin entries, 4/4 ARCHITECTURE.md surfaces, 0 deletions and byte-identical kc-pr-flow sections vs `origin/main`. An accuracy sweep across the checklist's named script/workflow/hook/versioning claims, extended to a sample of PRODUCT.md's plugin-outcome prose, found no overstated or fabricated claim. Cross-model review (agy/Gemini, since codex was out of usage credits) passed with two named, non-blocking P2 residuals confined to the lower-priority "Repository layout" paragraph — both real but minor, and accepted rather than routed to another round given they don't touch any AC's pass/fail condition. Verdict: PASS — no route-back to implementation.
