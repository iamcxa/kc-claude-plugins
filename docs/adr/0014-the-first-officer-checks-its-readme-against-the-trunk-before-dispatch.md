# 0014. The first officer checks its README against the trunk before dispatch

Date: 2026-10-13

## Status

Accepted

## Context

On 2026-10-13 the first officer (FO) drove four dispatches of one task from a workflow checkout detached at a 2026-10-08 commit. Its `docs/dev2/README.md` was 397 lines behind the 0.21.0 sync on origin/main, so two rules only the newer README carries were missed: dispatch records under `<task>/dispatch/`, and the `package_version.py` hold. `package_version.py` compares the loaded package with the README it is handed, so a stale README passes; nothing compared the README with the trunk's. Spacedock 0.27.0 has no such check (`spacedock --help` lists none, and `status` and `dispatch build` report no README/trunk comparison), and the only mechanical point on its side, `dispatch build`, is outside this package.

## Decision

**Words:** 「准」 — Captain, 2026-10-13, to the combined ideation gate question for this task and two others ("三個都批准，接受下列建議，照 1 → 2 → 3 實作"), which stated the accepted recommendations for this task: D1 fetch and hold if unreachable, D2 strict equality, D3 show the remedy only.

`scripts/workflow_checkout.py <README>` fetches `origin/<trunk>` (trunk from the README's frontmatter) and compares the README's bytes on disk with the trunk's blob at the same path. Exit 0 equal, 1 different, 2 cannot compare. FO runs it before each worker dispatch and on resume, and is told so in `kc-dev-flow-2:dev` (package-owned, so a stale-README FO still reads it) as well as in `references/sd/workflow.md`.

- D1 fetch inside the check; an unreachable origin holds (exit 2). Without a fetch a stale checkout's own `origin/<trunk>` passes it.
- D2 strict equality: a README ahead of the trunk (an unmerged edit) also holds, because "ahead" versus "behind" for one file needs a commit walk this check does not otherwise need.
- D3 FO shows the printed remedy and waits for the Captain; it neither runs the remedy nor moves the checkout, which concurrent sessions may be driving.

**Options considered:**
- the three decisions above as recommended (chosen)
- a second mode of `package_version.py` — rejected: it is a pure file read whose exit 1 means "load a newer package"; a git-backed second meaning on the same code makes the hold ambiguous
- comparing committed blobs (`HEAD:path`) — rejected: FO follows the bytes on disk, and uncommitted edits would pass
- a check inside Spacedock `dispatch build` — outside this package; not available in 0.27.0

**Recommended:** the first option listed in each decision above (fetch and hold; strict equality; show and wait), as the Captain accepted.

## Consequences

The check is prose-enforced: nothing in kc-dev-flow-2 forces FO to run it, and the 2026-10-13 FO's loading of `kc-dev-flow-2:dev` is not recorded, so this ADR does not claim it would have been caught. Only the README is compared, not `_mods/`; a README match is a proxy, since a sync PR changes both together. An offline FO cannot dispatch until the Captain accepts the hold, an FO session started on a branch that edits the README must hold, and each stale checkout costs one Captain turn. A first adoption whose README is not yet on `origin/<trunk>` exits 2 until it merges. Reopen if Spacedock gains a pre-dispatch hook, which would let the check be enforced instead of read.
