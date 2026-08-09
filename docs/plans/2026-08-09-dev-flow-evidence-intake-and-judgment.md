# Dev Flow Evidence Intake and Judgment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close the consumer-runtime evidence and upstream-improvement gaps in
`kc-dev-flow`, extract the portable engineering-judgment contract from Ship-Flow,
and publish `kc-dev-flow:science-officer-em` as the canonical replacement skill.

**Architecture:** Keep adopter collection in `continue-dev-flow`, add a
captain-invoked source intake procedure backed by a deterministic sanitizer and
recurrence counter, and keep portable policy in absolutes-gated vendored
references. The optional engineering-judgment mod remains the canonical policy;
the published Science Officer skill is a thin invocation and compatibility entry
that loads the selected local mod, returns the legacy report envelope plus the
full advisory record, and never acquires orchestration or provider authority.

**Tech Stack:** Markdown skills and references, Python 3 standard library,
repository contract tests, Claude Opus high read-only pressure tests and reviews.

---

### Task 1: Establish source-side improvement intake

**Files:**

- Create: `kc-dev-flow/scripts/improvement-intake.py`
- Create: `kc-dev-flow/scripts/improvement-intake.test.py`
- Create: `kc-dev-flow/skills/promote-dev-flow/SKILL.md`
- Create: `kc-dev-flow/skills/promote-dev-flow/agents/openai.yaml`
- Modify: `kc-dev-flow/skills/continue-dev-flow/SKILL.md`
- Modify: `kc-dev-flow/README.md`
- Modify: `scripts/kc-dev-flow-contract-test.py`

1. Run a fresh pressure scenario against current `origin/main`: give the source
   repository a sanitized reusable finding containing one rule-gap hint and three
   occurrences. Record whether the current instructions preserve recurrence,
   distinguish rule versus enforcement, and stop before task creation or edits.
2. Add failing tests for exact handoff fields, unsafe text rejection, stable
   fingerprinting across wording changes, distinct-observation counting, conflicting
   placement hints, proposal-only output, and zero GitHub or repository mutation.
3. Run `python3 kc-dev-flow/scripts/improvement-intake.test.py`; verify RED because
   the intake executable does not exist.
4. Add package-contract assertions for the new skill, executable, README entry, and
   the compatibility meaning of the existing `reusable-kernel` cursor value. Run the
   contract and verify RED on the missing surfaces.
5. Implement the smallest standard-library CLI that reads one or more sanitized JSON
   handoffs and writes one deterministic proposal to stdout. It calculates recurrence
   from distinct observation IDs and reports classification conflicts; it never
   decides placement, writes state, invokes GitHub, creates work, or edits policy.
6. Initialize and write `promote-dev-flow` as a source-maintainer procedure. Require
   duplicate search across kernel, mods, skills, enforcement scripts, and existing
   work items; classify `rule-gap`, `enforcement-gap`, `local-instance`, or
   `duplicate/no-change`; present a proposal to the captain before any mutation.
7. Clarify in `continue-dev-flow` that `reusable-kernel` is a compatibility transport
   label, not a confirmed kernel placement, and require the structured handoff.
8. Run focused tests, package contract, skill frontmatter lint, and a fresh use-case
   pressure test with the new skill.
9. Ask Claude Opus high for a read-only diff review. Repair every valid finding and
   rerun affected checks before updating issue #171's title/body without closing it.

### Task 2: Preserve the observation boundary at closure

**Files:**

- Modify: `kc-dev-flow/references/kernel.md`
- Modify: `docs/dev/_mods/kernel.md`
- Modify: `docs/dev/README.md`
- Modify: `kc-dev-flow/references/absolutes.registry`
- Modify: `scripts/kc-dev-flow-contract-test.py`

1. Run a fresh pressure scenario where a downstream consumer reports behavior, the
   source repository has strong lower-level evidence, and the originating runtime is
   not rerun. Record the current closure verdict and rationale.
2. Add failing contract assertions for observation-level preservation and this
   repository's closure-receipt fields. Verify RED on current `origin/main`.
3. Add one portable Verification-discipline clause: diagnosis and lower-level guards
   do not replace re-observation through the behavior-producing boundary; an equivalent
   runtime must state why it is equivalent; unavailable re-observation remains missing
   evidence rather than completion evidence.
4. Add the local instance to the validation evidence block: reported scenario,
   originating runtime kind, re-observation artifact and exact revision, equivalence
   rationale when applicable, and the already-required falsifier kind.
5. Copy the canonical kernel byte-for-byte to the self-adopted mod, run the absolutes
   checker to its expected RED, classify changed blocks in the registry, and rerun to
   GREEN.
6. Re-run the pressure scenario with the new policy and obtain a fresh Claude Opus high
   diff review. Repair valid findings before correcting #170's five-closed/six-total
   wording without closing it.

### Task 3: Extract portable engineering judgment

**Files:**

- Create: `kc-dev-flow/references/engineering-judgment.md`
- Create: `docs/dev/_mods/engineering-judgment.md`
- Modify: `docs/dev/README.md`
- Modify: `kc-dev-flow/README.md`
- Modify: `kc-dev-flow/references/absolutes.registry`
- Modify: `scripts/kc-dev-flow-contract-test.py`
- Create: `.context/ship-flow-science-officer-em-migration.md` (handoff only)

1. Run a generic-repository pressure scenario without Ship-Flow: green mechanical
   evidence conflicts with a professionally unsound irreversible change. Record whether
   the current policy produces independent synthesis, costly-no, and a non-authorizing
   recommendation.
2. Add failing contract assertions for the new optional mod, its self-adopted byte
   identity, stage selection, and its separation from `PASS|FAIL|UNKNOWN|UNAVAILABLE`.
3. Write the minimal optional mod: adjudicate findings against governing contracts and
   primary-source behavior; require independent synthesis; allow `costly_no`; require a
   converged recommendation before irreversible/schema/scope-cut presentation; make
   every route advisory and preserve captain/gate authority.
4. Keep this portable mod free of Science Officer aliases, persona, startup hooks,
   FO ownership, entity stages, model bindings, GitHub inline replies, and AI-gate
   re-trigger behavior. Task 4 supplies the separate invocation and compatibility
   entrypoint without putting those surfaces into policy.
5. Self-adopt the mod only in ideation and validation, copy it byte-for-byte, update the
   absolutes registry after its expected RED, and rerun the pressure scenario.
6. Ask Claude Opus high for a fresh read-only diff review and repair valid findings.
7. Write a gitignored English handoff describing the destination contract and the
   unowned Ship-Flow follow-up. Do not edit installed plugin caches; Task 4 defines
   the compatibility envelope and source deprecation path.

### Task 4: Publish the Science Officer replacement skill

**Files:**

- Create: `kc-dev-flow/skills/science-officer-em/SKILL.md`
- Create: `kc-dev-flow/skills/science-officer-em/agents/openai.yaml`
- Modify: `kc-dev-flow/.codex-plugin/plugin.json`
- Modify: `kc-dev-flow/README.md`
- Modify: `README.md`
- Modify: `scripts/kc-dev-flow-contract-test.py`
- Modify: `.context/ship-flow-science-officer-em-migration.md` (handoff only)

1. Run fresh Claude Opus high pressure scenarios without the new skill: direct
   invocation by the old aliases, an irreversible mechanically-green decision,
   and conflicting reviewer labels under pressure to post or mutate state. Record
   the missing discovery/compatibility behavior and any authority expansion.
2. Add failing package-contract assertions for the new `SKILL.md`,
   `agents/openai.yaml`, aliases, canonical mod loading, full advisory record,
   legacy `science_officer_em_upward_report` envelope, and zero stage/provider/
   merge authority. Run the contract and verify RED on the missing skill.
3. Initialize `science-officer-em` with the system skill-creator scaffold. Keep
   frontmatter to `name` and `description`, and generate deterministic UI metadata
   whose default prompt explicitly invokes `$science-officer-em`.
4. Implement the smallest replacement entrypoint. In an adopted repository, load
   the stage-selected vendored `_mods/engineering-judgment.md`; for a direct call
   without adoption, load the plugin-shipped reference only for that answer and do
   not claim repository adoption or gate authority.
5. Preserve old caller compatibility by returning
   `science_officer_em_upward_report` with the legacy judgment, trade-off, route,
   confidence, and `fo_boundary` fields plus the complete nested
   `engineering_judgment` record. Outside FO workflows, leave `fo_boundary` empty
   and name retained authority in `authority_boundary`.
6. Keep inline/isolated selection parent-owned. Do not hard-code model binding,
   startup topology, GitHub posting, AI-gate re-trigger, stage mutation, task
   creation, scheduling, merge, or closeout into the portable skill.
7. Update package discovery surfaces and rewrite the gitignored handoff: the new
   kc-dev-flow skill is canonical, while the Ship-Flow source should deprecate its
   old skill or retain only a thin adapter for source-specific launch/provider
   mechanics. Do not edit installed plugin caches.
8. Run the contract, frontmatter lint, skill quick validator, and the same fresh
   forward pressure scenarios with the new skill. Capture and repair any new
   loopholes before asking Claude Opus high for the Round 4 diff review.

### Task 5: Verify and prepare commit choices

**Files:**

- Modify only when a gate identifies a scoped defect.

1. Run all new focused tests and pressure scenarios.
2. Run `python3 scripts/kc-dev-flow-contract-test.py`.
3. Run `bash scripts/skill-frontmatter-lint.sh`.
4. Run `bash scripts/version-parity-check.sh` and verify no version changed.
5. Run `bash scripts/marketplace-verify.sh`.
6. Run `git diff --check`, inspect `origin/main...HEAD`, and verify the original
   Montpellier workspace and #169 lane remain untouched.
7. Present exact commit groups and file lists to the user. Do not stage or commit until
   the user confirms what to commit; after confirmation, stage only named paths.
