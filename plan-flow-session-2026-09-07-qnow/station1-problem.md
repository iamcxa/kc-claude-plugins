# Station 1 — the problem (FO draft, 2026-09-07, project 架構收斂與 POC 瘦身, code_repo iamcxa/qnow)

Who: Kent, as the only reviewer and merger on iamcxa/qnow.
Last time: three PRs (#1174 DEV-36, #1175 DEV-35, #1177 DEV-25) have sat OPEN, MERGEABLE, CI green since 2026-09-01 — six days — with no review record and no merge; DEV-37, the product acceptance that needs them, cannot start.
Today instead: PRs are merged from whichever chat built them (Conductor/Codex), with no accept/review/close record; the batch record that exists for kc-claude-plugins does not exist for qnow.
Cost: six idle days on three green PRs; the acceptance journey (three hosted actors) is blocked behind them.
Fact vs assumption: facts — the three PR states (probed), DEV-37's stated prerequisites, seven Todo tickets with one-paragraph bodies that L4 would refuse. Assumption — that kc-ship-flow can be installed into qnow before its first release (needs a local install from main; kc-ship-flow-v0.1.0 is not tagged, DEV-128 pending).

## Lint on the project (2026-09-07, main ac60ebe4)

LINT FAIL: L1 (project had no `## User value` — added, additive), L4/L8/L10 on the seven un-admitted architecture tickets and two Done ones, L6 identifier-order on DEV-37 → DEV-23 (a legitimate relation), L9 on tickets without surfaces. The four batch tickets (DEV-25/35/36/37) PASS L4 and L8 after the section conversion. The receipt schema requires lint.pass, so DEV-129 (L4/L8/L10 admitted-only; L6 id-order advisory) is dispatched as a pre-batch blocker, the same pattern as DEV-122 last session. DEV-37 executor: Conductor cloud worker (Captain: secrets are present locally and in Conductor cloud).

2026-09-07 — DEV-129 r1 accepted (3ad7e045; station on main ac60ebe4; AC-3 WARN partial variant), Draft PR #389 by open-pr.sh. Live QNow lint with the candidate: only L9 still fails, on un-admitted one-paragraph tickets plus DEV-37 (an acceptance run whose surface is a receipt file, not code). FO amended the Brief: L9 admitted-only (repair round sent); DEV-37's AC-2 now names its receipt path `docs/evidence/qnow-poc-acceptance-receipt.json` as its surface.
