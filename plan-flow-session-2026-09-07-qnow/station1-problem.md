# Station 1 — the problem (FO draft, 2026-09-07, project 架構收斂與 POC 瘦身, code_repo iamcxa/qnow)

Who: Kent, as the only reviewer and merger on iamcxa/qnow.
Last time: three PRs (#1174 DEV-36, #1175 DEV-35, #1177 DEV-25) have sat OPEN, MERGEABLE, CI green since 2026-09-01 — six days — with no review record and no merge; DEV-37, the product acceptance that needs them, cannot start.
Today instead: PRs are merged from whichever chat built them (Conductor/Codex), with no accept/review/close record; the batch record that exists for kc-claude-plugins does not exist for qnow.
Cost: six idle days on three green PRs; the acceptance journey (three hosted actors) is blocked behind them.
Fact vs assumption: facts — the three PR states (probed), DEV-37's stated prerequisites, seven Todo tickets with one-paragraph bodies that L4 would refuse. Assumption — that kc-ship-flow can be installed into qnow before its first release (needs a local install from main; kc-ship-flow-v0.1.0 is not tagged, DEV-128 pending).
