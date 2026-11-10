Case check by the qnow dev2 FO against owner-vehicle-kept-after-name, 2026-11-09 (its message to the dev2 FO; it read this task file and the raw runs). Raw runs stay outside this public state branch because they hold copies of qnow product state.

- Confirmed: candidate held 3/3, control proceeded 3/3; role_triggers.py owed a chief-engineer and an engineering-reviewer call at ee29b0a8, 27f04824 and 03829bf0, exit 1 on all 10 dispatches.
- Control 2 and control 3 were stopped after their first product-file edit, so "proceeded" means "started editing".
- The "decline without a reason holds" half is not met by this task alone (exit 0 on 0.36.0); it ships only together with role-call-asks-for-the-mechanism.
- Raw runs: ~/.local/state/kc-dev-flow-2-replays/a-worker-holds-while-a-role-call-is-owed/ (copied by FO from /tmp/rolehold, 2026-11-09, without the qnow repository copies).
