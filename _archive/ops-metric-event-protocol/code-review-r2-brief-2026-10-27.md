Re-review, read-only, analysis only. Candidate: iamcxa/kc-claude-plugins PR #727 at commit 194f0b835a9b0d1dcefd55be36ecedcb72ab23dc, the fix round for a "contract v1" module for an ops inbox (projects sign CloudEvents-style JSON events with Standard Webhooks HMAC; an inbox validates them with this contract before an AI agent reads them; two other projects will pin this commit, so contract behaviour is hard to change later).

The previous round (commit 36973c77) found, and this round claims to fix:
1. Metric event `time` must be UTC `Z` and calendar-valid; the heartbeat id bucket is cut from that string.
2. `sentry.issue.alert`: every field except `title` and `culprit` bounded (patterns, `level` enum, anchored `web_url`).
3. Hostile input (deep nesting, non-string body or type, bad headers or keys) is refused with a reason, never thrown.
4. A missing or non-finite `nowS` fails closed; `webhook-timestamp` must match `^\d+$`.
5. The non-prod environment prefix applies to the dedupe and incident keys of every type.
6. Refusal reasons echo sender text only as a short `[A-Za-z0-9._-]{1,64}` token.
7. `ops.inbox.selftest` subject must be `selftest/<id>`.
Stated limits the README now declares (out of scope): sentry event id not derived from its fields; a recovery repeated after a limit returns to an earlier value; `period` is a pattern, not a calendar check; key scoping by event type is a runtime gap; the key parser accepting an empty secret.

Task: (a) for each of items 1-7, say fixed / not fixed / partly, with a concrete input you tried or derived; (b) any new defect the fix introduced, any remaining way for an event to carry free text other than sentry `title`/`culprit`, any crash on hostile input, or anything forcing a breaking change after pinning. When you claim something holds, state the input and show it reached the check you are claiming (not an earlier refusal).

Output: verdict (sound / sound with fixes / unsound), then the item table, then new findings ranked P1/P2/P3 with symbol name, input, result, smallest fix. Under 60 lines. "none" if nothing; do not pad.
