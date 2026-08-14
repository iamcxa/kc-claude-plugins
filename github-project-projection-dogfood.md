---
id: cx23zq6y1apw1j0kvdf3mns9
title: Dogfood Spacedock projection in kc-claude-plugins Project #1
status: backlog
source: Captain instruction on 2026-08-14 to continue until Project #1 shows the projection result
product: repo-platform
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane:
---

Install the merged deterministic projector into `iamcxa/kc-claude-plugins`, project ten selected `docs/dev` entities into user Project #1, and prove visible field values plus a zero-mutation rerun without giving GitHub lifecycle authority.

## Scope

- Install exactly the workflow, config, and vendored projector bytes produced by `setup-github-project-projection`.
- Keep approval scope `selected` for ten reviewed entity slugs and cap the first run fail-closed.
- Create no linked-Issue bindings; projector-owned Issues may be created only for the selected entities.
- Preserve foreign Project items, verify exact receipts, and leave reverse sync, Milestones, status publication, and additional repositories out of scope.

## Acceptance criteria

1. A no-write installer plan reports exactly three target files and Project #1 identity `PVT_kwHOABc8eM4A-a-N`.
2. The committed config pins `main`, `spacedock-state/dev`, `docs/dev`, the `kc-dev-flow` profile, the installed projector digest, ten selected entities, an expiring classic-PAT approval, and a positive mutation cap.
3. CI and a local audit prove installed byte identity, workflow syntax, config validation, and zero secret values in tracked files.
4. A default-branch manual dispatch creates the selected projector-owned Issues and Project items while leaving receipt-less foreign items unchanged.
5. Live readback shows the selected items in Project #1 with `Status`, exact `SD Stage`, and non-empty `SD Product` when present.
6. An identical rerun records zero mutations and zero planned operations.
7. Every external write is journaled in the reconcile artifact; Project #1 remains derived and SD remains authoritative.

## Evidence boundary

The repository secret value is a separate host operation and never enters installer output, git history, task state, or chat. If the dedicated classic PAT secret is absent or its expiry cannot be bounded, stop before external apply while continuing all file-only validation.
