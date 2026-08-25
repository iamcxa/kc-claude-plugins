# Design: KC Dev Flow Single-Workflow POC Routing

- **Date**: 2026-08-25
- **Plugin**: `kc-dev-flow`
- **Status**: Accepted by the Captain after Claude PASS
- **Target release**: the unreleased 4.x contract
- **Implementation branch**: `iamcxa/dev-flow-explore-router`
- **Laboratory branch retained**: `iamcxa/dev-flow-behavioral-gate-design`

## 1. Decision

KC Dev Flow keeps one workflow, one state graph, and the existing three profiles.
It does not add an Explore workflow, an Explore stage, or a second state owner.

POC owns bounded exploration and bounded technical proof. Pilot and Production
own delivery after the next commitment is accepted:

```text
Could negative evidence change the next accepted commitment?
├─ yes → POC
│        ├─ proceed → close the POC; create, defer, or decline a delivery seed
│        ├─ stop    → close the POC; retain the learning
│        └─ change  → close the POC; reconsider direction
└─ no  → choose Pilot or Production by delivery risk
```

The machine slug remains `poc-exploration`. Its user-facing description is:

> **POC — bounded exploration or technical proof.**

“Bounded” means that the decision, cheapest credible falsifier, budget, and stop
condition are fixed before the first working stage. Explore is a use of POC, not
a workflow or profile name.

The product subtitle remains:

> Load development constraints in proportion to work risk, so agent behavior
> is just sufficient without losing verification or authority boundaries.

## 2. Evidence Behind the Decision

The 2026-08-18 through 2026-08-25 state records contained 25 profile-bearing
work items across kc-dev-flow, Relay, and QNow: 3 POC, 12 Pilot, and 10
Production. Twenty-two of the 25 were already Pilot or Production delivery.

The POC records did not support “direction is always accepted before POC”:

- the agent-native skill evaluation boundary could return no-go;
- the QNow Refine-on-Netlify experiment preceded architecture selection;
- the Netlify Database local integration gate proved one accepted technical
  boundary before hosted work.

One Pilot record, the kc-dev-flow improvement loop, first had to decide whether
to keep or retire the mechanism and changed direction when the evidence search
widened. It was discovery expressed as delivery work.

QNow supplied the useful average sequence: bounded POC evidence selected a
technical starting point; a new Pilot architecture contract accepted that
direction; later Pilot items delivered vertical slices; Production remained
reserved for release and operational authority. Relay's week contained only
Pilot and Production because its active Room direction was already accepted.

This supports one POC route with a stronger stop and handoff contract. It does
not support a parallel Explore workflow.

## 3. One Workflow and Three Profiles

The existing superset graph remains unchanged:

```text
backlog → ideation → implementation → validation → done
              └──────── POC skips ideation ────────┘
```

| Profile | Use when | Route | Terminal product |
|---|---|---|---|
| POC | Evidence can change the next commitment | `build → prove` | A supported decision and bounded evidence |
| Pilot | A bounded real-use direction is accepted | `shape → build → verify-deliver` | A limited durable product slice |
| Production | Delivery creates a production, migration, or continuing operational boundary | `shape → build → verify` | Release-ready, owned operational change |

Profile still describes the obligations loaded for one item. It does not predict
duration, correction count, implementation size, or model quality.

## 4. Entry Routing

`choose-work-profile` asks one routing question before recommending a profile:

> Could credible negative evidence cancel or materially change the next
> commitment this item asks the Captain to accept?

- **Yes** recommends POC.
- **No** compares Pilot and Production using the existing audience, lifespan,
  valuable-state, mutation, migration, and operational-commitment boundaries.
- A missing fact that can change the answer is one Captain question.
- A recommendation grants no authority to create, schedule, or advance work.

The “next commitment” is scoped to the item, not the entire product. A selected
product direction may still use POC when one technical mechanism must be proven
before the next delivery commitment. An experimental label alone does not force
POC; an accepted bounded feature can enter Pilot directly.

## 5. POC Entry Receipt

The next work-profile receipt schema adds four scalar fields required only when
`selected: poc-exploration`:

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  route: [build, prove]
  basis: <why this decision needs a bounded proof>
  poc_decision: <the next commitment this evidence decides>
  poc_falsifier: <the cheapest credible negative evidence>
  poc_budget: <explicit time, model, provider, or review ceiling>
  poc_stop_when: <observable point at which work stops>
```

The profile loader requires each field exactly once; rejects blank,
whitespace-only, null-like, template-echo, `TBD`, and `TODO` values; and binds
the result to the exact work-item bytes. It does not claim to understand the
meaning of arbitrary prose or to meter tokens, provider spend, or elapsed time.

Budget execution stays proportional:

- deterministic limits are checked mechanically when the required data exists;
- provider or token limits require a trustworthy usage receipt before they can
  be claimed as enforced;
- otherwise the declared limit is an attended Captain/First Officer stop point,
  not a fictitious automatic gate;
- reaching the limit ends probing and routes the available evidence to review.

Pilot and Production do not carry empty POC placeholders.

## 6. POC Working Contract

### `implementation` — build the probe

Use the shortest safe mechanism that can exercise the declared falsifier. A
real journey, owned logic, and the critical risk remain required. A report or
mock-only path is insufficient when the question is about integrated behavior.

Do not add a framework for hypothetical reuse, cross-host support, recurring
evaluation, release automation, or production hardening. Record temporary
artifacts when they are created and stop at the declared budget or stop
condition even when more work might make the result look better.

### `validation` — decide from evidence

Record one `## POC outcome` section before requesting the Spacedock gate:

```yaml
poc_outcome:
  direction: proceed | stop | change
  evidence: <exact artifact and revision locators>
  strongest_limit: <most important fact left unproved>
  reversal_fact: <evidence that would reverse this conclusion>
  cleanup: <complete or exact remaining cleanup>
```

All three outcomes can complete a POC. “Proceed” is not a delivery verdict;
“stop” is not a failed experiment; “change” is not permission to rewrite the
same item's acceptance criteria. Completion means the evidence supports the
recorded decision within the declared boundary.

Gate approval does not spend task-creation or scheduling authority. After
approval, the Captain may authorize creation, defer it, or decline it for
reasons independent of the technical conclusion.

## 7. Spacedock Gate and Outcome Separation

Spacedock's gate continues to decide evidence quality:

- `approve`: the POC conclusion is adequately supported;
- `revise`: specified evidence must be corrected;
- `hold`: the named evidence boundary stays closed.

The POC outcome separately decides what follows. Spacedock 0.27.0 already
provides every required primitive: one superset state graph, per-item fields,
gates that can be recorded without immediate consumption, `spacedock new`, and
later `gate consume`.

Spacedock does not provide a profile-aware transition hook. KC Dev Flow therefore
owns one small deterministic POC close guard. `continue-dev-flow` uses that guard
before preparing or consuming a POC gate. Before review, the guard validates the
outcome. Before consume, it also validates a separate post-approval handoff
receipt and, for a created handoff, resolves the downstream item. It then invokes
the existing Spacedock commands; it does not reimplement their state transaction.

After approval, record one `## POC handoff` section without rewriting the
approved conclusion:

```yaml
poc_handoff:
  disposition: created | deferred | declined | not_applicable
  to: <downstream id when created; otherwise empty>
  reason: <required for deferred or declined>
```

`stop` and `change` use `not_applicable`. `proceed` uses `created`, `deferred`,
or `declined` according to the Captain's separate task-creation decision.

The supported sequence is:

```text
validation records poc_outcome
  → gate record (without --consume)
  → if stop/change: gate consume → done
  → if proceed:
       Captain chooses create, defer, or decline
       → create:
            resolve source=poc:<exact-source-id>
            → reuse the sole existing item or spacedock new from current trunk
            → record disposition=created and to
            → gate consume → done
       → defer/decline:
            record disposition and reason
            → gate consume → done
```

Every created downstream item records the originating POC in its canonical
`source` field as `poc:<exact-source-id>`. Before creating or retrying, the close
path queries that source. Zero matches permits creation, one match is reused,
and multiple matches stop for repair. This closes the succeeded-create/failed-
handoff-write retry gap without adding a field or engine primitive.

Creating or disposing the downstream handoff before consuming the POC prevents
an orphaned close. If creation or state durability fails, the approved POC
remains in validation and can be recovered without reconstructing its
conclusion. A deferred or declined delivery does not invalidate a supported POC
conclusion and does not keep the POC open. No cross-entity transaction or
Spacedock change is required.

A caller can still bypass KC Dev Flow and invoke the raw Spacedock CLI, just as a
caller can edit workflow state outside the adopted procedure. This design claims
fail-closed behavior for the declared KC Dev Flow close path, not engine-level
tamper resistance.

## 8. Handoff Boundary

When the Captain authorizes delivery, a proceeding POC creates a new backlog
item, not a continuation of the POC. The handoff contains only:

- the originating POC's exact id in canonical `source`;
- the accepted next commitment;
- exact evidence and artifact revisions;
- the strongest rejected or failed alternative;
- the remaining unknowns and reversal fact;
- selective reuse candidates and cleanup status;
- proposed acceptance evidence and non-goals.

The new item has no preselected profile. The Captain selects Pilot or Production
through the normal entry route. The new branch starts from current trunk. Probe
commits are never merged wholesale merely because the POC proceeded; reused
bytes must satisfy the downstream profile.

A POC may retain or merge an isolated experiment artifact when that artifact is
itself the explicitly accepted POC product and creates no delivery promise. Any
product, migration, hosted, compatibility, or continuing-operation use requires
new profile selection.

## 9. Profile-Effect Evidence and Release Canary

The first behavioral comparison remains a manually approved local POC. It asks
whether a candidate profile packet reduces unnecessary process or Captain
correction without weakening the accepted outcome, verification, or authority
boundaries.

The POC must isolate local Claude runs from user-scope and project-scope memory,
instructions, hooks, skills, plugins, MCP servers, ambient credentials, and
unrelated writable paths. It records model, runtime, scenarios, sample count,
severity, usage, exact inputs, exact outputs, limits, and Captain judgment.

Its bounded claim is:

> In the evaluated POC and Pilot scenarios, the candidate profile reduced
> unnecessary process or Captain correction without weakening the accepted
> outcome, verification, or authority boundaries.

A finite probabilistic evaluation never establishes that a profile always
improves development.

If the POC outcome is `proceed`, the fixed differential sentinel may seed a
separate delivery item for the smallest release canary. That item selects Pilot
or Production independently. The canary's narrower claim is:

> This release candidate preserved the demonstrated profile effect on the fixed
> differential canary.

The local POC is not a release gate. The release canary is not authorized until
the POC proceeds and the Captain separately accepts its delivery scope.

## 10. Adoption and Migration

`adopt-dev-flow` continues to install one workflow directory, one superset graph,
one state holder, one profile loader, and the three existing route contracts. It
does not ask adopters to bind or operate an Explore workflow.

The v4 cutover coordinates the packaged and vendored loader, profile contracts,
README guidance, templates, and receipt schema:

1. New profile choices record v3 receipts.
2. The v4 loader accepts active v2 Pilot and Production receipts because their
   route and field meaning do not change; their next Captain profile choice is
   recorded as v3.
3. The v4 loader and close guard refuse an active v2 POC. Before the repo-wide
   cutover, each active v2 POC must either complete under the pinned v3.x
   package/vendor pair or be explicitly re-recorded as v3 by the Captain.
4. A POC still at backlog re-records its Captain choice with the four POC fields
   before entering implementation.
5. The close guard keys on `schema: kc-dev-flow-work-profile/v3`; there is no
   mixed v2/v3 POC close path after cutover.
6. Archived v1/v2 receipts remain historical evidence and are not rewritten.

This is a consumer-action compatibility break because adopters must re-vendor
the loader/contracts and may need to re-record active POC receipts. The release
therefore carries an ordered migration, rollback, version, and announcement
obligation.

## 11. Implementation Slices

### Slice A — Single-workflow contract

- replace the uncommitted two-workflow design with this contract;
- update README, rationale, kernel, profile-choice, continuation, adoption, and
  migration guidance;
- add the v3 receipt fields and fail-closed loader checks;
- add one deterministic POC outcome/handoff close guard used by
  `continue-dev-flow`;
- update POC base/build/prove contracts;
- keep the Spacedock graph and route slugs unchanged;
- add only mechanical local tests.

### Slice B — Profile-effect POC

- create one POC entity from the existing behavioral question;
- preregister sanitized decision points, falsifiers, budget, and stop condition;
- run the manually approved isolated local comparison;
- retain its evidence, outcome, gate ruling, and cleanup receipt.

### Slice C — Release canary, only after `proceed`

- create a clean backlog item from the POC handoff;
- select its delivery profile independently;
- reuse only the proven fixture, runner, evaluator, and receipt seams;
- design the smallest exact-candidate invocation and approval boundary;
- measure hosted and model cost before proposing a required check.

Slice C is not authorized by approving this design. It requires a proceeding POC
and a separate Captain decision.

## 12. Mechanical Testing and Cost Boundary

Slice A uses no model call and adds no new CI job. The incremental runtime added
to existing CI jobs is unmeasured and must be measured before release. Local
tests prove:

- the graph and existing POC/Pilot/Production routes remain executable on the
  pinned supported Spacedock runtime;
- new POC receipts missing each required field fail with a specific error;
- blank, whitespace-only, null-like, template-echo, `TBD`, and `TODO` POC values
  fail closed;
- Pilot and Production need no POC placeholders;
- the KC Dev Flow close guard refuses gate preparation without a complete POC
  outcome;
- an approved `stop` or `change` outcome can reach done without creating a new
  item;
- an approved `proceed` outcome can close with a Captain-recorded deferred or
  declined handoff and reason;
- the close guard refuses a `created` disposition before `poc_handoff.to` resolves
  to the sole downstream item with `source: poc:<exact-source-id>`;
- retry after successful creation but failed POC write reuses that downstream
  item instead of creating another;
- a failed downstream creation leaves the POC recoverably in validation;
- the downstream item starts at backlog without a preselected profile;
- package and adopter contract copies remain byte-identical where required.

The behavior of profile choice is evaluated only in the manually invoked POC.
No stochastic model result enters automatic CI in Slice A.

GitHub Actions and model cost for a later release canary remain unmeasured. No CI
cost claim is made until that item measures an exact candidate path.

## 13. Scope Guard

Slice A stops for redesign if it requires any of the following:

- a Spacedock engine change or cross-entity transaction;
- a provider credential or model call in CI;
- a general sandbox, GitHub identity adapter, retention service, or attestation
  system;
- an Explore workflow, Explore stage, fourth profile, or second state holder;
- automatic product delivery from a POC outcome;
- automatic profile selection for the downstream item;
- a new project tracker, iteration authority, or release authority.

The 14,568-line behavioral-gate branch remains a laboratory. Slice A copies no
file from it. Slice C may reuse a seam only after the POC evidence names it and
the downstream profile accepts it.

## 14. Acceptance Criteria

1. One installed workflow routes all work through POC, Pilot, or Production.
2. POC owns both bounded exploration and bounded technical proof.
3. Every new POC fixes one decision, falsifier, budget, and stop condition before
   implementation.
4. `proceed`, `stop`, and `change` are valid POC outcomes when supported by
   evidence.
5. Spacedock gate approval means the conclusion is supported, not that product
   direction passed.
6. A proceeding POC records one Captain disposition before reaching done: a
   resolved new backlog item, a reasoned deferral, or a reasoned decline.
7. The downstream item starts from current trunk and receives an independent
   Pilot or Production choice.
8. The Spacedock graph, route slugs, state authority, and terminal mechanics do
   not change.
9. The declared KC Dev Flow POC close path refuses missing outcomes and orphaned
   proceeding handoffs; no engine-level tamper-resistance claim is made.
10. Slice A adds no model call, paid CI path, secret, protected Environment, or
   release claim.
11. The behavioral-gate laboratory branch is neither merged nor treated as
    release evidence.

## 15. Alternatives Rejected

### Add a separate Explore workflow

Past-week records show that POC already owns the relevant experiments and
technical proofs. A parallel workflow would duplicate state, adoption, routing,
authority, and handoff mechanics for a minority path.

### Rename POC to Explore

Explore suggests open-ended research and does not cover an accepted direction
with one unresolved technical boundary. POC retains the requirement for a real
journey, owned logic, critical-risk evidence, cleanup, and explicit limits.

### Treat POC as delivery after direction selection

This contradicts the observed QNow and kc-dev-flow POC records and leaves
direction-changing work to be misclassified as Pilot. It also allows a probe to
grow into delivery without a new risk decision.

### Keep POC fields as prose only

Prose cannot fail closed when a new POC omits its falsifier or budget. The loader
checks presence and shape while leaving actual metering to the authority or a
deterministic receipt that truly observes it.

### Automatically create and profile the downstream item

Automation would spend task-creation and profile authority that remains with the
Captain. The attended gate-record, create, handoff, and consume sequence is
recoverable with existing Spacedock primitives.

### Merge the behavioral-gate branch before the POC

This makes unqualified infrastructure part of the product and reverses the
evidence order. Sunk implementation is not acceptance evidence.
