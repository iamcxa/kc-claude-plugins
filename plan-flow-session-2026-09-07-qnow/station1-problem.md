# Station 1 — the problem (FO draft, 2026-09-07, project 架構收斂與 POC 瘦身, code_repo iamcxa/qnow)

Who: Kent, as the only reviewer and merger on iamcxa/qnow.
Last time: three PRs (#1174 DEV-36, #1175 DEV-35, #1177 DEV-25) have sat OPEN, MERGEABLE, CI green since 2026-09-01 — six days — with no review record and no merge; DEV-37, the product acceptance that needs them, cannot start.
Today instead: PRs are merged from whichever chat built them (Conductor/Codex), with no accept/review/close record; the batch record that exists for kc-claude-plugins does not exist for qnow.
Cost: six idle days on three green PRs; the acceptance journey (three hosted actors) is blocked behind them.
Fact vs assumption: facts — the three PR states (probed), DEV-37's stated prerequisites, seven Todo tickets with one-paragraph bodies that L4 would refuse. Assumption — that kc-ship-flow can be installed into qnow before its first release (needs a local install from main; kc-ship-flow-v0.1.0 is not tagged, DEV-128 pending).

## Lint on the project (2026-09-07, main ac60ebe4)

LINT FAIL: L1 (project had no `## User value` — added, additive), L4/L8/L10 on the seven un-admitted architecture tickets and two Done ones, L6 identifier-order on DEV-37 → DEV-23 (a legitimate relation), L9 on tickets without surfaces. The four batch tickets (DEV-25/35/36/37) PASS L4 and L8 after the section conversion. The receipt schema requires lint.pass, so DEV-129 (L4/L8/L10 admitted-only; L6 id-order advisory) is dispatched as a pre-batch blocker, the same pattern as DEV-122 last session. DEV-37 executor: Conductor cloud worker (Captain: secrets are present locally and in Conductor cloud).

2026-09-07 — DEV-129 r1 accepted (3ad7e045; station on main ac60ebe4; AC-3 WARN partial variant), Draft PR #389 by open-pr.sh. Live QNow lint with the candidate: only L9 still fails, on un-admitted one-paragraph tickets plus DEV-37 (an acceptance run whose surface is a receipt file, not code). FO amended the Brief: L9 admitted-only (repair round sent); DEV-37's AC-2 now names its receipt path `docs/evidence/qnow-poc-acceptance-receipt.json` as its surface.

2026-09-07 — DEV-129 r2 accepted (4ad2ada4): L9 admitted-only too. Live QNow lint with r2: LINT PASS (L6 id-order printed as WARN; L2 `unadmitted: 11` with nothing admitted yet — a vacuous pass DEV-123 will close). Four batch tickets admitted to Cycle 1 (DEV-25/35/36/37); states left as they were (three are Ready/In Review with open PRs). Review station on #389 dispatched (code-reviewer, silent-failure-hunter).

2026-09-07 — review station on #389: 5 findings (4 correctness, 1 test-coverage). Zero-admitted vacuous pass and cycle.id truthiness → listed under DEV-123; advisory-not-recorded and prefix-only assertion → repair round 2 (rule() entry in the receipt; content asserted). **Reviewer disclosure (silent-failure-hunter)**: it deleted two temp worktrees it did not create (/tmp/pr389base, /tmp/pr389wt, the code-reviewer's, already finished) and ran `git worktree prune` in the FO's checkout — metadata only, no tracked content changed; FO verified the checkout afterwards. Recorded as **S40** (a reviewer with Bash can touch sibling agents' scratch; give reviewers distinct scratch roots or a read-only tool set).
- DEV-129 r3 accepted (a0a6c440): advisory recorded via rule() in the receipt, content asserted; 2 findings closed, 2 listed under DEV-123. Live QNow lint with r3: see above. #389 ready for the Captain's merge.

2026-09-07 — **S41 (Captain's question)**: public fixtures named after internal tickets; dev67/dev89 snapshot fixtures (#375) are verbatim internal Linear planning (real bodies, duckbase-co URLs, the Captain's name); dev122/dev129 are synthetic but carry the org URL. DEV-129 repair round 3 sent (neutral name, no org URL, second fixture folded into a test mutation); the older fixtures get their own ticket. The FO opened #389 without running the without-it test across the diff — the rule that would have caught the duplicate fixture.
- 2026-09-07 — Captain ruled S41 option (a): replace fixtures going forward (DEV-130), history stays; a history rewrite is re-evaluated after the two flows and the QNow PoC are done.
