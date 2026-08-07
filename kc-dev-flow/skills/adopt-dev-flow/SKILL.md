---
name: adopt-dev-flow
description: Use when a brownfield repository needs to adopt, audit, or upgrade a portable development workflow without replacing its existing tracker, sprint authority, stage runtime, or delivery provider.
---

# Adopt Dev Flow

Establish the smallest repository-local adoption of the dev-flow kernel and any
independently selected policy mods. The same procedure applies in Claude Code and Codex;
use host-native read, edit, test, and review tools without changing the authority
model.

## Required references

Read `../../references/kernel.md` completely. For brownfield adoption, also read
`../../references/reverse-recovery-audit.md`. Read
`../../references/work-control-profile.md` only when the repository declares or
is considering an optional control. Read another reference only when the adopter
is considering that policy mod.

## Select a mode

- **audit** — default read-only mode; report recovered surfaces,
  contradictions, and the smallest repair.
- **adopt** — after the user asks for implementation, bind existing authority in
  the workflow README and vendor only the selected policy.
- **upgrade** — compare adopted files with this installed source, present the
  changed policy for acceptance, and replace accepted files byte-for-byte.

## Audit before changing anything

1. Read the nearest repository instructions and check live branch, worktree,
   dirty state, shared-state ownership, and current tracker/runtime contracts.
2. Run the reverse-recovery audit. Do not replace an existing tracker, roadmap,
   workflow runtime, PR flow, or document merely because its name differs.
3. Map these authorities with evidence: project context, work items, iteration,
   execution state, delivery, observation, gate verdicts, and scope changes.
4. Classify each relevant surface as `WORKING`, `WORKING_UNIT_UNPROVEN`,
   `EXISTS_BROKEN`, `STUB`, or `MISSING`. Repair the cheapest compatible seam;
   only confirmed `MISSING` capability is greenfield.

## Adopt

1. Add a concise `## Local Profile` to the repository's existing workflow
   README. It binds the local locators for project context, work items,
   iteration, execution state, delivery, gate verdicts, scope changes, and any
   observation source. A missing optional observation source is written as
   `none`; it is never allowed to become delivery authority.
2. In each lifecycle stage section, add `Policy mods:` followed by the selected
   local `_mods/` paths, or `Policy mods: none`. The list is the stage's policy
   selection; merely finding a file in `_mods/` does not activate it.
3. Create the workflow's `_mods/` directory if needed and vendor
   `../../references/kernel.md` as `_mods/kernel.md` byte-for-byte. Vendor each
   explicitly selected policy mod under `_mods/` with the same basename.
4. Keep repository-specific mechanisms and exceptions in the workflow README.
   Never edit a vendored file to encode local policy. File presence records
   adoption; do not add a second status registry.
5. Validate the real local enforcement point and the repository's normal gates.
   A documentation grep does not prove runtime behavior.

The Local Profile is the binding. No binding YAML, digest, package fallback, or
ambient runtime hook is part of this design.

## Upgrade

1. Re-run the audit and recover the Local Profile before comparing files.
2. Compare local `_mods/kernel.md` with `../../references/kernel.md`, then compare
   each adopted policy mod with the installed reference of the same basename.
   A missing local kernel or a missing stage-selected mod is a refit requirement,
   not permission to read the installed file at runtime.
3. For every changed file, explain the changed invariants one at a time. The
   repository's captain may accept the complete canonical file or retain the old
   local version and record a local exception in the Local Profile. Do not create
   a locally edited hybrid.
4. Replace each accepted file byte-for-byte and rerun local gates. Do not delete
   an unselected or retired mod, and do not change any stage's `Policy mods`
   declaration, unless that change is explicitly part of the approved upgrade.

## Legacy migration

A legacy kernel-binding file is migration evidence, not live authority. Recover
its locators and selected controls. Before removal, record an itemized migration
receipt: every legacy authority or control, whether it remains in force, and its
exact Local Profile row, stage `Policy mods` declaration, or local enforcement
point. Any in-force entry without a unique destination stops the migration.
Immediately before removal, re-read the legacy source and every mapped destination;
if any bytes or in-force entries changed, rebuild and revalidate the receipt.
Remove the binding plus verifier references only after that final comparison and
in the same approved migration slice. Do not keep both mechanisms active.

## Authority boundary

The audit may produce one narrow improvement proposal with observations,
expected value, cost, and a disproof hook. Do not create, schedule, advance, or merge
a process-improvement task merely because the audit found a problem. The
repository's captain or named scheduling authority decides whether it enters a
sprint.

Never add a parallel status mirror. If authority cannot be established, stop
with `UNKNOWN`, name the missing evidence, and leave existing state unchanged.
