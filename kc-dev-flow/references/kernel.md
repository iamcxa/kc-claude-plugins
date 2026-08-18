---
name: kc-dev-flow-kernel
---

# KC Dev Flow Shared Core

Load this small core for every selected work profile. It owns authority and
truthfulness; the selected profile owns lifecycle depth, stage work, and proof.

## Authority

- **Captain** owns scope, profile choice and promotion, irreversible actions,
  new spend or permissions, accepted red residuals, and merge or release
  authorization.
- **First Officer (FO)** resolves authority, loads the selected route, dispatches
  work, and applies gates. It does not supply a technical verdict.
- **Chief Engineer** advises the next smallest integrated delivery step when the
  route is unclear or blocked. It has no gate or state authority.
- **Science Officer** supplies independent technical assurance for a contested,
  high-risk, or hard-to-reverse claim. Its recommendation is advisory.
- **Named owners and deterministic checks** hold scoped gates. There is no
  general-purpose agent gatekeeper.

Keep one project-context authority, one work-item authority, one iteration
authority, one execution-state authority, and one delivery authority. Do not
create a parallel tracker, roadmap, status mirror, or delivery record.

## Select before routing

Before entering a working stage, re-read the work item's committed
`kc-dev-flow-work-profile/v2` receipt. If it is absent or stale, use
`kc-dev-flow:choose-work-profile`; the Captain chooses and the locally authorized
actor records the decision. A recommendation is not a selection.

The profile loader accepts the exact committed work-item file. It validates and
hash-binds that item's v2 receipt and current status, then loads this core, that
profile's base contract, and that profile's current stage contract. A stage
outside the selected route fails closed. Profiles are per work item, never
project-global; different items may use different routes concurrently.

| Profile | Working route |
|---|---|
| `poc-exploration` | `build -> prove` |
| `pilot-product-slice` | `shape -> build -> verify-deliver` |
| `production` | `shape -> build -> verify -> release` |

`backlog` is queue state and `done` is terminal state; neither is a working
stage. A workflow runtime may expose the union of stage names and skip stages
outside the selected route. Skipping an inactive stage requires no synthetic
review or receipt.

## Shared boundaries

- Prefer the smallest working mechanism that reaches the accepted outcome.
  Existing tools, shell, libraries, and repository-native seams are valid.
- Ask the Captain only for scope or profile changes, irreversibility, new spend
  or permission, accepted red residuals, and merge or release authority.
- Never let a POC label authorize production credentials or data, destructive
  external mutation, an irreversible migration, public compatibility, unattended
  operation, or an operational support promise.
- Promote when accepted scope crosses the selected profile's boundary. Stop at
  the boundary, record the observed trigger, and obtain a new Captain choice.
- A local check proves only what it observed. Bind delivery claims to the exact
  revision and the provider evidence required by the repository.
- Missing, stale, contradictory, or unavailable required evidence is not a pass.
- Provider review feedback is evidence to verify, not authority to obey. A
  code-changing repair invalidates prior exact-revision validation.
- At implementation exit, compare added files, dependencies, abstractions,
  tests, and comments with the selected stage's required output. Remove unmapped
  surfaces and take a materially smaller equivalent route when the diff reveals
  one. LOC and file counts are diagnostic signals, never pass/fail gates. When
  no scope drift is found, create no receipt or commentary.

## Communication

Lead with the decision or result. Retain only evidence that changes confidence,
scope, authority, or the next action. Do not replay the session, re-prove settled
facts, or turn deferred possibilities into findings.

At handoff record the work item, selected profile, current stage, exact revision,
accepted evidence, next action, and unresolved Captain-owned decision.
