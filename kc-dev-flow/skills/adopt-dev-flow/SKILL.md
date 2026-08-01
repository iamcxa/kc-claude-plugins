---
name: adopt-dev-flow
description: Use when a brownfield repository needs to adopt, audit, or upgrade a portable development workflow without replacing its existing tracker, sprint authority, stage runtime, or delivery provider.
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
- **upgrade** — compare the pinned kernel version, preserve local bindings, and
  apply only changed invariants the repository accepts.

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
   `../../assets/local-binding.template.md`. Keep repository-specific adapters
   local. Copy a portable reference only when the repository needs it.
6. If implementation is authorized, repair one seam at a time and validate the
   repository's real enforcement point. Do not claim runtime behavior from a
   documentation grep.
7. Record the kernel source/version and every adopted optional control. An
   omitted control remains off.
8. If portable improvements may return to the kernel source, record
   `upstream_contribution.repository`, its package path, and either
   `propose_only` or `pull_request`. Omission defaults to `propose_only`.

## Authority boundary

The audit may produce one narrow improvement proposal with evidence and a
disproof hook. Do not create, schedule, advance, or merge a process-improvement
task merely because the audit found a problem. The repository's captain or
named scheduling authority decides whether it enters a sprint.

Never add a parallel status mirror. If authority cannot be established, stop
with `UNKNOWN`, name the missing evidence, and leave existing state unchanged.
