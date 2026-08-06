---
name: adopt-dev-flow
description: Use when a brownfield repository running Spacedock needs to adopt, audit, or upgrade the shared dev-flow kernel without replacing its existing tracker, sprint authority, or delivery provider.
---

# Adopt Dev Flow

Establish the smallest local binding to the versioned dev-flow kernel. The
same procedure applies in Claude Code and Codex; use host-native read, edit,
test, and review tools without changing the authority model.

## Required references

Read `../../references/kernel.md` completely. For brownfield adoption, also
read `../../references/reverse-recovery-audit.md`. Read
`../../references/work-control-profile.md` only when the repository declares
or is considering an optional control.

## Select a mode

- **audit** — default read-only mode; report recovered surfaces, contradictions,
  and the smallest repair.
- **adopt** — after the user asks for implementation, add the binding and repair
  only the confirmed seams.
- **upgrade** — run the binding checker, then apply only the changed invariants
  the repository accepts, preserving local bindings. The comparison is the
  checker's, not yours: reading two documents and judging them the same is the
  failure this mode exists to prevent.

## Procedure

1. Read the nearest repository instructions and check live branch, worktree,
   dirty state, shared-state ownership, and current tracker/runtime contracts.
2. Run the reverse-recovery audit. Do not replace an existing tracker, roadmap,
   workflow runtime, PR flow, or document merely because its name differs.
3. Map these authorities with evidence: project context, work items, iteration,
   execution state, delivery, observation, gate verdicts, and scope changes.
4. Identify contradictions and classify each surface as `WORKING`,
   `WORKING_UNIT_UNPROVEN`, `EXISTS_BROKEN`, `STUB`, or `MISSING`.
5. Propose the smallest binding using
   `../../assets/kernel-binding.template.yaml`. Keep repository-specific adapters
   local. Copy a portable reference only when the repository needs it.
6. If implementation is authorized, repair one seam at a time and validate the
   repository's real enforcement point. Do not claim runtime behavior from a
   documentation grep.
7. Write the binding to one machine-readable file the repository owns, carrying
   `kernel_source`, `kernel_version`, `kernel_entrypoint`, `kernel_digest`, and
   every adopted optional control. The workflow entrypoint links to that file
   rather than restating it. The checker refuses a prose filename, an unindented
   line declaring a key that is not a binding key, and an indented line with no
   key above it — but a file that is a well-formed binding record reads as one
   whatever its prose claims, so put the binding where nothing else lives.
   `kernel_entrypoint` must
   name a file inside the release's `references/`, which is the set the digest
   covers. An omitted control remains off. A binding missing the digest or
   entrypoint is declared but unverifiable, which the checker reports as
   `UNRESOLVABLE` — a different state from undeclared, and not a lesser one.
8. If portable improvements may return to the kernel source, record
   `upstream_contribution.repository`, its package path, and either
   `propose_only` or `pull_request`. Omission defaults to `propose_only`.
9. Run the checker and record its outcome. Do not compute `kernel_digest` by
   hand: leave the field out, run the checker, and copy the
   `verify-binding:expected-digest:` value it prints for the named release.

## Upgrade procedure

Run the checker before reading anything, and let its outcome pick the path:

```
python3 <installed kc-dev-flow>/scripts/verify-binding.py <binding file>
```

It takes no package path; it resolves `kernel_source` against the installed
releases itself. Exit is non-zero on every outcome except `PASS`.

- `PASS` — the pinned release is the newest installed and its bytes match.
  Nothing to upgrade. Report and stop.
- `STALE_COMPATIBLE` — a newer release exists and no file in its reference set
  changed. Update `kernel_version` alone; the digest already matches. Nothing
  normative moved, so no local text changes.
- `REBIND_REQUIRED` — either the binding disagrees with the release it names, or
  a newer release changed the reference set. Read the entrypoint the checker
  printed, diff the whole `references/` directory against the pinned release's
  copy, and bring the repository the changed invariants **one at a time**, each
  as a change the captain can accept or refuse. Update `kernel_version` and
  `kernel_digest` only after the accepted invariants have landed.
- `UNRESOLVABLE` — stop. Do not guess a binding, do not synthesise one from
  fields found elsewhere, and do not treat a missing release as an up-to-date
  one. Report the reason the checker gave and leave state unchanged.

Never rewrite a local contract to match the kernel wholesale. The upgrade is the
set of invariants the repository accepts, and a rejected invariant is recorded as
a local exception rather than silently dropped.

## Authority boundary

The audit may produce one narrow improvement proposal with evidence and a
disproof hook. Do not create, schedule, advance, or merge a process-improvement
task merely because the audit found a problem. The repository's captain or
named scheduling authority decides whether it enters a sprint.

Never add a parallel status mirror. If authority cannot be established, stop
with `UNKNOWN`, name the missing evidence, and leave existing state unchanged.
