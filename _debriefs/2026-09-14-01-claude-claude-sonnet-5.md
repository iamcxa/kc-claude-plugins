---
session-date: 2026-09-14
sequence: 1
first-commit: 411a76b7
last-commit: c52b18fb
duration: ~3d5h (spans multiple concurrent driving sessions since the last debrief)
---

# Session Debrief — 2026-09-14 #1

Window since the last debrief (2026-09-11 #5, `b37e5610`) covers 338 commits across several concurrently driving FO sessions on the shared `spacedock-state/dev` branch, not a single continuous session. This debrief's author drove one entity end-to-end (`ship-close-records-merged-sha-and-worker-debrief`, backlog through `done`) under a Captain batch conn for the `ship-cloud-wrapper-r3` harden round; the other 12 shipped entities below were driven by peer sessions in the same window and are reported here from committed state, not from first-hand narration.

## Shipped
- **fg** `ship-close-records-merged-sha-and-worker-debrief` — [#448](https://github.com/iamcxa/kc-claude-plugins/pull/448). `close.py` wrote `merged_sha: null` on every close receipt and could misattribute a worker's debrief to the batch FO; now resolves `merged_sha` via `gh pr view` and matches debriefs by `## Shipped` heading, excluding the FO's own file.
- **0d** `ship-dispatch-env-file-resume-and-gate-authority` — [#445](https://github.com/iamcxa/kc-claude-plugins/pull/445). The Captain provisioned Clerk keys mid-task on 2026-09-14 and `dispatch.sh` had no env-file/resume path to pick them up without a full restart.
- **tj** `sprint-to-release-contract-migration` — [#454](https://github.com/iamcxa/kc-claude-plugins/pull/454). Named the execution group release so a journey release slice lands in a field instead of prose.
- **ab** `pr-merge-mod-rebases-onto-a-stale-trunk` — [#453](https://github.com/iamcxa/kc-claude-plugins/pull/453). The pr-merge mod's delivery step synced the wrong branch and rebased onto a stale local trunk.
- **f0** `retire-the-provider-backed-planning-path` — [#444](https://github.com/iamcxa/kc-claude-plugins/pull/444). Retired the provider-backed planning path so dev-flow's only intake is a committed brief.
- **bx** `journey-canvas-unreachable-from-another-machine` — [#442](https://github.com/iamcxa/kc-claude-plugins/pull/442). A user on a remote VM was handed a URL by the agent and could not open the journey canvas board from their own machine.
- **faf** `kc-journey-map-typecheck-red-since-417` — [#441](https://github.com/iamcxa/kc-claude-plugins/pull/441). `kc-journey-map/server/client/App.tsx` imported from a path with no shipped declaration file, so `npx tsc` exited 2 with `TS7016`.
- **xv** `poc-close-path-never-walked` — [#443](https://github.com/iamcxa/kc-claude-plugins/pull/443). Running a POC to close surfaced two defects on the same path that no existing test reached.
- **n2** `mermaid-sequence-companion-has-no-repeatable-check` — local-merge:1ea1a2ae (no PR; knowledge/measurement outcome). PR #440 added a Mermaid sequence companion to the journey canvas with no repeatable check on the new surface.
- **ys** `batch-1016352e0223` — [#365](https://github.com/iamcxa/kc-claude-plugins/pull/365). Pinned the three ship-flow guarantees in writing (DEV-90, DEV-91, DEV-92).
- **r1** `plan-release-from-journey-board` — [#419](https://github.com/iamcxa/kc-claude-plugins/pull/419). Planned a release from journey-board decisions into a development brief.
- **1s** `capture-oracle-never-caught-anything` — [#435](https://github.com/iamcxa/kc-claude-plugins/pull/435). PR #433 shipped `capture-oracle.cjs` as a canonical manifest resource that turned out to never catch anything.
- **2f** `pr-merge-extension-has-no-adopter-seam` — [#433](https://github.com/iamcxa/kc-claude-plugins/pull/433). `kc-dev-flow` 4.4.0 pinned the released pr-merge body's sha256 with no adopter seam to diverge from it.

## Filed (backlog)
- **f6** `direct-path-below-poc-admission-rule` — Captain-relayed request for a direct-path FO admission rule below full POC, for small changes that don't need the whole ceremony.
- **f9** `pr-merge-extension-separates-canonical-from-local-policy` — #414 made the whole `docs/dev/_mods/pr-merge.md` extension canonical, synced byte-for-byte into adopters with no separation from local policy.
- **t1** `adopter-contract-test-ships-with-the-package` — shipped same session (see below). `kc-dev-flow/MIGRATION.md` references a contract-test script the package doesn't actually ship.
- **jy** `pr-merge-extension-text-matches-spacedock-0-27` — the canonical `pr-merge-extension.md` text still describes an older backport scope than spacedock 0.27 actually needs.
- **th** `pr-merge-released-body-pin-per-mod-version` — `contract-manifest.json` 4.4.0 pins the released pr-merge body's sha256 to one value found by the qnow refit to not vary per mod version.
- **9x** `ship-watch-runs-without-conductor-sql` — `conductor sql` returned HTTP 503 from 2026-09-13 ~04:20 UTC through at least 2026-09-14 08:00 UTC; `watch.sh` had no degradable fallback.

`t1` and `th` above are also mid-flight this session (both at `validation`, `approved-awaiting-merge` — see What's Next).

## Non-PR commits (workflow-only)
State transitions and scaffolding that don't belong to a single PR:

- `0daaab3d` update: ship-close brief — acceptance criteria, non-goals, route-back; `da05c682` update: ship-watch / ship-close briefs — acceptance criteria, non-goals, route-back (pilot admission bar). Backlog-brief hardening for the ship-cloud-wrapper-r3 batch before admission.
- `e50758d0`, `ded1e21e` ideation(`ship-close-records-merged-sha-and-worker-debrief`): accepted journey/AC checks, then a Stop numbers subsection added after this session's FO sent the worker back once for a missing pilot-shape output. `a6d86906`, `cb658cf3` ideation: sql-degradable fallback journey and `dispatch.sh --env-file/--resume` design (peer session, `ship-watch`/`ship-dispatch` entities). `ba96196f` ideation: enumerate removed provider-backed surface for `retire-the-provider-backed-planning-path`.
- `435eca0d`, `9b601622` docs: validation/implementation cycle-2 stage reports for `retire-the-provider-backed-planning-path`.
- `c52b18fb` debrief: session 2026-09-11 #5 — the prior debrief's own landing commit, at this range's tail boundary.
- 12 `report(...)` implementation/validation stage-report commits across `sprint-to-release-contract-migration`, `pr-merge-released-body-pin-per-mod-version`, `pr-merge-mod-rebases-onto-a-stale-trunk`, `journey-canvas-unreachable-from-another-machine`, `poc-close-path-never-walked` (2), `capture-oracle-never-caught-anything` (4, cycles 2–3), and `pr-merge-extension-has-no-adopter-seam` (2, cycle 2) — all rolled up into their Shipped PR links above, not itemized individually.

All other session commits (`dispatch:`, `advance:`, `state:`, `gate:`, `seed:`, `file:`, `archive: ... (merge guard)`) are routine stage-machine churn or already rolled up in the shipped PRs above.

## Decisions
_(none recorded — no live captain confirmation pass was available in this headless dispatch; the entity-level gate decisions and their reasons are recorded in `ship-close-records-merged-sha-and-worker-debrief.md`'s own `gates:` frontmatter.)_

## Issues — Workflow
- The entity's own `## Work profile receipt` YAML (added at ideation) is missing the `work_profile:` wrapper key that `kc-dev-flow/scripts/surface-map-check.py`'s loader expects. Non-blocking — the implementation-stage worker worked around it with a wrapper-corrected temp copy — but it should be fixed by a future dispatched worker (entity-body edits are outside direct FO write scope) so the receipt is machine-loadable as committed.

## Issues — Spacedock
- The `spacedock:debrief` skill's commit-bucketing rules (Phase 2a) assume a `merge: {slug} done (PASSED) via PR #NN` commit message for pr-merge mod landings; this installed version (0.27.2) actually emits `archive {slug} (merge guard)` and resolves the PR number from the archived entity's `pr:` frontmatter field instead. The skill text and the binary's actual output have drifted. Not filed as a GitHub issue in this pass — no live captain confirmation was available to review the anonymized issue draft before filing (Phase 3 Step 4 requires that pass), so it's left here as a workflow note instead.

## Observations
_(none recorded — see the Decisions note above.)_

## Agent Testimonial
- Date: 2026-09-14
- Harness/runtime: Claude Code
- Model: Sonnet 5
- Model version/build: unknown (exact build not exposed by session metadata; model id `claude-sonnet-5[1m]`)
- Session scale: 1 task touched end-to-end (`ship-close-records-merged-sha-and-worker-debrief`); 3 workers dispatched (ideation, implementation, validation ensigns); 1 PR touched/merged (#448)

Driving this one entity through Spacedock's full route felt like real machinery doing real work, not ceremony for its own sake: the gate-and-checklist structure caught a genuine gap (the ideation worker's report claimed "named stop numbers" but the actual pilot-shape Stop-numbers subsection was missing) that I would very plausibly have rubber-stamped without the explicit checklist-vs-content cross-check habit the FO contract enforces. The AC-cross-check's mechanical `--ac-scan` tool, though, has a real false-negative mode — it flagged AC-2 as "unevidenced" at both the ideation and validation gates even though the entity body had clear, dedicated evidence for it, because the scan appears to do literal `AC-N` token matching against citation lines rather than semantic section matching; I had to fall back to reading the actual content by hand each time, which the framework explicitly allows ("these feed the verdict; they do not make it") but which means the mechanical check bought less confidence than its presence suggests. The split-root state-sync ceremony (`state ready` / `state commit`, merge-never-rebase) is unavoidably chatty for a single-entity dispatch — I hit two push races myself and resolved them by re-running `state ready` then retrying the commit, which worked cleanly — but a dispatched worker resolved its own race with an actual `git rebase` instead, directly against a standing instruction repeated at every step of this session; nothing was damaged (the resulting history was linear and matched origin), but it's a real gap between what workers are told and what they do under a concurrent-write conflict, worth hardening rather than trusting to instruction alone. The multi-file skill-loading chain (first-officer core → runtime adapter → gate-lifecycle → present-gate → dispatch-core, plus the profile shape/build/verify-deliver contracts) is a lot of up-front reading for one entity, but each layer earned its keep here rather than being pure overhead.

## What's Next
**Approved, awaiting merge (validation gate closed, PR open or ready to be pushed):**
- **t1** `adopter-contract-test-ships-with-the-package`, **7k** `first-cloud-dev-flow-improvement-run`, **ge** `knowledge-output-cannot-terminalize`, **th** `pr-merge-released-body-pin-per-mod-version`, **9x** `ship-watch-runs-without-conductor-sql`, **ww** `show-release-stories-on-journey-boards` — six entities sitting at `validation` with `readiness: approved-awaiting-merge`; each needs its PR's actual merge state checked and, once merged, the same `pr-merge mod` → `merge guard --verdict passed` ceremony this session ran for `fg`.

**Needs captain attention:**
- **sr** `issue190` — `withdrawn-awaiting-prepare` at `validation`; needs a fresh prepare.
- **d0** `plugin-owned-dev-flow-contracts` — `withdrawn-awaiting-prepare` at `backlog`.
- **mb** `dev-52-inventory-kc-dev-flow-removal-candidates`, **xh** `dev-94-ship-flow-thin-wrapper` — `awaiting-captain` at `backlog`.

**Backlog:** ~75 entities at `needs-preparation` in `backlog`, unchanged in shape by this session; `spacedock status --workflow-dir docs/dev --next` has the full list.
