# Validation review: ship-verify-uat-close-round-2

## AC cross-check

- AC-1: `python3 kc-ship-flow/scripts/uat-doc.test.py` — pass ("uat-doc test: all checks passed"),
  including the new `two-root`/`two-root-merged` fixture checks (flat + folder-form + `_archive/`
  entity across both split and merged roots).
- AC-2: `python3 kc-ship-flow/scripts/close.test.py` — pass ("close test: all checks passed"),
  including the new `debrief-scan` fixture checks.
- AC-3: regenerated the real `ship-cloud-wrapper` sprint receipt against a scratch copy of
  `docs/ship/.spacedock-state` (`--no-commit`; no push; real dev/ship checkouts confirmed clean
  afterward via `git status --short`). Task set
  `{ship-cloud-dispatch-and-watch, ship-remove-duplicated-stations, ship-verify-uat-close}` matches
  the hand-written `_ship_fence/close-receipt-ship-cloud-wrapper.json` exactly; `close.py --validate`
  on the regenerated file exits 0.
- AC-4: covered by the `debrief-scan` fixture's task with no fence entry — appears with
  `workspace_id: null`, still counted merged from `pr:` alone (asserted in `close.test.py`).

## Regression check

`dispatch.test.sh`, `watch.test.sh`, `contract-test.py` were run before and after this change
(via `git stash`); failure counts and messages are identical in both states
(`conductor cli changed: read the diff, then re-pin` — this sandbox's `conductor` binary doesn't
match the scripts' pin, unrelated to this task, which touches neither `dispatch.sh`, `watch.sh`,
nor any pin file).

## Verdict

All four ACs have executed, falsifiable evidence (not prose-only). Recommend: approve.
