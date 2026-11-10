---
title: The merge check does not demand paths a validation report names as removed scratch
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the qnow dev2 FO, sent with the Captain's approval 「送出」 (2026-11-10), and FO's own case in batch 19 (a validation report citing evidence under a /tmp folder that macOS may clear).
- Bite: on qnow owner-vehicle-kept-after-name (adopted 0.35.0 scripts, run 2026-11-09 ~15:40 UTC), `delivery_gate.py question` and `check` printed `Captain steps record fails: message S4: missing path /tmp/ovk-val4-wt` and held, because inspect_steps runs the absolute-path existence check (S4) over the gate text plus the latest validation report, and the report's cleanup bullet says the validator removed that scratch worktree as told; `delivery_gate.py steps` on the record itself exited 0. The only pass is recreating the folder, which games the check. State: qnow spacedock-state/dev2 at 5e3a5110, `_archive/owner-vehicle-kept-after-name.md` last validation report and `owner-vehicle-kept-after-name/delivery-gate-text.md`.
- Suggested direction (qnow FO, not a ruling): exclude paths the report states were removed, or scope S4 to the gate text and the steps record.
- Non-goals: dropping S4 for the gate text or the steps record.

## Budget
- One package PR to delivery_gate.py and its tests.

## Stop condition
- The qnow input above passes S4 while a missing path the Captain is asked to run still holds.

## FO alignment

Alignment: needed at ideation; which paths S4 reads is the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
