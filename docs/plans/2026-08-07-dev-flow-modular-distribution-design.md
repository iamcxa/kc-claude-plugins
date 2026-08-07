# Dev Flow Modular Distribution Design

**Status:** approved architecture reconstructed from the 2026-08-07 relay dogfood
and audited against `origin/main@b9f5882`.

## Goal

Make `kc-dev-flow` portable through vendored policy files and repository-local stage
selection, without a binding YAML, digest verifier, status registry, or ambient
runtime mutation.

## Audit verdict

The previous round is not discarded wholesale:

- Keep the kernel authority/proof placement from PRs #161 and #162.
- Keep the absolutes registry and checker from PR #164; its package contract has a
  real failure surface and remains independent of adopter binding.
- Keep the state-prerequisite extraction from PR #165; it is repository runtime
  infrastructure, not kernel distribution.
- Replace `kernel-binding.template.yaml`, `verify-binding.py`, its test suite, and
  every skill or self-adoption dependency on them.

The relay's first vendored kernel is not canonical: it compressed away valid proof
clauses preserved above. The portable source remains the current upstream kernel,
with only its distribution and self-improvement sections changed. Relay must refit
from that canonical file after this package lands.

## Ownership

- `references/kernel.md` owns portable authority, lifecycle, proof, continuation,
  and bounded self-improvement.
- Other files under `references/` are independently adoptable policy mods.
- An adopter's `docs/dev/README.md` Local Profile binds repository authority and
  stage sections list applicable `Policy mods`.
- Files present under the adopter's `_mods/` directory record adoption. No second
  registry exists.
- `adopt-dev-flow` owns initial vendoring and explicit upgrades. A refit may invoke
  its upgrade mode. `continue-dev-flow` reads but never installs or rewrites policy.
- Spacedock continues to execute hook mods only. This change adds no Spacedock
  runtime behavior.

## Adoption and upgrade

Adoption reverse-recovers existing project, work-item, iteration, execution, and
delivery authorities. It writes a Local Profile into the existing workflow README,
then vendors the canonical kernel plus explicitly selected policy mods into `_mods/`.

Upgrade compares each vendored file with the installed canonical source and presents
changed invariants for acceptance. Accepted files are replaced byte-for-byte. Local
policy belongs in README, never inside a vendored file. Upgrade never deletes an
unselected mod or changes stage lists implicitly.

A legacy binding is migration evidence only. Adoption recovers its authority
locators, verifies the Local Profile preserves them, and removes the legacy binding
and checker references only in the same approved slice.

## Continue flow

On launch, `continue-dev-flow`:

1. discovers the workflow and reads its Local Profile;
2. reads the local `_mods/kernel.md` completely;
3. resolves the active task and stage from live authority;
4. reads only policy mods named by that stage;
5. performs bounded self-improvement before routing product work;
6. resumes or selects committed work through existing authority.

Missing kernel, missing named mod, missing authority, or ambiguous shared-state
ownership stops with a named adoption/refit requirement. Continue does not fall back
to the package reference because that would silently run policy the repository did
not adopt.

## Self-improvement state

`_improvements/state.yaml` is derived coordination state beside the authoritative
`_debriefs/` home. It records schema version, the newest processed debrief, and the
last run's consumed debriefs and disposition.

Continue considers only debriefs newer than the cursor, reads at most the most recent
three, classifies at most one repository-local or reusable candidate, records value,
cost, observations, and a disproof hook, then advances the cursor even when no
candidate is proposed. With no unseen debrief, it performs no repeated analysis.

The record is not a work item. Detection cannot file, schedule, merge, or pause work.
Only existing captain authority can admit a proposal into a work-item provider.

## Verification

- Package contract tests fail while legacy binding artifacts remain or the new
  canonical mod is missing.
- Canonical/self-adopted policy parity remains byte-for-byte where this repository
  adopts a mod.
- The absolutes checker continues to validate every canonical Markdown reference.
- Pressure tests show the old continue skill asks for a binding and reprocesses old
  debriefs; the new skill reads local policy and honors the cursor.
- A fixture runs continue semantics twice: the second run with no new debrief must
  produce no candidate and no cursor movement.

