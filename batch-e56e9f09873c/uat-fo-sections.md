# UAT — batch e56e9f09873c (First Officer sections; the generated part is `uat.md`)

## What you are approving

Four Draft PRs that make ship-flow's last three stations and its close step scripts fed by the batch record. Merge order matters because #381 carries the two layers below it until they land:

1. **#378** DEV-104 — review station: `open-pr.sh` + `disposition.py` (head `55d06579`, CI green)
2. **#379** DEV-105 — e2e gate: `e2e-gate.py`, credential-stripped `e2e-cli.sh`, this batch's flow (head `ba96da4e`, CI green)
3. **#380** DEV-106 — handoff: `uat-doc.py` + dry-run `notify.sh` (head `b6d50347`, CI green)
4. **#381** DEV-107 — close: schema + validator + debrief writers (head `ede6eecb`, all 9 findings closed, CI pending at write time)

After #379 and #380 squash-merge, #381 will show a conflict; the FO merges main into it under `moved_base` — no action from you.

## How this batch was verified (what "accepted" means here)

Every candidate: accept station on origin/main (`accept-evidence.sh`, commit 4300eee6) ACCEPT; SHA equals the remote head; kc-pr-review with four agents in the FO session, findings dispositioned by `defaults`; CI green at the head. Every blocking finding was fixed in a repair round and re-verified by the FO at the candidate, by execution, before the PR moved.

## Decisions the defaults made that you may overturn

The full list is in `uat.md` § Decisions made under `defaults` (24 lines). The ones that changed shape:

- **All three layer-1/2 PRs were blocked by security findings and repaired** (fork-syntax branch unbound to SHA; case-sensitive category gate; candidate-tree scripts run with FO credentials; markdown injection into this document; whitespace disposition closes a defect). If you would rather have shipped round 1 and filed the findings, that is overturnable per PR.
- **DEV-107 was rebased by the FO** onto the repaired lower layers (merge `89839673`) rather than re-dispatched.
- **DEV-106's Slack half was not built** (planning delta → DEV-113): the plan named no channel or credential. The one message for this batch goes out from the FO's session; the channel is your input.
- **Layer 1 ran as local subagents, not cloud workers**, on your instruction after the quota pause; dispatch-to-evidence 14–20 min each, no Evidence refusals (six of eleven the day before on cloud workers).

## Two things the FO got wrong, both corrected in the record

- The FO ran a **stale accept station** (its worktree lagged main by three commits) for the whole batch; a manual guard covered the gap; one "station defect" was invented from it and retracted (S32/S33).
- The FO's **templating ruling on DEV-105 was wrong** and the worker refused it correctly after a dry run; replaced by the worker's own option (S-list, batch README).

## Residuals (known limits, not untested claims)

- `uat-doc.py` labels any non-main base as `(main)` (DEV-106 r2 fixed only the missing case).
- `open-pr.sh` titles from a merge head after a rebase (S34 → DEV-112).
- `notify.sh` has no real send path (DEV-113).
- The debrief writers' defects are in #381's repair round; this batch's debriefs were FO-edited by hand.
- Fixtures under `scripts/fixtures/ship-flow/uat-doc/` copy two real batch records into main — retention is your call.

## Defects returned to planning

S28–S34 with dispositions are in `receipt/close-receipt.DRAFT.json`; two new Backlog candidates filed (DEV-112 title source, DEV-113 Slack send path). The dev debrief is in the close receipt; the ship debrief is written after your merges.
