---
commissioned-by: spacedock@0.10.1
entry-point: ship-flow:ship-shape
entity-type: feature
entity-label: feature
entity-label-plural: features
id-style: slug
stages:
  defaults:
    worktree: true
    concurrency: 2
  states:
    - name: draft
      initial: true
      worktree: false
    - name: shape
      worktree: false
      gate: true
      manual: true
      skill: ship-flow:ship-shape
      model: opus
    - name: design
      worktree: true
      gate: true
      manual: conditional
      skip-when: "!affects_ui && !domain"
      skill: ship-flow:ship-design
      model: opus
    - name: plan
      skill: ship-flow:ship-plan
      model: sonnet
    - name: execute
      skill: ship-flow:ship-execute
      model: sonnet
    - name: verify
      worktree: false
      skill: ship-flow:ship-verify
      model: sonnet
      dispatch: debate-driven
      feedback-to: execute
    - name: ship
      worktree: false
      skill: ship-flow:ship-review
      model: sonnet
    - name: done
      terminal: true
      worktree: false
  transitions:
---

# Ship-Flow Pipeline

Ship-focused pipeline for spacedock-ui. SHAPE once with captain, then agents autonomously plan → execute → ship. Each feature goes through one human gate (shape) before autonomous delivery.

> **Motto — Bad news early, no surprises.**
> Blockers, violated assumptions, scope creep, ID collisions, parallel-session races, or any unexpected state surface to captain **at discover-time** — not at stage-boundary, not buried in a report, not revealed only at merge. Autonomous delivery between stages is cheap; silent surprises at merge time are expensive. Apply across every stage (shape / plan / execute / verify / review / ship-final). If a fresh-context subagent finds the captain's hand-off was stale, say so before proceeding. If `--next-id` returns a value another session just claimed, surface it before committing. If a PR hits CONFLICTING post-create, stop and report before auto-resolving a non-trivial case. Source: CL/Recce culture (global CLAUDE.md Escalation Mantra).

> **Always Be Coaching (ABC)**
> Every stage agent treats each cross-review finding and every blocker surfaced to the captain as a teaching moment — not just a gate. When the cross-review gate emits VETO or PROMPT_CAPTAIN, the reviewer includes a brief coaching note: *why* the finding matters (which principle, which past failure mode, what future harm the rule prevents). When an agent surfaces bad news early, it names the invariant it's enforcing so the captain builds model over time. ABC does NOT mean verbose — one sentence per finding is enough. ABC is enforced by INVARIANTS.md Principle 6 Rule C audit (7th factor "Render Fidelity / Coaching Hygiene" added #106 T6.4).

## Ship-Flow 2.0 (entity #085)

**Thesis**: ship-flow is a thin auditable harness around claude 4.7's natural capabilities — not a procedural teacher. Human-in-loop at shape; later stages agent-auditable.

### 3 user-invocable entries

| Command | Input | Output artifact | Human in loop? |
|---|---|---|---|
| `/shape <concept \| issue \| vague>` | directive or entity id | `<entity-folder>/spec.md` | YES — confirm / refine / reject gate |
| `/ship <entity-id \| requirement>` | entity-id OR concrete req (vague → routes to `/shape`) | `plan.md` → `execute.md` → `verify.md` → `review.md` → `ship.md` + code | NO after shape |
| `/verify <entity-id \| requirement>` | entity-id or req (standalone escape-hatch) | `verify.md` | NO unless BLOCKING |
| `/add-todos <idea>` | free text | todo entry | NO |

### Entity folder layout (default for new pitches)

```
docs/ship-flow/<id>-<slug>/
  README.md     # entity metadata + links to stage artifacts
  spec.md       # /shape output — problem, appetite, children, assumptions, DAG
  plan.md       # ship-plan output — task breakdown, verification spec, DC
  execute.md    # ship-execute output — commits, files modified, UAT evidence
  verify.md     # ship-verify output — quality gate, review, UAT, verdict
  review.md     # ship-review output — PR body draft, ROADMAP/PRODUCT sync
  ship.md       # final shipping output — PR link, deploy, merge status (written by /ship)
```

Existing flat entities (`docs/ship-flow/<slug>.md`) still supported (non-breaking).

### Skill count (post-Wave 5b, post-#113.2)

7 stage + 5 utility = 12 total. Split-counted per Principle 2 (stage cap 7/7 — full).

- **Stage skills** (≤7 cap, user-invocable): `ship-shape`, `ship`, `ship-plan`, `ship-execute`, `ship-verify`, `ship-review`
- **Utility skills** (uncapped): `add-todos`, `ship-onboard`, `ship-runtime-detect`

Removed: `ship-sharp` (deprecated alias, Wave 5b T4).

### 3-Layer architecture (Principle 6 Rule B)

- **Layer A** (delegation): superpowers atomic skills (`brainstorming`, `writing-plans`, `subagent-driven-development`, `writing-skills`) + e2e-pipeline + pr-review-toolkit. Stage skills delegate philosophy (TDD order / HARD-GATE Q-loop / dispatch protocol) to Layer A.
- **Layer B** (ship-flow augmentation): Shape Up methodology, Musk decomposition, cross-review gates, canonical doc sync — the unique value of ship-flow.
- **Layer C** (canonical primitives): `lib/*.sh` (extract-section, patch-map, write-stage-artifact, shape-confirm, check-invariants) + `entity-body-schema.yaml`.

Exception clause (Principle 6 Rule B): ship-shape Mode A autonomous proposer owns flow when Layer A philosophy conflicts with stage contract. Exceptions documented in-file with rationale.

### Named-teammate-per-pitch (Principle 6 Rule A)

Default team per pitch:
- `planner` (opus) — shape → plan → review
- `executer` (sonnet) — execute
- `verifier` (opus/sonnet per pitch size) — verify

Stage transitions within a pitch use SendMessage to named teammate (~10× faster than fresh dispatch). Fresh subagent reserved for adversarial review / cross-teammate gate / captain request / clearly separate domain.

### Cross-review gate at every stage transition (Principle 6 Rule C)

5-factor rubric (feasibility / executable scope / quality / DC adequacy / canonical sync) by cross-teammate counterpart. Verdict: PROCEED / VETO (max 2 loops) / PROMPT_CAPTAIN. Reviewer fallback: cross-teammate → fresh sonnet → fresh opus when `appetite: big-batch`.

### 2.0 Changelog (entity #085)

| Wave | Scope | Commits |
|---|---|---|
| W1 | #085 body + ship-shape trim baseline | `df348e38` (trim 426→232) · `42015cb4` (body) |
| W2 | `/shape` 2.0 — spec.md + Mode A/B/C + cross-review | `4c4fb830` |
| Q-patch | Captain Q-answers + #085 body Mode C sync | `59874aa2` |
| W3 | `/ship` 2.0 — pipeline entry + per-stage .md + vague→shape routing | `ac605212` |
| W4 | `/verify` 2.0 — dual invocation + ROI + agent-browser e2e | `5b108e41` |
| W5a | Internals trim — ship-plan / ship-execute / ship-review | `a6c4cc11` · `245a943c` · `a8c3e7ab` |
| W5b | Primitives — write-stage-artifact.sh / shape-confirm.sh --layout=folder / check-invariants split / ship-sharp removal | `acd73545` · `4f04341a` · `d51620e4` · `0b3fcc1a` |
| W6 | INVARIANTS + README + #085 body + ship-review sizing | (this commit et al) |

See `plugins/ship-flow/INVARIANTS.md` for Principle 2 / 6 detail and `docs/ship-flow/ship-shape-v2-implementation.md` for the #085 design record.

---

## Quick Start

### New repo (first time)
```
/ship-flow:ship-onboard          # Scans codebase, generates PRODUCT.md + ROADMAP.md
/plugin install designer-skills@julianoczkowski  # Design-flow + design-review skills (required for ship-design stage)
```

### Ship a feature
```
1. Create entity file:           bash plugins/ship-flow/bin/ship-capture.sh "<desc>"
                                 # or manually: docs/ship-flow/{slug}.md (status: draft)
2. /ship-flow:ship-shape {slug}  # Captain defines problem, done criteria, size → only human gate
3. FO auto-dispatches:           plan → execute → verify → ship → done (UI entities: captain smoke test at verify)
4. PR created automatically      # Reviewer sees full UAT results table with reproducible commands
```

### PR reviewer requests changes
```
/ship-flow:ship-execute {slug}   # Handles both fresh execute and PR-feedback re-entry (auto-detected via pr_feedback_round)
FO auto-re-dispatches:               execute → verify → ship → new PR
```

### Full pipeline
```
draft → shape (captain) → plan → execute → verify → ship → done
                ↑                    ↑         |  ↓
                |                    └─────────┘  captain smoke test (UI entities)
                |
                └── ship-execute Step 0 (PR reviewer → re-entry via pr_feedback_round)
```

## UAT Pipeline

UAT (User Acceptance Testing) is not a single stage — it's a thread running through the entire pipeline:

```
User Stories (shape)
  → User Journey (shape Step 2.8) — typed steps with boundary/risk
    → Done Criteria (shape Step 4) — typed DC derived from journey (cli/api/ui/skill/e2e)
      → Verification Spec (plan Step 3.5) — exact procedures per type
        → AC Verification 1st pass (execute Step 5.1) — run by type
          → UAT 2nd pass (verify Step 4) — independent re-run
            → PR body (ship Step 2) — table with procedures for reviewer reproduction
```

### Done Criteria Types

| Type | What it verifies | How it's verified | PR reviewer reproduction |
|------|-----------------|-------------------|------------------------|
| `cli` | Command output | Bash: run command, check exit code + output | Copy-paste command |
| `api` | Endpoint behavior | Bash: curl with expected status/body | Copy-paste curl |
| `ui` | Page content | curl route + grep content | Open browser or curl |
| `skill` | Skill behavior | Skill() invoke + check output | Run in Claude Code |
| `e2e` | Full user flow | e2e-pipeline flow YAML | Watch screenshot/video, or walk through manually |

### PR Feedback Loop

When a PR reviewer requests changes:

1. Captain runs `/ship-flow:ship-execute {slug}` (pr-feedback mode auto-detects)
2. Skill reads PR review comments via `gh pr view --comments`
3. Maps each comment to a Done Criterion (DC-1, DC-2, ...)
4. Classifies: assertion-fail → execute, architecture → plan, nit → log only
5. Rolls back entity status, closes PR
6. FO re-dispatches → fix → verify → new PR
7. Circuit breaker: 3 feedback rounds without approval → escalate to captain

## File Naming

Each feature is a markdown file named `{slug}.md` — lowercase, hyphens, no spaces. Example: `spacebridge-session-zombie-cleanup.md`.

## Schema

Every feature file has YAML frontmatter. Fields are documented below; see **Feature Template** for a copy-paste starter.

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Optional legacy identifier; slug is the effective entity ID because `id-style: slug` |
| `title` | string | Human-readable feature name |
| `status` | enum | One of: draft, shape, plan, execute, verify, ship, done |
| `source` | string | Where this feature came from |
| `started` | ISO 8601 | When active work began |
| `completed` | ISO 8601 | When the feature reached terminal status |
| `verdict` | enum | PASSED or REJECTED — set at ship stage |
| `priority` | enum | Captain priority: P0 (drop everything), P1 (this sprint), P2 (next sprint), P3 (backlog) |
| `score` | number | Sharp scoring gate objective score, 0.0–1.0 (computed, different from priority) |
| `worktree` | string | Worktree path while a dispatched agent is active, empty otherwise |
| `issue` | string | GitHub issue reference (e.g., `#42`) |
| `pr` | string | GitHub PR reference (e.g., `#57`) |
| `parent` | string | Epic/parent entity ID (e.g., `"003"`) — creates hierarchy for DAG view |
| `depends-on` | list | Entity IDs this entity depends on (e.g., `["004", "005"]`) — DAG edges. FO will not dispatch this entity until all dependencies reach `done` |
| `tracker` | string | Issue tracker provider: `gh` (GitHub) or `linear` (Linear). Determines how `issue` field is interpreted |
| `external_id` | string | External tracker ID (e.g., `PROJ-123` for Linear, `owner/repo#42` for cross-repo GitHub). Used alongside `issue` for full traceability |
| `token_budget` | number | Estimated cost in USD, set at shape (from size triage) |
| `token_actual` | number | Actual cost in USD, accumulated by FO across all stages |
| `entity_type` | enum | `entity` (default) or `epic`. Epic entities have `status: epic`, are skipped by FO `--next`, and contain child entities that flow through the pipeline independently |
| `children` | list | Child entity slugs — set by ship-shape epic mode. e.g., `["auth-api", "auth-ui"]` |

### Section Tags

Each section in the entity body can be wrapped with HTML comment tags for surgical extraction without full-file parsing:

```markdown
<!-- section:{tag} -->
## Section Header
content
<!-- /section:{tag} -->
```

Tags are invisible in rendered markdown (GitHub, Claude Design, dashboard). They enable:
- `bash plugins/ship-flow/lib/extract-section.sh {entity-file} {tag}` — extract any section by name
- Layer filtering: `layer: decision` (problem/journey/criteria) vs `layer: implementation` (plan/execute/verify/ship artifacts)
- Future: FO surgical reads, dashboard incremental rendering, spec-of-spec `implements:` traceability

Tag names and layer values are defined in `references/entity-body-schema.yaml` → `section_tag` field per subsection.

**Skills write tags** when creating new entity sections. **Legacy entities** (no tags) use the H2 boundary fallback in `plugins/ship-flow/lib/extract-section.sh` automatically — no migration needed.

**Tag naming convention:** kebab-case matching the section header with stage prefix for disambiguation (e.g., `verify-verdict` not just `verdict`, `ship-verdict` not just `verdict`).

### Hierarchy & Dependencies

Entities can form a tree (via `parent`) and a DAG (via `depends-on`):

```
Epic: "003" (parent)
  ├── "004" (child, depends-on: [])
  ├── "005" (child, depends-on: ["004"])
  └── "006" (child, depends-on: ["004", "005"])
```

**Rules:**
- `parent` creates a grouping relationship (epic contains children). An epic entity can have status `draft` while its children are in-flight.
- `depends-on` creates a sequencing constraint. FO will not advance a blocked entity past `draft` until all dependencies reach `done`.
- Circular dependency detection: at shape time, if adding a `depends-on` edge would create a cycle, reject and notify captain.
- An entity can have `parent` without `depends-on` (grouped but independent) or `depends-on` without `parent` (sequenced but flat).

### Epic Entities

An **epic** entity is a directive too large for a single pipeline pass. Ship-shape detects this when size triage exceeds L (scope > 15 files or 5+ directories). Epic mode decomposes the directive into vertical slice child entities.

**Lifecycle:**
1. Ship-shape epic mode runs architecture research, proposes vertical decomposition into 3-5 children
2. Captain confirms decomposition
3. Ship-shape auto-creates child entity files with `parent:` and `depends-on:` frontmatter
4. Ship-shape writes `## Epic Context` to the epic entity with ADRs, Cross-Entity Contracts, decomposition table, and shared research
5. Epic entity `status` is set to `epic` — FO `--next` skips it permanently
6. Children flow through the pipeline independently (shape → plan → execute → verify → ship)
7. Each child's shape stage reads the parent's `## Epic Context` to inherit decisions and contracts

**FO routing:** `status: epic` is not in `stage_by_name` → `print_next_table()` skips the entity unconditionally (status script L482-483).

**Child entity frontmatter example:**
```yaml
parent: "040"          # epic entity id
depends-on: ["041"]    # other children this depends on
entity_type: entity    # default — children are normal entities
```

### Issue Tracker Binding

The `tracker` field determines how issue references are interpreted:

| `tracker` | `issue` format | `external_id` format | Example |
|-----------|---------------|---------------------|---------|
| `gh` (default) | `#42` or `owner/repo#42` | same as `issue` | `issue: "#42"` |
| `linear` | `PROJ-123` | Linear issue ID | `issue: "PROJ-123", external_id: "PROJ-123"` |

When `tracker` is absent, default to `gh`. The `pr-merge` mod reads `tracker` to format the PR body correctly:
- `gh`: `Closes #42`
- `linear`: `Fixes PROJ-123` (Linear auto-close syntax)

### View Support

Entity frontmatter supports three view modes (UI renders these from the same data):

| View | Data source | What it shows |
|------|-------------|---------------|
| **Table** (default) | All frontmatter fields | Sortable, filterable rows |
| **Kanban** | `status` field as columns | Entities as cards in stage columns (draft / shape / plan / execute / verify / ship / done) |
| **DAG** | `depends-on` + `parent` fields | Entities as nodes, dependency edges, color = status. Epics shown as containing groups |

### Priority

Two distinct priority mechanisms — don't conflate them:

| Field | Set by | When | Purpose |
|-------|--------|------|---------|
| `priority` | Captain | At draft or shape | Subjective urgency — "how soon do I want this?" |
| `score` | Shape scoring gate | At shape Step 5 | Objective quality — "how well-defined and feasible is this?" |

**Priority levels:**

| Priority | Meaning | ROADMAP mapping | FO behavior |
|----------|---------|----------------|-------------|
| **P0** | Drop everything — critical bug, blocker, security | Now (top) | FO dispatches immediately, preempts P1 work |
| **P1** | This sprint — committed, actively working | Now | Normal dispatch order |
| **P2** | Next sprint — shaped, ready when Now clears | Next | Queued, dispatched when P0/P1 clear |
| **P3** | Backlog — idea with potential, not yet shaped | Later | Not dispatched until promoted |

Captain sets priority at draft (initial gut) or shape (after Musk audit). FO uses priority for dispatch ordering when multiple entities are ready.

## Core Principles

### Vertical Slice Requirement

**Entities are always vertical slices.** Each entity is an independently deliverable and testable E2E journey — never a horizontal layer.

| Vertical slice (correct) | Horizontal layer (wrong) |
|--------------------------|--------------------------|
| "User can register with email + password (form → API → DB → redirect)" | "All authentication API routes" |
| "Captain can view entity detail with comment panel" | "All UI components for commenting" |
| "Ship-shape writes Epic Context on decomposition" | "All schema YAML changes" |

A vertical slice has:
- A **clear entry point** (what the user/system does to start)
- **Crosses all required layers** (UI, API, storage — whatever the journey needs)
- **An observable outcome** the captain can verify without knowing implementation internals

When a directive is too large for one entity → use epic decomposition (ship-shape epic mode), not horizontal splitting.

## Stages

### `draft`

Captain captures an idea or bug. The feature stays here until the captain is ready to shape it. Advance to shape manually.

- **Inputs:** Captain's initial description in the entity body
- **Outputs:** Clear problem statement and initial context sufficient for shaping
- **Good:** Specific, actionable description with reproduction steps (for bugs) or user story (for features)
- **Bad:** Vague one-liners with no context; mixing multiple unrelated issues in one entity

### `shape`

Captain-facing shaping stage. Reads ROADMAP.md context, runs a Musk-style audit (fastest path? purpose? what if we don't build this?), triages size (S/M/L), and scores. This is the only human gate in the pipeline — captain approves before autonomous work begins.

- **Inputs:** Entity body from draft, ROADMAP.md for project context
- **Outputs:** Shaped problem statement, size classification (S/M/L), acceptance criteria, scoring gate verdict
- **Good:** Ruthlessly scoped — the smallest change that solves the real problem; clear acceptance criteria that agents can verify
- **Bad:** Gold-plating scope; accepting the problem framing without challenging assumptions; skipping the "what if we don't?" question

### `plan`

Agent-autonomous planning. Size-adaptive research (S=skip, M=targeted, L=deep), plan writing with task breakdown and verification commands, self-review loop up to 3 iterations.

- **Inputs:** Shaped entity with acceptance criteria from shape stage
- **Outputs:** PLAN section in entity body with ordered tasks, file targets, verification commands, and research findings
- **Good:** Each task has concrete file paths, a verification command, and clear done-criteria; research findings cite file:line evidence
- **Bad:** Tasks that say "implement the feature" without specifics; missing verification commands; research that restates the problem instead of investigating the codebase

### `execute`

Agent-autonomous execution. Dispatches one ensign per task from the plan, runs quality checks per task (build + test + typecheck), review loop for issues found. Non-blocking issues auto-create new draft entities.

- **Inputs:** PLAN section from plan stage
- **Outputs:** Implemented code changes in worktree, quality check results per task, any auto-created entities for discovered issues
- **Good:** Each task committed separately with passing quality checks; discovered issues tracked as new entities rather than scope-creep fixes
- **Bad:** Committing broken code; silently fixing unrelated issues in the same worktree; skipping quality checks

### `verify`

**Load skill:** Invoke `Skill("ship-flow:ship-verify")` before starting stage work.

Agent gate (not captain gate — FO auto-resolves from verdict). FO dispatches haiku review agents FIRST, then dispatches verify ensign (sonnet) to integrate findings.

**FO pre-dispatch (before verify ensign):** Dispatch these haiku review agents in parallel. Each reads the execute diff and writes raw findings to the entity file under `## Haiku Review`. Canonical detection logic lives in `ship-verify/SKILL.md` Step 3.1 — this table summarizes:

**Hard skip:** if diff contains only non-source files (`*.md`, `*.yaml`, `*.json`, `*.toml`, etc. — no `.ts`/`.tsx`/`.py`/etc.), skip ALL haiku dispatch. Sonnet verify ensign runs inline review only. Why: haiku hallucinated 50-100% of citations on prompt-text diffs in 2026-04 D1 measurement (n=2 SKILL.md entities, 0 surviving findings).

| Agent name | Skill to load | When to dispatch |
|------------|--------------|-----------------|
| `code-reviewer` | `pr-review-toolkit:code-reviewer` | Always (when source files present) |
| `silent-failure-hunter` | `pr-review-toolkit:silent-failure-hunter` | Size M/L (when source files present) |
| `insecure-defaults` | `trailofbits:insecure-defaults` | Diff touches auth/config/env/secret in production code (excludes `*.test.*`, `tests/`, `*.md`) |
| `sharp-edges` | `trailofbits:sharp-edges` | Diff touches API/route/handler in production code (excludes `*.test.*`, `tests/`, `*.md`) |
| `variant-analysis` | `trailofbits:variant-analysis` | Entity source contains "bug" or "fix" |
| `pr-test-analyzer` | `pr-review-toolkit:pr-test-analyzer` | Diff adds OR removes test files (not just modifies) — *demoted from M/L mandatory in D1* |
| `type-design-analyzer` | `pr-review-toolkit:type-design-analyzer` | Diff adds 3+ new exported types/interfaces/enums |
| `comment-analyzer` | `pr-review-toolkit:comment-analyzer` | OPT-IN — entity body contains `haiku-opt-in: comment-analyzer` |
| `code-simplifier` | `pr-review-toolkit:code-simplifier` | OPT-IN — entity body contains `haiku-opt-in: code-simplifier` |

> **Post-D1 cuts** (2026-04): demoted `pr-test-analyzer` from M/L mandatory (n=4 sample: 6 raw → 1 NIT, 0 actionable). Demoted `comment-analyzer` and `code-simplifier` to opt-in (not seen in sample). Tightened `type-design-analyzer` threshold (was: any new `type`/`interface`/`enum`; now: ≥3 new exports). See `ship-verify/SKILL.md` Step 3.1 for citation. Re-evaluate after next 5 entities ship.

Each haiku agent prompt: "Load Skill({skill}). Review `git diff {execute_base}..HEAD`. Report raw findings only — file:line + exact code snippet + check name. No severity. No fix recommendations. Return [] if nothing triggers."

**After all haiku agents complete:** Dispatch verify ensign (sonnet) with `Skill("ship-flow:ship-verify")`. Verify ensign reads `## Haiku Review`, spot-checks citations, classifies findings, runs quality gate + UAT.

- **Inputs:** Execution log with commit SHAs, done criteria from shape, plan for cross-check, PRODUCT.md constraints, haiku review findings
- **Outputs:** Single `## Verify` section with 5 subsections — `### Quality Gate` (5 checks), `### Review Findings` (classified by severity), `### Knowledge Captures` (D1/D2), `### UAT` (mode + results table), `### Verdict` (status / cost / timestamps). Pre-2026-04-19 entities use legacy `## Verify Output` / `## Verify Report` / `## Verify UAT` H2 sections — readers accept both.
- **Good:** Every check has evidence; BLOCKING findings are specific and actionable; done criteria verified with runnable commands; haiku citations spot-checked
- **Bad:** Skipping quality checks; marking PASS without running UAT; classifying real bugs as NIT; trusting haiku findings without spot-check

**Captain smoke test (UI entities):** When an entity has `ui`-typed Done Criteria and verify PASS, FO must complete agent-side verification first (automated tests, code review, self-UAT via e2e-debug), then invite captain for a smoke test before advancing to ship. This is a mod-level gate, not a separate stage:

1. FO starts dev server from worktree branch
2. FO presents specific URLs to captain (entity detail pages that exercise the changes)
3. Captain tests interactively and reports issues
4. If issues found → feedback cycle back to execute
5. Captain says OK → advance to ship

Order matters: agent does all its own verification first, captain tests last. Captain UAT is the final gate, not a substitute for automated verification.

### `ship`

**Load skill:** Invoke `Skill("ship-flow:ship-review")` before starting stage work.

Agent-autonomous. Creates PR, updates ROADMAP.md (Now → Shipped) and PRODUCT.md (new capability + user stories), reports token cost. Only runs after verify PASS.

- **Inputs:** `## Verify → ### Verdict` with `status: passed` (or legacy `## Verify Report` PASS), Problem + Done Criteria for PR body, Shape Output for user stories
- **Outputs:** Single `## Ship` section with subsections — `### PR Draft` (consumed by pr-merge mod), `### ROADMAP.md Update` / `### PRODUCT.md Update` (conditional), `### D2 Knowledge Candidates` (conditional), `### Token Summary`, `### Verdict` (status / PR link / cost / timestamps). Side effects: PR created on GitHub, ROADMAP.md updated, PRODUCT.md updated. Pre-2026-04-19 entities use legacy `## Ship Output` + `## Ship Report` H2 sections — pr-merge mod accepts both.
- **Good:** PR body references done criteria with checkmarks; both docs updated; token cost reported
- **Bad:** Creating PR before verify PASS; forgetting to update PRODUCT.md; not reporting token cost

### `done`

Terminal stage. The merge hook fires here — PR merge, worktree cleanup, entity archival. No stage work — this is a pure lifecycle marker. FO advances entity to `done` after `ship` stage completes successfully.

- **Inputs:** `## Ship → ### Verdict` with PR link (or legacy `## Ship Report`)
- **Outputs:** PR merged, worktree cleaned up, entity archived
- **Good:** Clean merge, no orphaned worktrees
- **Bad:** Advancing to done before ship stage completes

## Workflow State

View the workflow overview:

```bash
/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.9.6/skills/commission/bin/status --workflow-dir docs/ship-flow/
```

Output columns: ID, SLUG, STATUS, TITLE, SCORE, SOURCE.

Include archived features with `--archived`:

```bash
/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.9.6/skills/commission/bin/status --workflow-dir docs/ship-flow/ --archived
```

Find dispatchable features ready for their next stage:

```bash
/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.9.6/skills/commission/bin/status --workflow-dir docs/ship-flow/ --next
```

Find features in a specific stage:

```bash
grep -l "status: plan" docs/ship-flow/*.md
```

## Feature Template

```yaml
---
id:                         # optional legacy field; slug is the effective ID
title: Feature name here
status: draft
source:
started:
completed:
verdict:
priority:                  # P0 | P1 | P2 | P3 — captain urgency
score:                     # 0.0-1.0 — shape scoring gate (computed)
worktree:
parent:                    # epic entity ID (e.g., "003") — optional
depends-on: []             # entity IDs this blocks on — optional
tracker:                   # gh | linear — optional
issue:                     # #42 or PROJ-123 — optional
external_id:               # full external reference — optional
pr:
token_budget:              # set at shape (from size triage)
token_actual:              # accumulated by FO across stages
---

Description of this feature and what it aims to achieve.
```

## Commit Discipline

- Commit status changes at dispatch and merge boundaries
- Commit feature body updates when substantive

## Committing work in progress

ship-flow commit steps (task commits in ship-execute, bootstrap and midway commits in ship-onboard, ship + archive commits in inline-on-main pattern) use **pathspec-lock syntax** to prevent parallel-session staging contamination.

**Forbidden patterns** (enforced by `plugins/ship-flow/lib/__tests__/test-skill-commit-lint.sh` — DC-4 regression guard):

- `git add -A` — stages every modified + new file, scoops unrelated in-flight drafts
- `git add .` — same scoped to cwd
- `git commit -am "..."` / `git commit -a -m "..."` — auto-stages every tracked modification

**Correct pattern** — pathspec-lock at BOTH stage-time and commit-time:

```bash
git add -- <path1> <path2>
git commit -m "<message>" -- <path1> <path2>
```

The `-- <paths>` at commit-time is the load-bearing defense against parallel-session contamination (e.g., another CC session's autonomous save daemon running `git add -A` between your `git add` and your `git commit`). The commit-time pathspec locks the index scope to the listed paths regardless of what else gets staged in the meantime.

**Why this exists**: entity `#063 explicit-staging-ship-flow` (`_archive/`) — commit `5069b8ba` on 2026-04-21 bundled 480 LOC from three unrelated drafts (#059/#060/#028) into a commit tagged "archive: #054" because `git add -A` + `git commit -am` habit bypassed explicit staging. Force-push-to-fix was not an option post-origin-push; tracking commit `2007dbd9` serves as audit trail. Full 5-layer avoidance analysis in `autonomous-save-commit-attribution.md` user memory.

**Deferred follow-ups** (pending a second incident signal):

- Shell wrapper `ship-entity-commit.sh` — would derive pathspec from entity metadata and refuse broad staging at invocation time.
- Commit-attribution linter `check-staged-attribution.sh` — would cross-check commit message entity IDs against staged-file IDs. `husky + lint-staged` framework already registered in `plugins/spacebridge/package.json` (empty `.husky/`) — future integration is a 1-line hook addition.

**Regression guard**: run `bash plugins/ship-flow/lib/__tests__/test-skill-commit-lint.sh` — exits 0 when all skill files follow the discipline, exits non-zero when any forbidden pattern is introduced.

**What to do if the linter fails**: the diagnostic output lists the offending file + line number + pattern. Fix the offending example in-place to use pathspec-lock syntax (`git add -- <paths>` then `git commit -m "..." -- <paths>`). Do NOT suppress the linter — the linter passing is what proves the skill contract holds.

**Running the linter in CI**: the test script is a plain `bash` invocation with no dependencies beyond GNU/BSD `grep`. Wire it into whatever CI step runs `bash plugins/ship-flow/lib/__tests__/*.sh` — no separate integration step required.

## Worktree-first for new entities

Every `/shape` (that reaches confirm) or `/ship <entity-id>` (that dispatches teammates) MUST run inside a git worktree branched from `main`, NOT on the main tip directly.

**Why** — pathspec-lock (`git add -- <path>` + `git commit ... -- <path>`) above is the *procedural* defense against parallel-session staging contamination. Worktrees are the *structural* defense. MEMORY #25 codified pathspec-lock as necessary but NOT sufficient: a concurrent Claude Code session's `git add -A` can still leave visible index state between your explicit-pathspec calls. Worktrees eliminate the contention window — parallel sessions operate on independent working trees and independent indexes.

**Rule** — at `shape-confirm.sh` / stage-artifact-writer invocation time, `git rev-parse --absolute-git-dir` must resolve under `.claude/worktrees/<slug>/.git/worktrees/…`, not the repo's main `.git/`. On main tip, HALT and spawn worktree first.

**How to spawn**:
- **Claude Code agent**: `EnterWorktree` tool with `name: shape-<id>-<slug>` (Claude Code docs). Creates `.claude/worktrees/<name>` on branch `worktree-<name>` from current HEAD.
- **Manual captain**: `git worktree add .claude/worktrees/shape-<id>-<slug> -b worktree-shape-<id>-<slug>`

**Enforced at skill layer**: `plugins/ship-flow/skills/ship-shape/SKILL.md` Invariants + `plugins/ship-flow/skills/ship/SKILL.md` Invariants both list this rule. Agents running those skills HALT if the worktree check fails.

**Pairs with** — "Committing work in progress" above. Use both: worktree eliminates contention; pathspec-lock still required in case someone skips the worktree step.
