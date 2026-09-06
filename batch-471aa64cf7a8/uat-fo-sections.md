# UAT — batch 471aa64cf7a8 (B: kc-ship-flow as its own plugin)

Six PRs, all merged by the Captain on 2026-09-06, in this order: #383 (DEV-122 rider, plan-lint scope) → #384 (B1 skeleton) → #386 (B2 scripts moved) → #385 (B4 pin POC) → #387 (B3 prose sorted) → #388 (B5 docs/ship commissioned). Main is ac60ebe4.

## What the Captain can now do that was not possible this morning

- `kc-ship-flow` is the eighth plugin: manifests, marketplace entry, release-please component at 0.1.0 (Release PR pending), and its contract test runs as a step of the required `marketplace-parity` job on every PR.
- Every ship station is an installed script under `kc-ship-flow/scripts/` with a station page under `kc-ship-flow/references/stations/`; `scripts/ship-flow/` no longer exists.
- The 300-line runtime prose is gone from authority: 26 of 28 segments live in kernel / station pages / the Evidence-block grammar / a non-normative runbook, bound by `prose-placement-check.py`; 2 residual principles are tickets (DEV-126, DEV-127).
- A batch can be pinned to plugin bytes station by station (`pin.py`, POC verdict proceed; digest length-prefixed, replays and regressions refused).
- `docs/ship/README.md` is a commissioned spacedock workflow (entity batch, six stages) with a machine-read Local Profile table; the next batch runs through `kc-ship-flow:first-officer`.

## Known residuals

- **S38**: #385 merged three commits past the FO-accepted head (Captain-directed Codex repair); no Evidence block exists for the merged head. Rule candidate in DEV-114.
- **Workspace count**: the approval allowed 5 workspaces; six items (five B tickets plus the DEV-122 rider) each got a local worktree, the Captain re-signed the approval at 6 on 2026-09-07 (「approve A」); the receipt records 6 and S39 names the bookkeeping miss.
- **e2e gate**: milestone has no CLI flow file → `e2e: not applicable` with reason; a flow for the ship workflow itself belongs to the next batch's dogfood.
- **Enforcement decision outside defaults**: the FO moved the ship contract test into the required job and deleted the path-filtered workflow (DEV-116 r2). One more step per PR; CI time not measured.
- DEV-119 AC-2 (a real batch through the skill) is the next batch.

## Merge order followed and what it cost

Three moved_base merges last batch; zero this batch — every PR landed at its accepted head except #385 (see S38).

---
