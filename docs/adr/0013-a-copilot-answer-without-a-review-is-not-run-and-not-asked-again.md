# 0013. A Copilot answer without a review is "not run" and is not asked again until the Captain says so

Date: 2026-10-13

## Status

Accepted

## Context

On 2026-10-13 FO requested Copilot on iamcxa/kc-claude-plugins #627 and #628. Within six
seconds each got a COMMENTED review reading "Copilot was unable to review this pull request
because the user who requested the review has reached their quota limit." with no heading and
no line comment. `copilot_review.py` printed `answered ... evidence=review:<id>` and exited 0
for it, so a refusal read as a review of the head with no findings. The adopter's
`## Extensions` rule already says an extension that cannot run is `<name> not run: <reason>`,
never clean; the reader gave FO no exit code for this case. `codex_review.py` already reads
an answer it does not recognize as findings, never as clean, and kc-pr-flow has no Copilot
non-review recognition (checked 2026-10-13).

## Decision

**Words:** 「不等 Copilot，也要修復它額度不足時的應對方式」 — Captain, 2026-10-13, after FO reported the refusal; and 「准」 — Captain, 2026-10-13, approving the ideation gate whose question stated the recommendations for D1 and D2.

**Options considered:**
- D1, fail closed: an answer is a review only with a review heading or a line comment of its own; anything else is exit 5 and is reported as `copilot not run: <first 120 characters>` (chosen)
- D1, match the quota sentence only — rejected: covers one wording in one language, and every other non-review answer (an error, an empty body, another language) still reads as answered
- D2, no request to Copilot again in the task until the Captain says its quota is back (chosen)
- D2, one retry per new head — rejected: the recorded refusals came back in seconds, each retry adds a bot review to the PR, and nothing is gained while the quota is out

**Recommended:** the first option of each, D1 fail closed and D2 no re-request until the Captain says so.

`copilot_review.py` exits 5 when the head has Copilot answers but none has a heading or its
own line comment; the line quotes the answer and carries `answer=review:<id>`, never
`evidence=`, so it is no round and never clean. A real review of the same head still decides
over a later refusal, and a refusal answers the request before it. `pr_watch.py` reports
`copilot=not-run` and wakes `wait` once. FO does not wait for Copilot or request it again in
the task until the Captain says the quota is back, and the merge ask names Copilot as not
read with the quote. Later work must keep the reader's rule positive (a review is shown by
its heading or line comment), not a list of refusal wordings.

## Consequences

Every non-review answer now stops FO from counting a round, at the cost that a future
Copilot layout with neither a heading nor a line comment reads "not run" until the script is
taught, and FO reads the quoted body to see it. A refusal that carries its own heading would
still read as answered; EXTENSION.md Limits says so. If the quota returns mid-task, Copilot
stays unread until the Captain asks. Whether FO behaves this way at the next refusal is
observable only then. Reopen if Copilot documents a review format or a refusal status that
the reader can read directly.
