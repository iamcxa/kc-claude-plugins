Code review, read-only, analysis only. Candidate: iamcxa/kc-claude-plugins PR #727 at commit 36973c775d7d3fa00b36a44e505bdf9bdce5eb3e, a "contract v1" module for an ops inbox. Projects sign CloudEvents-style JSON events (Standard Webhooks HMAC signing) and POST them to an inbox; the inbox validates them with this contract before an AI agent reads them. After merge, two other projects pin this exact commit, so contract behaviour is hard to change later.

The contract's promises (from its README):
- Only allowlisted fields; every value is a number, a date, an enumerated value, or a bounded pattern with no spaces, so an agent never reads free text from an event.
- The raw body must equal JSON.stringify(JSON.parse(body)) (refuses duplicate keys and non-canonical forms).
- Event id is derived deterministically from the event's fields, so retries and resends dedupe and two different facts never share an id.
- Signing keys are scoped by environment (prod vs preview/dev) and by source prefix; an event without environment needs a prod-capable key; dedupe and incident keys never let a preview-signed event claim or join a prod one.

Find defects where the code does not keep these promises, plus correctness bugs, crashes on hostile input, and anything that would force a breaking change after projects pin it. Already known and out of scope: the key parser accepts an empty secret and a source prefix without a trailing colon; `period` is a pattern not a calendar date; `time` is not bounded to the clock; inbox runtime (HTTP handler, routing, storage) is not in this PR.

Output: verdict (sound / sound with fixes / unsound), then findings ranked P1/P2/P3, each with the symbol name, a concrete hostile input or sequence, the observed or derived result, and the smallest fix. Under 60 lines. Say "none" if you find nothing; do not pad.
