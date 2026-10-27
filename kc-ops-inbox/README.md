# kc-ops-inbox

A signed ops event becomes one decision an agent has prepared for the Captain (docs/adr/0040). Not yet a plugin: there is no `plugin.json` or marketplace entry, so nothing here is released.

| Path | What it is |
| --- | --- |
| `contract/` | Contract v1: what a producer sends, the validator, published schemas, fixtures. Start with `contract/README.md`. |
| `core/inbox-core.mjs` | The platform-neutral inbox: verifies, claims event and incident, dispatches the trigger workflow, posts the Slack notice. Imports `node:crypto` and the contract module, which imports only `node:crypto`. |
| `netlify/functions/inbox.mjs` | The Netlify adapter (Blobs store). Another host writes its own adapter over the same core. |
| `trigger/` | `ops-event.yml` (the one workflow in the trigger repository), the First Officer prompt and launcher, and the git credential helper that answers only for https on the GitHub host. |
| `bin/ops-run.mjs` | The trigger run: opens an incident (record, Draft PR, gate) or joins an event to it. |
| `bin/check-citations.mjs` | Re-reads every ADR reference block of a record with git and sha256. |
| `gate/ops-gate.yml`, `bin/record-gate.mjs` | Records the gate from the Captain's own GitHub review, writing only the state branch. |
| `ops-workflow/README.md` | The project's ops workflow (triage, decision, done). |
| `setup/RUNBOOK.md`, `bin/readback.mjs` | The twelve setup steps with their owners, and the script that reads each back (exit 0 only when every row passes). |

Tests: `npm ci && npm test` in this folder. The flow tests run the real Spacedock binary against local git remotes and a fake GitHub; they are skipped when `spacedock` is not on PATH, and fail instead when `OPS_REQUIRE_SPACEDOCK=1` (CI sets it).

Known limits (r1): the inbox is at-most-once (an unanswered dispatch keeps its claims and Slack says so); the agent App can push the state branch, so R22 of the read-back checks that every recorded gate follows from the Captain's review; nothing runs after the Captain's decision.
