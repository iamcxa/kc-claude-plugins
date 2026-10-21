# Inbox exactly-once delivery POC

Disposable proof, not a package. Run the local rig with `npm install && npm test`
(add `RIG_REAL_WAIT=1` for a real 61.5 s gap before the third send).

Real-site pieces, each an outward action the Captain approves first:

| Piece | Names |
| --- | --- |
| Netlify site env (Captain sets) | `WEBHOOK_SECRET` (`whsec_` + base64), `OPS_REPO`, `OPS_WORKFLOW`, `OPS_REF`, `DISPATCH_APP_ID`, `DISPATCH_INSTALLATION_ID`, `DISPATCH_APP_PRIVATE_KEY`, `SLACK_WEBHOOK_URL` |
| Scratch repo Actions (Captain sets) | variable `OPS_PUSH_APP_CLIENT_ID`, secret `OPS_PUSH_APP_PRIVATE_KEY` |
| Workflow file | `workflow/ops-event.yml` to `.github/workflows/ops-event.yml` on `master` |

Send: `WEBHOOK_SECRET=... node send.mjs https://<site>/inbox <event-id> [tamper]`.
