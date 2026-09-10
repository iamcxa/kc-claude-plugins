# Validation review — ship-verify-uat-close (7e), attempt 2 (post correction round 1)

## Correction round 1 (recorded as gate record --round validation/1)
- F1 fixed: merged origin/main (750db571), picking up #406's dispatch.sh/watch.sh.
- F2 fixed: close.py/uat-doc.py now read dispatch.sh's real top-level slug -> {workspace, session, message_sha256} fence shape (commit 8dc28e4f); new tests load the sibling task's own dispatch.sh fixture, not a hand-authored guess.
- F3 fixed: v2 receipt schema shipped as kc-ship-flow/schemas/kc-ship-close-receipt.v2.schema.json, wired into close.py --validate via jsonschema.
- F3b (v1 deletion) rejected-with-reason: five other scripts still read v1; removal is the sibling ship-remove-duplicated-stations task's scope.
- F4 fixed: PR #411 body rewritten exactly per docs/dev/_mods/pr-merge.md template, no Linear id.

## Round-2 independent re-review (Stage Report: validation (cycle 2))
- AC-1/AC-2/AC-3 independently reproduced live at head 8dc28e4f (uat-doc.test.py, close.test.py both "all checks passed").
- PR #411 body checked section-by-section against pr-merge.md template: motivation (23 words), What changed (4 bullets), Evidence (2 N/N-passed bullets), Native stack exception (23 files / +1117/-375, reproduced live), Residuals, audit link resolves, no Linear id. dispatch.sh/watch.sh confirmed present on branch post-merge.
- Fence-shape fixture traced to #406's own commit (0cc25fa3), matched against dispatch.sh's literal fence-writing code — not hand-authored.
- v1-schema-deletion skip confirmed still genuinely blocked: contract-test.py and validate-receipt.py both hard-depend on the v1 schema file today.

## Acceptance criteria cross-check
- AC-1, AC-2, AC-3: MET, independently reproduced twice (implementation + validation workers).
- AC-4: NOT MET, correctly scoped out per this entity's own Work profile receipt; blocked on the sibling dispatch/watch task's fence-file shape, which itself marks AC-3 SKIPPED for the same reason — a genuine cross-entity sequencing dependency.

## Residuals carried into the gate
- Design doc `docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md` exists only on `origin/docs/ship-flow-cloud-wrapper-spec`, not `main`.
- `close.py` reads but does not itself write `debrief.status: "failed"` — no script in this sprint writes that field yet.
- Pre-existing `fenced-dispatch.test.sh` failure (3/4 cases) reproduces identically on unmodified main; unrelated to this change; reverified on the clean merge commit.
