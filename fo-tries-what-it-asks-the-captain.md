---
title: FO runs any step it asks the Captain to run or look at, as far as it goes without his credentials, and names the one step only he can do
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: intake from the subspace-relay dev2 FO (Paseo agent 1671c3a9, 2026-10-21), quoting the Captain there (relayed, not a ruling in this session): 「都准。但注意，412 你以後應該要自己先測試過才轉給我 UAT，這是 dev2 規範有缺，還是寫得不夠好沒有讓你執行？」 and 「可以，提給 dev2 fo」; an earlier instance on 2026-10-13 (relay task agent-review-identity): 「之後你要我跑的東西你應該要自己跑過一次」.
- Bite: relay PR #412 (task room-modals-try-copy, profile pilot): FO did not run the validator's acceptance script as written before the gate, which breaks the existing rule in kc-dev-flow-2 0.27.0 `skills/validation/principles.md` ("FO runs it as written before the gate"); separately FO asked the Captain for a browser UAT step (open an owner link, sign in as owner) that neither FO nor the validator had driven.
- The gap reported: the rule covers only the acceptance script. Nothing covers an ad-hoc check FO asks of the Captain outside it (a browser flow, an extra command, a token step), so FO can hand him an untried step and stay compliant.
- Shape proposed by the relaying FO (its wording, not the Captain's): before FO asks the Captain to run or look at anything, it runs that step itself as far as it goes without his credentials (for a UI flow, a real browser up to the step that needs his account or token), shows the observed output, and names the one step only he can do and why.
- First ideation step: check whether the miss is a missing rule or an unenforced one (the acceptance-script half is an existing rule FO did not follow), and where a check could catch it (the gate presentation, delivery_gate.py's ask text, the observer).
- Upstream first: validation principles, the README's FO steps and Delivery authority, delivery_gate.py, the observer; relay's state record for the evidence.

## FO alignment

Alignment: needed at ideation; whether a new rule or an enforcement point is the answer is the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
