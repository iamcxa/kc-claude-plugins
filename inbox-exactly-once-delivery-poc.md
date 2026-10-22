---
title: A signed event sent three times wakes the ops workflow exactly once, and the inbox cannot push code
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-inbox-exactly-once-delivery-poc
pr:
gates:
    version: 1
    records:
        - id: gate:inbox-exactly-once-delivery-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:inbox-exactly-once-delivery-poc-backlog-1
              briefing:
                id: briefing:inbox-exactly-once-delivery-poc:backlog:attempt-1:revision-1
                digest: sha256:d47faa0fe293d6907a0cdd832659441bac780a94a9b691f67c168f3bd7e74362
                room-ref: ./inbox-exactly-once-delivery-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:inbox-exactly-once-delivery-poc:backlog:1
                briefing: briefing:inbox-exactly-once-delivery-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T08:38:26.64456Z"
                decision: approve
                reason: Captain answered 「准，請持續針對套件的意義做觀察與回饋」 in chat on 2026-10-21 to the backlog gate question, which stated that approving accepts the four criteria, non-goals, the 1-day budget and the stop conditions as written and enters implementation; each outward action still asks first. No Netlify site, secret, Slack destination, App permission change or default-branch push is authorized by this approval.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-21T08:46:20Z
---

Second proof for `kc-ops-inbox`, before the inbox-r1 Pilot is admitted. The riskiest unexecuted assumption, named by the engineering-reviewer on 2026-10-21: an event entering a real inbox reaches a running First Officer exactly once, at a measured latency, even when the sender retries. The first POC (`hermes-ops-fo-exe-dev-poc`, closed PASSED 2026-10-21) never sent anything through an inbox.

Captain's words:
- 「可以，但為了避免誤差，我希望可以派一個 worker 再做一次研究確認這個方向可行，因為這會是一個輕量的 agentic ops 服務，我不希望一開始就因為我的誤差走錯方向」 (2026-10-21)
- 「應該要先定義好 inbox 合約，由不同管道收取，且 platform 本身也要提供 hook 可以接，不能直接依賴第三方平台」 (2026-10-21)
- 「可以先跑這個 poc。」 (2026-10-21, to the probe presented from the engineering-reviewer's report)

## Scope

- One Netlify function on a scratch Netlify site receives a Standard-Webhooks-signed fixture event whose body carries CloudEvents 1.0 attributes (`id`, `source`, `type`, `specversion`). It verifies the signature, dedupes on `source` + `id` with a strong-consistency Netlify Blobs `onlyIfNew` write, calls `workflow_dispatch` on the scratch repository `iamcxa/ops-inbox-probe-scratch` with a credential that has only Actions: write, and posts the returned run link to Slack.
- The dispatched workflow mints its own App installation token with `actions/create-github-app-token` and explicit permissions, and creates one `ops/<id>` branch.
- Non-goals: relay's real hook, the Sentry adapter, FO triage content, where the gate record lives, raise-from-link, qnow.
- Each outward action asks the Captain first: the scratch Netlify site, its environment secrets, the Slack destination, any GitHub App permission change, and the workflow push to the scratch repository's default branch.
- Budget: at most 1 day.
- Stop conditions: duplicate runs or a missed strong-consistency read after two materially different attempts; a Netlify function cannot verify and dispatch within its limits; the inbox needs a credential that can push code.

## Acceptance criteria

**AC-1**: The same signed event sent three times with one `webhook-id`, once more than 60 seconds after the first, produces exactly one workflow run and one `ops/<id>` branch.
Verified by: the function's responses for all three sends, the scratch repository's run list and branch list after the last send.

**AC-2**: The same event with one altered byte is rejected and starts nothing.
Verified by: the rejecting response and no new run or branch.

**AC-3**: The time from the event's arrival to the Slack notice and to the workflow run starting is measured and recorded.
Verified by: timestamps from the function log, the Slack message and the run's start time, for the accepted send.

**AC-4**: The inbox holds only a credential that can start the workflow; the push-capable token exists only inside the workflow run.
Verified by: the inbox credential's permission set read back, a refused push attempt with it, and the in-workflow token's permissions printed without its value.

## FO alignment

Direction alignment before implementation: not needed; the Captain approved running this probe in chat on 2026-10-21, and each outward action asks first.
Surfaces: none
Visible change: none
Captain standing ask, 2026-10-21 (with the backlog approval): 「請持續針對套件的意義做觀察與回饋」. FO reports a package-value observation at each gate of this task.
Captain direction, 2026-10-21 (chat): 「你要注意一件事，平台是剛好是 netlify，不是平台一定是 netlify。五個都同意，這些裡面哪些你可以幫我做？」. FO reading, not his words: the inbox core must not depend on Netlify; Netlify hosts this POC only.

## Stage Report: implementation

- DONE: Exercise the riskiest path first and locally: signature verify, strong-consistency onlyIfNew dedupe on source+id, and the workflow_dispatch call, with three sends of one webhook-id (one more than 60 seconds later) and one tampered send against a local fake GitHub API, before any outward action.
  `npm test` in kc-ops-inbox/poc-exactly-once (branch spacedock-ensign/inbox-exactly-once-delivery-poc, e7e6a746): 9 of 9 pass; with RIG_REAL_WAIT=1 the third send went 61.5 s after the first (real clock, 202/200/200, one dispatch, one Slack post). The dedupe store is an in-memory stand-in, so Blobs' own conditional-write atomicity is NOT yet exercised.
  Mutation proofs, each caught: drop onlyIfNew fails the 3-send and the concurrent test; skip the signature check fails the tampered-byte and stale-timestamp tests; drop return_run_details fails the 3-send, concurrent and token-permission tests.
  Other tests: a branch-unsafe id is rejected before any claim; the minted token request asks for exactly Actions: write on one repository; a 500 refusal releases the claim; a 204 reply and a lost reply both keep the claim.
- DONE: Raise every outward action to the First Officer as one decision request naming the exact target, owner, permissions and cost if known (scratch Netlify site and its environment variables, the Slack destination, the dispatch-only credential, Actions secrets, the workflow push to the scratch repository's default branch), and take none on your own judgment.
  Raised as ONE request in the hold report, below; no site, secret, App, Slack or push action was taken. Only read-only GitHub reads of the scratch repo were made.
- SKIPPED: Record AC-1 to AC-4 with primary evidence from the real scratch site and repository, the measured latencies, and one package-value observation.
  Held: every real-site measurement needs the outward grants above. AC-1 to AC-4 are unmeasured, not failed. Local evidence is in item 1; the package-value observation is preliminary and below.

### Hold report: one decision request (all five outward actions are one bundle, because the site, the credential and the workflow only prove anything together)

Recommendation: approve all five as written. Each is reversible; cleanup is listed.
1. Scratch Netlify site (owner: Captain's account; free tier assumed, cost not measured): create `ops-inbox-poc-<suffix>`; deploy `kc-ops-inbox/poc-exactly-once` with `netlify deploy --prod --dir public --functions netlify/functions`. Remove with `netlify sites:delete`.
2. Netlify environment variables, set by the Captain: `WEBHOOK_SECRET` (`echo "whsec_$(openssl rand -base64 24)"`), `OPS_REPO=iamcxa/ops-inbox-probe-scratch`, `OPS_WORKFLOW=ops-event.yml`, `OPS_REF=master`, `DISPATCH_APP_ID`, `DISPATCH_INSTALLATION_ID`, `DISPATCH_APP_PRIVATE_KEY`, `SLACK_WEBHOOK_URL`. The sender needs `WEBHOOK_SECRET` in its shell; the Captain either runs the sends or supplies it through his secrets wrapper.
3. Slack destination: Captain names one channel and creates an incoming webhook. Free.
4. Dispatch-only credential: a NEW GitHub App `ops-inbox-dispatch-iamcxa`, permissions Actions: Write only (Metadata: Read is implicit), no webhook, installed on the scratch repository only. The existing App 5397558 must NOT be reused: its private key sits in the inbox and could mint contents:write, so AC-4 would fail structurally. Fallback: a fine-grained PAT, Actions: Write on that one repository, 7-day expiry; weaker AC-4 read-back.
5. Scratch repository (owner iamcxa): Actions variable `OPS_PUSH_APP_CLIENT_ID` and secret `OPS_PUSH_APP_PRIVATE_KEY` for the existing App 5397558 (`gh variable set` / `gh secret set --repo iamcxa/ops-inbox-probe-scratch`). Then push `workflow/ops-event.yml` to `.github/workflows/ops-event.yml` on `master`: ruleset 25482703 shows `current_user_can_bypass: never` and needs one approving review, so Captain sets it `enforcement=disabled`, one push, back to `active` (minutes). Actions minutes: about two short runs, not measured.

### Verified against vendor sources (2026-10-21)
- Dispatch returns 200 with `workflow_run_id`, `run_url`, `html_url` only when the body carries `return_run_details: true`; otherwise 204 (GitHub REST OpenAPI description). The design input omitted that flag.
- Blobs: `getStore({ name, consistency: "strong" })` and `set(k, v, { onlyIfNew: true })` returning `{ modified }` (Netlify docs). Standard Webhooks signs `id.timestamp.body`, `v1,` base64 HMAC-SHA256, `whsec_` secret (spec). Actions pinned: create-github-app-token v3.3.0 at 64ab729a6294000f5aa4a4bc0b73d1f32bc45510; `app-id` is deprecated, so the workflow uses `client-id`.
- Not verified: Netlify function timeout (no number found on the Blobs page); to be measured on the real site.

### Package-value observation (preliminary, local only)
- The inbox is thin: about 120 lines of owned logic. The hard parts were three facts that live outside Spacedock: key custody (an inbox that can mint push tokens defeats the boundary), the run-id flag, and a ruleset that makes every new workflow file a Captain action.
- Exactly-once is really claim-then-dispatch. A lost reply after GitHub accepted a dispatch forces a choice between a duplicate run and a lost event; the rig keeps the claim (at-most-once). A production inbox that must not lose events needs reconciliation: `boundary-crossed: retry-recovery` for any Pilot that promises delivery.

### Findings for FO (roborev, two runs, base c27e7659)
Run 1 evidence=roborev:964 (High: treated dispatch 204 as failure; fixed in 7619ec7c). Run 2 evidence=roborev:965 (High: a transport error released the claim; fixed in e7e6a746 by releasing only on a definite refusal, with a test). The fix after run 2 was not re-gated, per the two-run cap. Gates: comment_ratio 5 comment lines of 318 code, 1.6%, under the 5% maximum; doc_impact lists 0 documents; design_surfaces presentable; number_guards not run (Surfaces: none, no ADR).
ADR: none added. Cleanup: nothing created outside the worktree; `/tmp/ghapi.json` removed. What this does not prove: Blobs atomicity, the real latency, the token read-back, or any behaviour on the real site.

### Summary

The riskiest logic is built and falsified locally (dedupe, signature, dispatch call, narrow token request) with three mutation proofs, and two roborev findings were fixed. AC-1 to AC-4 are held on one bundled outward-action request; nothing outward was done.

### Cycle 2 addendum: after the Captain's 2026-10-21 approval of all five actions
- Platform boundary: `inbox-core.mjs` imports nothing from Netlify. Netlify-specific: `netlify/functions/inbox.mjs` (11 lines), `netlify.toml` (6 lines), the `@netlify/blobs` entry in `package.json`. Commit bc3eb38e; 9 of 9 tests pass.
- Done: scratch site `ops-inbox-poc-a66194` (https://ops-inbox-poc-a66194.netlify.app, id 695f5bf3-ba28-42e1-9d12-e7010be5c123) on team Spacedock (Pro plan; Recce is Free and was avoided), deployed with the function at `/inbox`. Set `OPS_REPO`, `OPS_WORKFLOW`, `OPS_REF` and secret `WEBHOOK_SECRET` (copy at ~/.config/ops-inbox-poc/webhook-secret, mode 0600, never printed). Scratch repo Actions variable `OPS_PUSH_APP_CLIENT_ID` set.
- Refused by the permission system, not worked around: `gh secret set OPS_PUSH_APP_PRIVATE_KEY` (secret-store write), ruleset 25482703 off (CI bypass), and the first live send (production-URL call). The Captain runs the first two himself or adds a permission rule; nothing from them was attempted twice.
- Still the Captain's: the Slack incoming webhook, the new Actions-write-only App, its key and `DISPATCH_*` values. Real sends and AC-1 to AC-4 follow after those.

## Stage Report: implementation (cycle 2)

- DONE: Exercise the riskiest path first and locally: signature verify, strong-consistency onlyIfNew dedupe on source+id, and the workflow_dispatch call, with three sends of one webhook-id (one more than 60 seconds later) and one tampered send against a local fake GitHub API, before any outward action.
  Cycle 1 report above: 9 of 9 local tests plus a real 61.5 s run and three mutation proofs; code head cd079cb8, comment_ratio 8 of 335 lines (2.4%).
- DONE: Raise every outward action to the First Officer as one decision request naming the exact target, owner, permissions and cost if known (scratch Netlify site and its environment variables, the Slack destination, the dispatch-only credential, Actions secrets, the workflow push to the scratch repository's default branch), and take none on your own judgment.
  Raised once; the Captain approved 2026-10-21 and completed the permission-gated steps himself (secrets, ruleset, Slack, dispatch App 5408871). Ruleset 25482703 read back `active` by me on 2026-10-22; `.github/workflows/ops-event.yml` is on master.
- DONE: Record AC-1 to AC-4 with primary evidence from the real scratch site and repository, the measured latencies, and one package-value observation: what these measurements say about whether an inbox in front of Spacedock is worth building.
  AC-1 to AC-3 pass on FO's sends (log `inbox-exactly-once-delivery-poc/fo-sends-2026-10-22.log`) with my own read-back; AC-4 passes on two of its three evidence legs, the refused push is not run. Detail below.

### AC evidence
- AC-1 PASS. Sends of event `poc2-20261022T084821` returned 202 dispatched, 200 duplicate, 200 duplicate; the third left 67.1 s after the first (63.4 s after the second). My read-back (`gh api`, 2026-10-22): the run list holds one `ops-event` run, id 39750507891, workflow_dispatch, success, created 08:48:25Z; the branch list holds exactly one `ops/poc2-20261022T084821` (the 6 `ops/probe-*` and 1 relay branch are older). Limit: sequential sends only; the real site never saw a concurrent burst (the local rig did).
- AC-2 PASS. The one-byte-altered send returned 401 `signature-mismatch`; the run list and branch list above show nothing started by it (`...-t` tamper id has no run or branch).
- AC-3 MEASURED, accepted send, function clock (ms after arrival): verified +2, dedupe claim +142, token minted +445, dispatch answered +1807, Slack webhook answered +1873, response out +1968. GitHub: run created 08:48:25Z (arrival was 08:48:23.5Z), job started 08:48:28Z, branch created about 08:48:33.6Z (10 s after arrival). Sender saw 3.4 s end to end for send 1 (1.45 s before arrival, includes network and any cold start) and 1.0 to 1.2 s for duplicates. Slack message-visible time was NOT read: my Slack connector cannot see #kctest, so only the webhook's own 200 is recorded.
- AC-4 PARTIAL. Inbox credential read-back: the token response on send 1 listed `{"actions":"write","metadata":"read"}`. In-workflow token (run 39750507891 log, value never printed): it created `refs/heads/ops/poc2-20261022T084821` (contents write works), actions list and pull-request list returned 403 "Resource not accessible by integration". The issues probe returned 404, not the 403 my probe text predicted, so it proves nothing either way. Refused push with the inbox token: NOT RUN. Cheapest route, awaiting FO's yes: `node probe-refused-push.mjs ~/.config/ops-inbox-poc/dispatch-app.pem 5408871 173699418 iamcxa/ops-inbox-probe-scratch`, which mints the Actions-only token and tries one branch create (expect 403; if it were accepted it would create `ops/refused-push-probe`, a one-branch cleanup).

### Package-value observation
- An inbox in front of Spacedock is cheap and fast enough: about 140 lines of owned logic and 1.8 s from arrival to a started run, against a runner that takes 3 s more to begin and an FO run measured in minutes. Latency is not the cost.
- The value is the contract, not the platform: signature check, claim-before-dispatch and a credential that cannot push. All three held on the real site, and the core runs unchanged under a memory store, so Netlify is replaceable.
- The cost sits outside the code: two GitHub Apps, a ruleset toggle per new workflow file, and secrets only the Captain may set. Worth building only if the Pilot also owns that setup and the retry-recovery duty (a lost reply after an accepted dispatch costs a duplicate or a lost event).
- Not shown: behaviour under real concurrent retries, Blobs atomicity beyond sequential sends, a second adapter, FO triage content.

### Cleanup and limits
Left in place for the Captain: site `ops-inbox-poc-a66194`, the `ops-inbox-dispatch-iamcxa` App, repo variable and secrets, `ops-event.yml` on master, branch `ops/poc2-20261022T084821`, `~/.config/ops-inbox-poc/`. ADR: none. Roborev findings from cycle 1 were fixed in code; the final fix was not re-gated (two-run cap).

### Summary

The exactly-once path works on the real scratch site: one run and one branch for three sends over 67 s, tampering refused, 1.8 s to dispatch. The refused-push leg of AC-4 is the only item not run, and it needs the FO's yes.
