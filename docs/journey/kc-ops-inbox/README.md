# kc-ops-inbox operator journey

[journey.yaml](journey.yaml) is the canonical source: one operator, six steps, sixteen stories, four proposed releases. No release is selected; the Captain chooses. Every story is `gap` or `unverified`, because `kc-ops-inbox` has no code on `main`.

## Sources

| Source | Used for |
| --- | --- |
| Design brief `kc-ops-inbox-brief.md` (draft, not approved), including the Captain's words of 2026-10-19 | outcome, parts, agent authority |
| The Captain's chat words of 2026-10-20, quoted on the story they rule | Hermes, Slack agent, self-hosted runner |
| POC task `hermes-ops-fo-exe-dev-poc` (closed 2026-10-21, passed at POC depth): AC-6 to AC-12, validation report | the three `unverified` stories |
| relay journey `spacedock-review-ops` (relay PR #399, branch `iamcxa/journey-spacedock-review-ops`) | stories moved from relay |
| qnow journey story `production-operations` (r12, gap) | second adopter |

Each story carries a `source` question naming its origin. Open questions have no answer on purpose; the FO's seven relay scenarios that the Captain has not confirmed are open questions on the story they would belong to, not stories.

## Reading it

The story map shows story cards with a green, red or violet border for `exists`, `gap` and `unverified`. Questions and their sources show on the journey-board projection, which this render did not draw:

```bash
node kc-journey-map/lib/journey-render.mjs docs/journey/kc-ops-inbox/journey.yaml kc-ops-inbox --pages story-map,journey-board
```

## Evidence limits

- Unproven: the three `unverified` stories (agent lane, task plus Draft PR, gate from review) ran once on a scratch repository. Spacedock does not authenticate who records the gate, and the gate record dismissed the Captain's approval, so merging needed a second review.
- Unmerged: the POC candidate is on branch `spacedock-ensign/hermes-ops-fo-exe-dev-poc`; `kc-ops-inbox` is absent from `origin/main` (checked 2026-10-21).
- Undeployed: no event intake, dedupe, Slack notice or live producer exists.

## Proposed releases

| Release | Outcome |
| --- | --- |
| `inbox-r1` | Notice and one recommendation: the FO's candidate for the next slice. `raise-from-link` and the in-service agent are deferred. Eight stories; three are the POC-proven authority boundary. |
| `inbox-r2` | Act from the notice: raise the limit without a terminal; the task records the outcome. |
| `inbox-r3` | More events and a second project: routine reports close without a gate; qnow's alerts. |
| `inbox-r4` | Remember and ask: queryable diagnoses and history; ask from Slack. |

## Relay's ops map: where each story goes (proposal, 2026-10-21)

Source: relay journey `spacedock-review-ops` at PR #399. This is a proposal; relay's file and PR are untouched.

| Relay story | Goes to | Reason |
| --- | --- | --- |
| `release-lanes`, `stale-pin-retry`, `staging-limits`, `flaky-release-spec`, `webkit-release-check` | stays in relay | relay's own release pipeline and CI |
| `refusal-lines` | stays in relay | relay's own log counting; it becomes a producer of inbox events |
| `signed-in-ceiling`, `storage-collected` | stays in relay | limits and collection are relay code; both merged (#400, #390) |
| `stop-writes`, `front-door-switch` | stays in relay | relay switches; the inbox may later call one through a narrow tool |
| `capacity-notice` | moves to kc-ops-inbox | notify duty moved; relay only emits the signed event |
| `refusal-history` | moves to kc-ops-inbox | history duty moved |
| `raise-from-link` | moves, split | notice, link and gate are inbox; the raise endpoint stays relay's |
| `agent-recommends` | moves to kc-ops-inbox | the agent, task and Draft PR are inbox |
| `fo-answers`, `fo-self-diagnoses` | moves to kc-ops-inbox | the SD Review FO is paused waiting for the inbox; in-service FO is not v1 |
| `secrets-wrapper` | stays in relay | development-secret hygiene, no inbox consumer |
