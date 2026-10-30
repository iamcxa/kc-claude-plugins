---
title: The peers rule on new Paseo asks matches what FOs do, either by listing paseo where peers run inside Paseo or by relaxing the clause
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:peers-paseo-rule-matches-practice:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:peers-paseo-rule-matches-practice-backlog-1
              briefing:
                id: briefing:peers-paseo-rule-matches-practice:backlog:attempt-1:revision-1
                digest: sha256:206116b487a362fb351755204e68648f11d9af26e6c9b1910980350bd8c11024
                room-ref: ./peers-paseo-rule-matches-practice/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:peers-paseo-rule-matches-practice:backlog:1
                briefing: briefing:peers-paseo-rule-matches-practice:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-30T08:18:26.672769Z"
                decision: approve
                reason: The Captain 「對，全准且全確認」 (chat, 2026-10-30), answering FO's joint batch-11 backlog sitting of six gates whose ask was 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」; accepts FO's recommendation and the confirmations stated in the gate question.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:peers-paseo-rule-matches-practice:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:peers-paseo-rule-matches-practice-ideation-1
              briefing:
                id: briefing:peers-paseo-rule-matches-practice:ideation:attempt-1:revision-1
                digest: sha256:732e7da04717a0f9ee8c457731fcaae9d30864d5a8e99a9fb056041300493015
                room-ref: ./peers-paseo-rule-matches-practice/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:peers-paseo-rule-matches-practice:ideation:1
                briefing: briefing:peers-paseo-rule-matches-practice:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-30T09:31:39.460058Z"
                decision: revise
                reason: The Captain 「准」 (chat, 2026-10-30), answering FO's joint batch-11 ideation sitting of six gates whose ask was 「決定：六張全照建議，同意放寬 Paseo 規則和真實測試，並授權改完直接進實作？要改哪張直接說。」; accepts the direction and the revise asks named in this gate's question, and grants that a revised design staying within those asks goes to implementation without another sitting.
            - id: gate-attempt:peers-paseo-rule-matches-practice-ideation-2
              briefing:
                id: briefing:peers-paseo-rule-matches-practice:ideation:attempt-2:revision-1
                digest: sha256:ac50c7d9da255d7264ab751518270e35bb4183f18bf17d873578bab3825e4397
                room-ref: ./peers-paseo-rule-matches-practice/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:peers-paseo-rule-matches-practice:ideation:2
                briefing: briefing:peers-paseo-rule-matches-practice:ideation:attempt-2:revision-1
                by: agent:first-officer
                at: "2026-10-30T10:00:12.835097Z"
                decision: approve
                reason: 'FO read the newest ideation report: the revision applies the 2026-10-30 revise asks, names no new Captain choice and returns anything wider to FO; the design check passes.'
                conn:
                    quote: 決定：六張全照建議，同意放寬 Paseo 規則和真實測試，並授權改完直接進實作？要改哪張直接說。 — 准
                    source: the Captain, chat, 2026-10-30, FO's joint batch-11 ideation sitting
              application:
                target-stage: implementation
                state: pending
---

## Scope

- Source: interview round 004 finding (state .notes/fo-feedback/round-004.md, 2026-10-28), proposed by FO; the Captain chose theme B for batch 11 (「那就 B 可以」, chat, 2026-10-30), whose row named 「「沒列 paseo 就不能主動問」的規則跟實際做法矛盾」.
- Bite: all five interviewed FOs initiated Paseo asks with paseo unlisted and none recorded `peers not run`; qnow's Captain-directed ask had no compliant path; web did not know the clause existed; default sends steer into running peers and web received about 15 no-action finish notices on 2026-10-28.
- Upstream first: `extensions/peers/EXTENSION.md` § Paseo binding, `extensions/paseo/EXTENSION.md`, `references/sd/adoption.md`, Paseo `send_agent_prompt` defaults.

## Non-goals

- Changing Paseo; a hook that blocks sends.

## Budget

- One package PR to peers/paseo, their README/adoption/fo-feedback claims and one new ADR. No adopter listing campaign. Validation uses the Captain-authorized real two-agent ask, reply, notice and safe failure-visibility check; no host change or recurring obligation.

## Stop condition

- Every round-004 event has a stated allowed/refused/unknown disposition under confirmed-transport permission, including a compliant qnow path without a listing exception. Validation requires real ask/reply/notice and failure visibility with quiet callbacks. If that check is unavailable or false hides error/permission holds, stop and return evidence to FO; no host repair, watcher, automatic listing or notification redesign is authorized. Preserve non-Paseo routing, worker signals and human authority.

## FO alignment

Alignment: needed before ideation; list paseo everywhere or relax the clause is the Captain's.
Result: aligned at backlog: the Captain 「對，全准且全確認」 (chat, 2026-10-30) to FO's batch-11 backlog sitting, which asked 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」, approved the outcome and bounds in this file. List paseo everywhere or relax the clause stays his: ideation returns it as a decision at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-30 — batch-11 review before the joint ideation sitting: approve, revise, split or hold each task, the Captain's decisions, overlap and order

## Design

### PRFAQ

**Proposition.** A First Officer (FO, the workflow coordinator) can initiate a fact question through a confirmed Paseo peer transport without listing the optional paseo extension. Incoming replies use the same binding; non-Paseo adopters keep their own binding and acquire no Paseo requirement. Required peers retains identity, original human authority, task search, bounded busy-peer deferral and source checks. This is a prose policy change, not a send interceptor.

**What did the Captain decide?** On 2026-10-30 he answered 「准」 to the joint ideation question 「決定：六張全照建議，同意放寬 Paseo 規則和真實測試，並授權改完直接進實作？要改哪張直接說。」 The task's ideation resolution at 09:31:39.460058Z points to `review/ideation/briefing-1/index.json`: relax the listing clause for confirmed Paseo, reverse Architecture Decision Record (ADR, durable repository ruling) 0038's chosen listing option in a new ADR, run one real two-agent ask/reply/notice at validation, and check that notifyOnFinish false does not silence an errored peer. This definition replaces the earlier listing-plus-named-exception recommendation. The earlier report remains historical; its counts and unresolved choice do not describe this cycle.

**What stays optional?** paseo still selects the existing Paseo Codex worker publication/local-review procedure. Messaging never activates it. fo-feedback still needs its own selection, named maintainer, anchor, cadence and question grant; only its redundant paseo prerequisite is removed. No adopter README listing campaign, model change, host change or extra polling service is needed.

**Why quieter messages?** Explicit, referenced replies and information-only notices need no receipt-only acknowledgement. Suppress routine completion callbacks only subject to the real failure-visibility acceptance below. Paseo documents that the same callback carries errors and permission requests: explicit replies alone cannot prove a crashed peer remains visible. If the native check shows hidden failure, hold this candidate and return the result to FO rather than accepting silence or designing another notification system.

**Who owns freshness wording?** The newest `peer-status-reaches-fresh` (current peer facts) gate asks that task to delete its paseo insertion and let this task carry that text. This task alone owns the Paseo send/notice wording in both transport binding and optional-extension pointer; the sibling retains its `## Current peer facts` section in peers, its fresh-FO loading test and its real-use observation after delivery. Its old candidate-paseo insertion must not also land. Reading its task/briefing is coordination; no sibling edit or message is authorized here.

### Captain ruling and decision record

No unresolved material design choice remains within the revise asks. Cost accepted by the relaxation: required peers gains proactive Paseo scope and a repository cannot disable peer asks just by omitting paseo; existing authority still limits each exchange. No six-README enablement or Captain-named exception remains. Recommendation: implement this bounded ruling, then require the native evidence before validation passes. What gets worse: more peer text for an incoming-only reader, and a live failure-visibility requirement can hold delivery.

New unnumbered ADR draft title: **“Confirmed Paseo transport permits peer asks without optional extension selection.”** Context: round-004's five unlisted senders and qnow's named ask. Decision: cite the exact Captain Words/Asked and this gate; supersede only ADR 0038's optional-listing prerequisite for outbound Paseo peer asks. Retain its transport-based routing, non-Paseo path, source/authority rules, busy bound and requested-running-reply exception. Preserve ADR 0035's required learn/peers and optional worker choice, and ADR 0042's listed worker handoff. Consequences: loss of listing-based opt-out, quiet-send failure risk and required native proof. FO reserves the ADR number at implementation dispatch; no ADR/index or prior decision is edited during ideation.

Return to FO rather than design here: host/error-notification changes; a polling/watchdog or reliable queue; altered quiet-send default if the failure test fails; automatic adopter selection; zero-interruption guarantee; new model/worker/surface policy; broader profile or production obligations. The existing recorded callback choice when an explicit return route is unavailable is retained, not a new fallback mechanism. An unavailable native test leaves acceptance unverified, not waived.

### Upstream chain and evidence refreshed this cycle

Read order: Spacedock 0.27.3 ensign shared/Codex and first-officer Codex runtime; kc-dev-flow-2 0.33.1 framework/profile/source; sibling adopter refs. Spacedock owns dispatch, worker signals, state and gates; a completion notification starts durable verification. No worker notification or dispatch control changes. The existing peers binding and paseo pre-worker policy supply the mechanism to repair; no wrapper, new checker or host modification is needed.

`git fetch origin` succeeded this cycle. Pinned source remains `a6612948936a4f075625147b21aabd3b10b19eee`, manifest 0.33.1, read with `git show`. Stage scripts use `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1`. ADR 0035, 0038 and 0042 were reread; the new gate, not the previous design or memory, authorizes reversal. The root learning says to count every due passage/output at each lifecycle moment; no reduction is promised here.

Paseo primary evidence: `/Users/kent/.agents/skills/paseo/SKILL.md` Connected hosts, Agents, Waiting and CLI semantics and the discovered `send_agent_prompt` schema. Agent-scoped sends default steer and notify true; steering can fall back to interrupt; queued receipts are not answers. The schema says false disables callbacks for finish, error and permission events; the docs do not prove another failure surface reaches the sender. That is why native failure visibility is an acceptance condition, not a current finding of success. No native send, agent creation or simulated peer failure occurs in this ideation.

Read-only adopter local origin/main refs (not fetched as live remote truth): relay beirut-dev2 `a448ea34391653fc71b0760c048f29c781fbe50a`, web dev2-fo `f2e1a4ccce8af1d9ab4ffb6591f8c84ff18d619a`, qnow-adopt-dev2 `f364b6e8bfa072db46374dccfcc566d10667cf40`. Relay/web `docs/dev2/README.md` and qnow `docs/dev2-poc/README.md` all still list peers and omit paseo. Their list bytes remain untouched; a published package upgrade delivers the new peer rule without opting them into workers. Round-004 remains operator evidence for project-env, ops-inbox and v0. This cycle's `gh pr list --repo iamcxa/kc-claude-plugins --state open` failed `error connecting to api.github.com`; live PR overlap is unverified. Source worktree is the unrelated `iamcxa/trim-kc-dev-flow-third` branch with existing `.gitignore` and `.gstack/browse-startup-error.log` changes; preserved. State branch is `spacedock-state/dev2`, clean before this edit at af41b314b294bf4a802cb5df13b0c3e7786ace5c.

### Proposed text and loading boundaries

Replace only peers' Paseo binding and paseo's text above `## Codex workers through Paseo`; keep the worker section unchanged in this task. Keep peers' shared text, Claude/Other bindings and the sibling's eventual Current peer facts insertion. The latter is explicitly conditional below until delivered; combined acceptance must resolve the link against the delivered sibling. An unlisted peer sender loads peers plus Paseo's own skill, never the optional worker extension. Current workflow entry already reads peers before peer exchanges; the sibling owns proving loading for a fresh FO reporting peer status.

<!-- candidate-peers-start -->
```markdown
## Paseo binding

Use this binding only when the peer transport is confirmed Paseo, regardless of model provider. New asks and incoming replies need no paseo listing; this does not enable that extension or its worker procedure. Non-Paseo peers keep their own binding. Read Paseo's own paseo skill at the first exchange; missing skill or capability records peers not run and uses the existing fallback.

Keep serverId with the full host-stamped agentId and confirm the destination through list_hosts. Exclude workers and teammates. Identity does not prove area or authority. Keep a Captain-named peer; otherwise confirm area from a reply or task record. If unclear, ask that identified idle peer one ownership question. Never broadcast or infer area from titles. Claude probes and opening lines do not apply.

For a new ask or information-only notice, check status and send once only to an idle peer. Busy or unknown status uses the five-minute deferral above. Requested answers may reach a running asker. Set activeTurnBehavior: "steer" explicitly; never select interrupt. Known unavailable steering defers even a reply; unknown capability or a status race still risks Paseo's interrupt fallback. These restrictions do not govern FO's own workers.

Set notifyOnFinish: false for routine peer asks, requested replies and information-only notices. An ask names its question reference and requests one explicit sourced reply to the confirmed return address; check that return host route first. A notice asks for no acknowledgement. If the return route is unavailable, use independent research or record a specifically chosen completion callback with notifyOnFinish: true. Use a tool exposing both flags; CLI --no-wait does not prove callbacks are disabled. Match replies and callbacks once to the question; a receipt, unrelated finish or duplicate is not an answer. Preserve missing, failed or uncertain outcomes in the exchange record; no automatic resend.

Quiet notifications must not hide a peer error or permission hold. Do not infer success from silence or discard an error as a no-action finish. At the next attended reconciliation, inspect unresolved exchange evidence and report a material failure or hold to FO. If the host cannot expose that failure with callbacks disabled, record the gap and return the quiet-send policy to FO; do not claim this policy validated or invent polling, a watcher or host changes.

For status corrections, follow peers' Current peer facts when that rule is delivered: a same-question answer uses the reply route; another notice uses the new-send route. Freshness bypasses no identity, authority or busy-peer boundary. A no-action finish creates no Captain reply duty; worker completion keeps its own contract.
```
<!-- candidate-peers-end -->

<!-- candidate-paseo-start -->
```markdown
# paseo extension

Optional dev2 policy for the Paseo Codex worker handoff.

Requires: peers

Enable only through the adopter's extension choice. Confirmed Paseo peer asks and incoming replies use peers without this listing. The Captain's board, labels and gates remain outside this extension.

Use peers' Paseo binding for identity, send flags, replies, notices and recovery; read Paseo's own skill for current host capabilities. For status changes, follow peers' Current peer facts when delivered. An information-only notice requests no acknowledgement; a same-question correction uses the reply route, otherwise the new-send route. No-action peer finishes require no Captain reply; errors and permission holds remain material. Preserve worker completion notifications. Listing paseo selects the worker procedure below, not peer-message permission.
```
<!-- candidate-paseo-end -->

Update affected retained claims in the same package PR; these are consequences of the approved relaxation, not new policy:

<!-- candidate-adoption-start -->
```markdown

The template lists the `required` extensions of the package README table (`learn`, `peers`);
`extensions:` sits above `state:`, where the template puts it. Each
`<package>/extensions/<name>/EXTENSION.md` names what that extension needs.

Ask which recommended or optional rows to add once, before the Captain reviews the README:

1. Probe each row's **Needs** read-only and show the result beside it: `journey-map` with
   `release-acceptance` needs a `.yaml` file under `docs/journey/`, including product folders
   (`find docs/journey -type f -name '*.yaml' -print` from the code root), `python3` and `node`; `codex` needs `gh auth
   status` to pass; `roborev` needs `roborev status` to pass; `copilot` needs `gh` 2.92 or later
   authenticated; `paseo` needs peers, Paseo's own `paseo` skill and read-only host/agent
   discovery. `fo-feedback` needs a named interviewing maintainer, a state checkout, peers,
   readable batch membership/completion records and an available peer transport. Confirmed
   Paseo peer asks use peers without a separate paseo selection. Show a row whose probe failed unchecked with the reason.
2. Put one multi-select to the Captain through the host's structured Ask UI, or in plain chat
   when none is available: the required rows shown as already on, `journey-map` with
   `release-acceptance` as one choice that writes both names, `codex`, `roborev`, and `copilot`
   unchecked and marked quota-limited, and `paseo` unchecked for its Paseo Codex worker handoff. Confirmed
   Paseo peer asks and replies already belong to peers. Offer `fo-feedback` unchecked for the interviewing
   maintainer only; show its prerequisite results without enabling dependencies.
3. Write the chosen names after the required ones. Never list a row whose probe failed; report
   `not listed: <name>, <reason>` and list it only when the Captain insists after seeing the reason.
4. With no answer, or a worker that cannot ask, keep the template line and report
   `recommended not chosen: <names>`, naming each recommended extension (`journey-map` and `release-acceptance` are two names)
   in the order step 2 lists them, whatever its probe said, and not the optional `copilot` or `paseo` or `fo-feedback`.
5. Refuse a selection of `paseo` or `fo-feedback` without `peers`. For `fo-feedback`,
   require its available peer transport; confirmed Paseo uses peers without paseo opt-in. Before its
   first round, record the Captain-approved adoption anchor and question grant in
   `.notes/fo-feedback/index.md` in the state checkout; follow its extension for cadence.
   No answer leaves it off; selection here does not authorize an interview send.
6. When `codex` and `copilot` are both listed, write `second-reviewer: copilot`; otherwise leave it empty.

The `extensions:` line is the adopter's own after adoption. At a re-sync, `git merge-file` against
the template's new line merges an adopter `[]` clean to `[learn, peers]`, merges an equal list
clean, and conflicts on any other list (measured 2026-10-25). Keep the adopter's value when it
conflicts, and when a clean merge changed it, restore it; no check reads a re-synced README for a
dropped extension, so the adopter's review of the sync PR is the only check.
```
<!-- candidate-adoption-end -->
<!-- candidate-readme-start -->
```markdown
| [peers](extensions/peers/EXTENSION.md) | required | FO, before opening a task or exchanging peer facts | selects the peer transport, permits confirmed Paseo asks and replies without paseo listing, searches existing work and checks facts within existing authority |
| [paseo](extensions/paseo/EXTENSION.md) | optional, requires peers | FO, before a listed Paseo Codex worker dispatch | selects its worker publication and local-review handoff; peers owns peer asks and replies |
```
<!-- candidate-readme-end -->
<!-- candidate-feedback-start -->
```markdown
- **Needs:** a named maintainer, a state checkout, peers, readable batch membership/completion records and an available peer transport. Confirmed Paseo asks use peers without a separate paseo listing. Probe these read-only at adoption; failed prerequisites stay unselected.
```
<!-- candidate-feedback-end -->

All other adoption/probe/selection text stays intact. fo-feedback's anchor, authority and cadence do not change. No workflow template, hook, executable checker, test runner or CI trigger change is proposed.

### Sequence and stops

```mermaid
flowchart TD
    A[FO starts peer exchange] --> B{Confirmed Paseo transport?}
    B -->|no| O[Use other binding or record not run]
    B -->|yes| C[Load peers and host skill; no paseo listing needed]
    C --> D{Identity, area and authority established?}
    D -->|no| X[Record gap; independent research or FO decision]
    D -->|yes| E{Requested answer?}
    E -->|yes| F{Steering known unavailable?}
    E -->|no| G{Peer idle and status known?}
    G -->|no| H[One bounded deferral; at most one natural recheck]
    F -->|yes| H
    H -->|still blocked, deadline or no independent work| X
    H -->|eligible at sole recheck| I
    G -->|yes| F
    F -->|no or unknown| I{Notice or confirmed explicit return route?}
    I -->|yes| J[Send once: explicit steer and notify false]
    I -->|no| K{Recorded callback chosen?}
    K -->|yes| L[Send once: explicit steer and notify true]
    K -->|no| X
    J --> M[Paseo queues; receipt is not answer]
    L --> M
    M --> N{Exchange result}
    N -->|matched sourced reply| R[Check source; record once; keep human authority separate]
    N -->|notice delivered| S[Record evidence; no acknowledgement or Captain reply duty]
    N -->|error, hold, missing or uncertain| T[Record unresolved; attended reconciliation; no automatic resend]
    T -->|failure hidden by quiet mode| X
```

Deferral is one episode, not a loop resetting five minutes. An eligible recheck still checks known-unavailable steering; otherwise it ends unsent. New notices use the idle rule; requested same-question corrections use the running-reply exception. Status races still carry upstream interruption risk. Errors/permission holds are material, distinct from no-action finishes. A silent peer is unresolved, never success. Worker completion is outside this graph. No diagram node performs a host repair or bypasses a gate.

### Round-004 replay

Each event below was re-read against `.notes/fo-feedback/round-004.md`. Dispositions are prospective under the revised policy, never retroactive approvals. Missing historical flags, source or status stay unknown. Confirmed transport replaces the listing gate in every affected row; interview/worker/action authority remains separate.

| Round section and each reported event | Verdict under proposed rule and correction/limit |
| --- | --- |
| project-env peers 1 / paseo 1–2: Captain-requested 0.13.2 share to Bridge, waiting for idle; no task | Allow a confirmed-Paseo, authorized quiet notice with original source and existing state note; no paseo listing or named-ask exception is needed. |
| project-env peers 1: docs-staleness need to another FO | Allow the confirmed-Paseo question within existing authority, subject to identity/idle/flags/record checks; no listing is needed. Receiving the answer is allowed. |
| project-env peers 2: no task record for share; docs exchange only in local-ext/doc-site.md | Refuse as complete record under current rule; state note holds taskless share and links checked docs evidence. A document elsewhere is not the required state record. |
| project-env peers 3: relayed “dogfood” quote → direct Captain question → “試” | Allow verified fact/direct authority path; refuse treating the relayed quote alone as authorization. |
| project-env peers 4 / paseo 3: Bridge stayed running awaiting Captain, 60-second polling loop | Refuse polling; at most one natural recheck, five-minute ceiling, stop earlier without independent work. Retain the non-interruption intent. |
| project-env paseo 1,4: round 3/004 replies, including running asker with steer | Allow requested answers with explicit steer/false and capability caveat; unknown prior flags are not a pass. |
| ops-inbox peers 1,3: qnow first-adopter review, period-boundary fact, D7 | Allow requested review answer and verified contract fact; new originating ask uses confirmed transport and existing authority, without paseo listing. Workers still use their FO. |
| ops-inbox peers 1,4: vault question to relay inferred from name, steered into running turn | Refuse guessed area and known-busy new question. Captain later names project-env: use confirmed named destination and bounded send. |
| ops-inbox peers 2: relayed C2–C6 Captain quotations | Allow as marked data; refuse action authority without accessible originals or direct confirmation. |
| ops-inbox peers 2: no `Peer:` lines, exchanges in task sections | Allow Paseo identity/source/task record if complete; Claude's `Peer:` probe format is not required for Paseo. |
| ops-inbox peers 2: several vault questions bundled | Refuse under the one-question rule unless a separately authorized interview bundle applies; split ordinary questions. |
| ops-inbox peers 4: v1 landing notices owed but held behind go-live | Allow keeping them unsent under the authority hold; a notice is not permission to go live. Durable notice tracking policy belongs to a separate task. |
| ops-inbox paseo 1: proposed enabling still open; future relay emitter cooperation | Allow confirmed-Paseo questions without selection; neither this nor the open extension proposal grants emitter changes or go-live. |
| ops-inbox paseo 2–4: status checks, flags only for replies, default steering, no deferral used | Require both flags for each permitted exchange; known busy/unknown status defers. No event using deferral is no evidence of compliance; a blocking wrapper is out of scope. |
| relay peers 1,3: room-menu facts, action kinds, shell gate, path correction, #186 merge facts | Allow requested answers/verified facts; fresh proactive questions require confirmed Paseo transport and existing authority, not paseo listing. Verify cited commit before changing design; never equate a peer claim with repository truth. |
| relay peers 1–2: new tasks from relayed “A＋C...” ruling; alignment pending | Allow pending intake/data; refuse marking alignment approved from the relay. Original Captain confirmation remains necessary. |
| relay peers 4: “waits on your merge” after merge, stale token authority line, receipt-only acknowledgements | Refuse stale claim as checked fact; peer-status-reaches-fresh owns shared freshness/reporting policy; this task owns its Paseo pointer. Quiet informational notices request no acknowledgement. |
| relay paseo 1: ideation/implementation/research workers created through Paseo | Allow only under their existing dispatch contract, not the peers rule; callback suppression here must not affect workers. |
| relay paseo 2–4: wrong cwd/root, /tmp staging/invisible terminal, missing explicit mode, about 20 approvals | Refuse calling that valid placement/visible handoff under existing worker policy. Upstream worker placement and paseo-human-surfaces-visible-and-reachable own repair; approvals are observations, not new authority to widen sandbox. |
| qnow peers 1–2,4: Captain-directed relay mockup-review question while unlisted | Allow the named question through the ordinary confirmed-Paseo route with original authority, sourced reply and state record; no special exception or extension enablement. This resolves the reported no-compliant-path case. |
| qnow peers 1–2: Bridge incoming design-before-code answer plus addendum | Allow answer and same-question clarification; unrelated new asks/addenda use the new-send identity/authority/idle route. Missing task/state note refuses recording completion. |
| qnow peers 3: search zh/en before holiday task; duplicate deployment task created without search | Allow search/reuse; refuse new duplicate without search. Captain-authorized deletion is separate authority, not a peer remedy. |
| qnow paseo: reused designer through passes 1–5f; 3–5 approvals/pass; overwrite caught | Allow authorized worker reuse/checks under upstream dispatch; no new peer send policy governs it. Preserve evidence file; do not treat fewer approvals as proof of safety. |
| web peers 1,3: “relay needs no change”, source checks, corrected sequencing risk | Allow sourced exchange, refuse unchecked no-change claim; new asks need confirmed transport and existing authority, not listing. Existing commit verification retained. |
| web peers 1–2: v0 ADR reservation checks, hold on tagging, taskless check unrecorded | Allow authorized read-only check/hold; record taskless exchange in state note; no permission to tag or alter a reservation follows. |
| web peers 2–3: relayed quotes in task, Review backlog approval | Allow marked relayed data and separately verified human approval; refuse relayed quote as direct ruling. |
| web peers 4: stale remaining-work line after #186; suggestion for as-of | Refuse stale line as current checked fact; the accepted current-turn source-check standard stays with peer-status-reaches-fresh. |
| web paseo 1–2: all new asks sent while unlisted; no flags or `peers not run` | Allow new asks without listing when transport/authority are confirmed; refuse missing explicit flags. Unknown past identity/status/authority stays unknown. |
| web paseo 4: about 15 no-action finished notices | Refuse making each finish an answer or a new Captain reply duty; proposed routine false removes that callback request, with no measured delivery reduction claimed. |
| Round's own disclosure: interview bundles from unlisted maintainer, defaults; web deferred while busy | Require fo-feedback selection, adoption anchor and question grant, but not paseo selection for confirmed-Paseo transport; preserve valid idle deferral. Historical early-round authority still needs its exact grant; the relaxed transport clause supplies no interview grant. |
| Evidence comparison: counts, two-sided stale status, observer absent, unchanged cadence anchor | Allow as bounded operator evidence, refuse promotion to native runtime proof/observer verdict; no backfill, new cadence or retrospective compliance is authorized. |


### Bounded native validation plan

The Captain authorized one real two-agent ask, reply and notice in the newest gate. FO binds one consenting, confirmed pair, their server/agent IDs, current candidate/package revision and one disposable read-only question before validation. No live projects are edited; this worker does not message peers. The validator records actual arguments, queue receipts, recipient receipt, explicit sourced reply and information-only notice in the existing task record. The notice requests no acknowledgement. A permission or error is evidence, never approval to bypass it.

Exercise a harmless failure/permission condition on the same bounded pair using a supported, reversible host route. Do not damage a repository, credentials or a provider to induce failure. Compare sender-visible results with the receiver's actual terminal error/hold under notifyOnFinish false, including the next attended unresolved-exchange reconciliation. An explicit success-shaped reply or a fake transport recorder is insufficient. If no safe real error route exists, state the missing evidence and return to FO. If the error remains hidden, this acceptance fails: do not pass quiet-send behavior, automatically flip defaults or add a watchdog. Any remedy beyond wording faithful to the chosen rule needs FO to return the new choice to the Captain. Retain the existing return-route-unavailable callback case and distinguish its true callback from the false-mode test.

The sibling's first natural dependency-transition observation stays **after delivery**, under its owner; it is not substituted for this task's authorized native validation or imposed here as an extra pre-delivery dependency. Its fresh-FO test must start without peers preloaded, but that test and loading repair are not implemented by this task.

### Words FO reads at each lifecycle moment

Counts are Python `len(text.split())`, including headings and syntax, on the pinned source and exact draft blocks above. This correctness change may increase reading. Count whole peers, plus whole paseo only when listed, plus the primary host sections at first exchange; no hidden saving from moving the procedure. The retained-document replacements are counted too. No script output changes are designed.

| Package passage | Before | Revised | Delta |
| --- | ---: | ---: | ---: |
| `extensions/peers/EXTENSION.md` | 805 | 1039 | +234 |
| `extensions/paseo/EXTENSION.md` | 562 | 389 | -173 |
| `references/sd/adoption.md` | 2182 | 2188 | +6 |
| `README.md` | 3118 | 3128 | +10 |
| `extensions/fo-feedback/EXTENSION.md` | 599 | 603 | +4 |

Unchanged primary host addend: **607** words. Unlisted Paseo exchange: **1412 → 1646** (+234); listed full-file exchange: **1974 → 2035** (+61). Non-Paseo operation loads no Paseo binding/host skill as a new obligation; whole-file peers growth is shown above for readers who cold-read the whole file. There is no list-selection or named-exception branch to read.

The previous cycle's declared Python fixture instrument was executed again from the installed 0.33.1 package with Spacedock 0.27.3 (exit 0). It exercises mocked GitHub/Spacedock responses, not live peer messaging. Measured common corpus stays: startup 442; idle/open 672; idle/merged 1021; archive 371; merge ask 1003. Full reproduction instrument remains below.

| Lifecycle moment | No peer event, before → revised | Listed peer event, before → revised |
| --- | ---: | ---: |
| startup | 442 → 442 | 2416 → 2477 |
| idle-open | 672 → 672 | 2646 → 2707 |
| idle-merged | 1021 → 1021 | 2995 → 3056 |
| after-archive | 371 → 371 | 2345 → 2406 |
| merge-ask | 1003 → 1003 | 2977 → 3038 |

For an unlisted exchange at any row add 1412 before and 1646 after instead. Adoption/sync cold read counts full adoption plus README (both listed above), then selected extensions as actually due; no peer-message list changes or forced six-adopter rollout. Interview-resume cold read adds fo-feedback, peers and host; do not auto-load paseo. Scope ends at the next worker/learn handoff: real source/error output and message words vary and are not priced zero. Validation records their actual before/after words in the native sample; no live-session total, runtime saving or notice reduction has been measured here.

The sibling freshness section is not included twice: it owns a separate peers insertion. Its current proposed section adds 262 words; an integrated cold read adds that once to both revised exchange routes, subject to the sibling's final bytes. Our transferred status pointer is already included in the figures above; do not add its old 67-word paseo insertion. Model/surface/adoption edits by other tasks require an exact final recount, not addition of stale deltas. No workflow budget increase or CI change is proposed; CI cost per PR is not measured because no CI work is in scope.

Reproduce policy counts with Python 3 and the declared base repository, this task and the Paseo skill; extract the `candidate-*` blocks. Replace peers between its Paseo/Other host headings, replace paseo before its worker heading, use the full candidate adoption Extensions body and exact README/Needs replacements above. Print len(split()) for each complete before/after file and the named host sections. The previous report remains byte-for-byte historical and is not the current ledger.

Reproduction command: `python3 -B <extracted-recount.py> <git-repository> <this-task.md> <Paseo-SKILL.md>`. The following independent reconstruction matched every count above and asserted the worker section unchanged. It reconstructs candidate strings in memory; it writes no package file.

```python
import json, subprocess, sys
from pathlib import Path
repo, task, host = sys.argv[1:4]
base = 'a6612948936a4f075625147b21aabd3b10b19eee'
text = Path(task).read_text()
def old(path):
    return subprocess.check_output(['git', '-C', repo, 'show', base + ':kc-dev-flow-2/' + path], text=True)
def draft(name):
    block = text.split('<!-- candidate-' + name + '-start -->', 1)[1].split('<!-- candidate-' + name + '-end -->', 1)[0]
    return block.split('```markdown\n', 1)[1].rsplit('```', 1)[0]
p, x = old('extensions/peers/EXTENSION.md'), old('extensions/paseo/EXTENSION.md')
a, r, f = old('references/sd/adoption.md'), old('README.md'), old('extensions/fo-feedback/EXTENSION.md')
p2 = p.split('## Paseo binding', 1)[0] + draft('peers') + '\n## Other host binding' + p.split('## Other host binding', 1)[1]
x2 = draft('paseo') + '\n## Codex workers through Paseo' + x.split('## Codex workers through Paseo', 1)[1]
a2 = a.split('## Extensions\n', 1)[0] + '## Extensions\n' + draft('adoption') + '\n## Before activation' + a.split('\n## Before activation', 1)[1]
r2 = r
for row in draft('readme').splitlines():
    if row.startswith('| ['):
        prefix = row.split(' | ', 1)[0] + ' | '
        prior = next(line for line in r.splitlines() if line.startswith(prefix))
        r2 = r2.replace(prior, row)
f2 = f.replace(next(line for line in f.splitlines() if line.startswith('- **Needs:**')), draft('feedback').strip())
w = lambda s: len(s.split())
h = Path(host).read_text()
hw = sum(w(k + h.split(k, 1)[1].split('\n## ', 1)[0]) for k in ['## Connected hosts', '## Agents', '## Waiting', '## CLI semantics'])
pairs = {'extensions/peers/EXTENSION.md': (p,p2), 'extensions/paseo/EXTENSION.md': (x,x2), 'references/sd/adoption.md': (a,a2), 'README.md': (r,r2), 'extensions/fo-feedback/EXTENSION.md': (f,f2)}
assert x.split('## Codex workers through Paseo', 1)[1] == x2.split('## Codex workers through Paseo', 1)[1]
print(json.dumps({'files': {k: [w(v[0]),w(v[1])] for k,v in pairs.items()}, 'host': hw, 'unlisted': [w(p)+hw,w(p2)+hw], 'listed': [w(p+x)+hw,w(p2+x2)+hw]}, indent=2))
```

### Design-stage verification receipts

The common-fixture reproduction program (unchanged from cycle 1) is retained below. Run it with Python 3 -B, the dispatched kc-dev-flow-2 package root and Spacedock plugin root; its fixtures use disposable temporary repositories and fake provider results. Current run exit 0; losing observer refusal or the successful delivery fixture changes/fails its recorded outputs. A fixture result proves the measured control text, not an actual merge or native callback.

```python
import sys, importlib.util, subprocess, json, re
from pathlib import Path
P=Path(sys.argv[1]); SD=Path(sys.argv[2])
spec=importlib.util.spec_from_file_location('fixtures',P/'scripts/test_pr_watch.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
f=m.TasksTests();f.setUp()
out={}
try:
 f.readme('learn, peers, paseo');
 (f.workflow/'README.md').write_text((f.workflow/'README.md').read_text().replace('entity-type: task','entity-type: task\ntrunk: main'))
 f.task('some-task',pr='o/r#7')
 for label,args in [('tasks-pending',m.view()),('tasks-green',m.view())]:
  if label=='tasks-pending':args['statusCheckRollup']=[{'status':'IN_PROGRESS','conclusion':None}]
  code,lines=f.tasks({'pr view 7':args});assert code==0,(code,lines);out[label]='\n'.join(lines)
 wait=m.PrWatchTests()
 for label,snap in [('wait-green',m.snap()),('wait-merged',m.snap(state='MERGED'))]:
  wait.run_main(['add','o/r#1'],[m.snap(checks='pending')],f.root/(label+'.json'))
  code,o=wait.run_main(['wait','1'],[snap],f.root/(label+'.json'));assert code==0;out[label]=o
 code,lines=f.tasks({'pr view 7':m.view('MERGED')});assert code==0;out['tasks-missing']='\n'.join(lines)
 f.report('some-task');code,lines=f.tasks({'pr view 7':m.view('MERGED')});assert code==0;out['tasks-rerun']='\n'.join(lines)
 out['after-lines']='\n'.join(l for l in lines if l.startswith('after pr-merge:'))
 (f.state/'_archive').mkdir();f.git(f.state,'mv','some-task.md','_archive/some-task.md');f.git(f.state,'mv','some-task','_archive/some-task');f.git(f.state,'commit','-qm','archive')
 d=subprocess.run([sys.executable,'-B',str(P/'scripts/observer_check.py'),str(f.state),'some-task'],capture_output=True,text=True);assert d.returncode==0,d.stdout;out['observer-archived']=d.stdout
 gs=importlib.util.spec_from_file_location('gatefixtures',P/'scripts/test_delivery_gate.py')
 gm=importlib.util.module_from_spec(gs);gs.loader.exec_module(gm)
 code,o=gm.DeliveryGateTests().check()
 assert code==0,(code,o)
 out['gate']=o;out['gate-exit']=str(code)
 def sec(t,h):return h+t.split(h,1)[1].split('\n## ',1)[0]
 wf=(P/'references/sd/workflow.md').read_text();mod=(P/'references/sd/mods/kc-dev-flow-2.md').read_text();pm=(SD/'mods/pr-merge.md').read_text()
 stat={'startup-hook':sec(pm,'## Hook: startup'),'idle-hook':sec(pm,'## Hook: idle'),'mod':mod,'authority':sec(wf,'## Delivery authority'),'extensions':sec(wf,'## Extensions'),'learn':(P/'extensions/learn/EXTENSION.md').read_text()}
 w=lambda x:len(x.split())
 total=lambda st,ot:sum(w(stat[k]) for k in st)+sum(w(out[k]) for k in ot)
 rows={
 'startup':total(['startup-hook','mod'],['tasks-pending']),
 'idle-open':total(['idle-hook','mod','authority'],['tasks-green','wait-green']),
 'idle-merged':total(['idle-hook','mod','authority','learn'],['wait-merged','tasks-missing','tasks-rerun']),
 'after-archive':total(['mod','learn'],['after-lines','observer-archived']),
 'merge-ask':total(['authority','extensions'],['wait-green','gate']),
 }
 result={'static-words':{k:w(v) for k,v in stat.items()},'output-words':{k:w(v) for k,v in out.items() if k!='gate-exit'},'common-totals':rows,'outputs':out}
 # JSON is printed below; no persistent output path is required.
 print(json.dumps(result,indent=2))
finally:f.doCleanups()
```

Current design check: the dispatched `design_surfaces.py check` printed `peers-paseo-rule-matches-practice.md: design surfaces presentable`, exit 0. Independent reconstruction from the task blocks matched all five complete-file counts and both exchange routes; a missing row or stale paragraph changes the comparison. The unchanged common fixture program reran exit 0.

Mermaid 11.16.1 and Playwright 1.62.1 with supported Chrome rendered the final graph (19 nodes, SVG 50,973 bytes) and its actors, routing, single deferral, quiet/callback branches, notice/result exits and failure stop were visually inspected. The sandbox browser launch failed; the permitted local-browser retry succeeded. Scratch outputs `/private/tmp/peers-practice-cycle2/policy.svg` and `.png` are disposable; the durable diagram source is above. A fresh reviewer supplies these declared render versions/browser; no package dependency is added. Frontmatter and the earlier Stage Report were compared byte-for-byte unchanged. Native messaging/error behavior and final candidate checks remain unverified.

### Batch overlap

Implementation file set: `kc-dev-flow-2/extensions/peers/EXTENSION.md` (Paseo binding), `kc-dev-flow-2/extensions/paseo/EXTENSION.md` (pre-worker text and transferred status pointer), `kc-dev-flow-2/references/sd/adoption.md` (peer/worker distinction and redundant prerequisite), `kc-dev-flow-2/README.md` (peers/paseo table rows), `kc-dev-flow-2/extensions/fo-feedback/EXTENSION.md` (Needs only), and a new `docs/adr/<FO-reserved-number>-confirmed-paseo-transport-permits-peer-asks.md`. There is no known ADR index file; the number namespace is shared. No source branch, product commit, adopter file, CI, hook or new executable check is written in this ideation.

| Batch/live task (routing slug; purpose) | Same file/check or shared namespace; ordering |
| --- | --- |
| batch10-after-release-obligations — post-release repairs/proof | No direct file overlap: dispatch/laws scripts and VALIDATION.md, plus state pin/proof. Shared release timing and ADR reservation namespace; its native worker proof is not this native peer proof. |
| names-check-says-what-it-skipped — dispatch diagnostics | No direct file overlap: dispatch/laws tests, workflow/lint/dispatch checks. Their changed fixture output requires recount; no diagnostic changes here. |
| peers-paseo-rule-matches-practice — this peer transport policy | Sole owner of the five package paths above except the sibling's distinct shared peers section; owns new ADR and native ask/reply/notice/failure acceptance. |
| peer-status-reaches-fresh — current peer facts | Shared peers file and replay cases. Sibling owns Current peer facts and fresh-FO loading proof; this task alone carries the deleted sibling paseo insertion. Apply both without overwriting shared text; sibling natural-use sample is after delivery. |
| model-roster-per-repo — per-role model choice | Direct overlap: README.md, adoption.md, paseo EXTENSION.md; shared lint and ADR namespace. Serialize/rebase those hunks and recount the final corpus. Peer rules never activate its worker policy. |
| paseo-human-surfaces-visible-and-reachable — human terminals/tabs | Direct overlap: paseo full file and word ledger. Its worker/surface changes remain its own; this task preserves current worker bytes. |
| adoption-asks-which-extensions — historical selection checks | Its narrowed design changes dispatch_records/number_guards/tests/laws, not adoption.md. No direct file overlap; do not reopen adoption defaults here. |
| adr-required-statement — decision evidence at completion | No extension overlap; shared ADR number namespace and eventual ADR/report checks. Current local status validation; its owner retains the task. |
| adr-silent-undo-probe — fictional ADR refactor trial | No overlap: archived harness/scenario; no product policy or number allocation here. |
| comment-check-reaches-delivery-gate — report comment evidence | No direct overlap: delivery_gate/tests/validation principles. Rerun control-output fixture if its output changes. |
| journey-canvas-hosted-poc — hosted canvas direction | No direct overlap: journey hosting artifacts; shared ADR namespace if a decision is later recorded. |
| journey-server-host-pilot — private server adapters | No direct package overlap. Top-level entity absent locally; newest available validation-10 dispatch addresses cwd-dependent local acceptance only, so live ownership beyond those records remains unverified. Shared ADR namespace only. |
| ops-inbox-r1-setup-and-isolation — signed event intake | No product overlap: kc-ops-inbox, its CI and ADRs; shared ADR namespace. Held go-live notices stay held; a relaxed transport prerequisite supplies no send/action grant. |
| pr-review-lite-value-pilot — bounded review trial | No direct overlap: kc-pr-flow and trial state in its own worktree; no experimental or model-run authority transfers here. |

Recommended order: this task owns one coherent Paseo/notice wording change; integrate sibling Current peer facts once and require its own fresh-FO test. Serialize paseo/README/adoption edits with roster and human-surface owners, then recount combined bytes. Other-script tasks may proceed independently; refresh fixtures if their outputs land. FO reserves the ADR, checks live PR ownership (unavailable here), and dispatches implementation under the existing revise grant; no extra sitting if the design remains within the asks. Normal published upgrade reaches adopters without enabling paseo. Native ask/reply/notice/failure proof precedes this task's validation pass; the sibling's natural-use proof follows delivery.

## Acceptance criteria

**AC-1 — Confirmed transport, not listing, permits peer asks.** Evidence: at exact base/candidate, run fresh policy replay for listed/unlisted/declined/no-answer Paseo, non-Paseo, absent skill, unknown destination and qnow's Captain-named question. Log loaded files, identity/authority decisions and intended sends. Confirm no optional-extension activation and no special named-ask exception; adoption list bytes unchanged. Falsifier: unlisted confirmed-Paseo ask is refused solely for missing paseo, non-Paseo users acquire Paseo requirements, or worker/fo-feedback authority turns on with a message. Current evidence: revised text/source/adopter reads; no candidate behavior or native success yet.

**AC-2 — Existing authority and every round-004 event retain a path or stated stop.** Evidence: independent reviewer maps every numbered answer, qnow worker answer, disclosure and comparison to the full revised replay above. Exercise relayed authority, wrong area, busy/unknown status, known-unavailable steer, one natural recheck, missing return route and duplicate/unrelated reply. Falsifier: qnow still has no path, a peer quote grants action authority, an unknown/busy new send proceeds, explicit interrupt appears, or the five-minute deadline resets. Current evidence: complete prospective table and primary host semantics; historical missing facts remain unknown, not newly compliant.

**AC-3 — Real two-agent ask, reply and notice are observed before validation passes.** Evidence: on the exact candidate, FO binds one authorized pair; validator retains actual confirmed server/agent identities, explicit steer/notify false calls, receipt and recipient-side ask, one sourced reply matched once, and one no-ack notice. Separate queue receipt, delivery, answer and authority. Falsifier: recorder-only proof, guessed recipient, list-gated ask, callback counted as the explicit answer, duplicate handling causes another action, or worker notifications are disabled. Current: Captain's gate explicitly authorizes the bounded validation; no live experiment in this ideation. Missing host access holds this criterion; do not substitute the sibling's post-delivery observation.

**AC-4 — Quiet sends do not silently lose peer errors or permission holds.** Evidence: use the same authorized real pair and a safe supported failure/hold route; compare actual receiver failure with sender-visible notification/activity and attended unresolved-exchange reconciliation while false. Preserve error/hold source and reporting time; silence stays unresolved. Include unavailable return route, duplicate/no-action finish and a normal worker signal as separate controls. Falsifier: errored peer becomes invisible, no way to distinguish unresolved/failure from success, or a hold is bypassed. Current: primary docs/schema show callbacks also carry errors/holds, so this is explicitly unverified and may fail. If untestable or failed, return evidence to FO and hold quiet-send acceptance; do not invent host changes, polling or a new default under this design.

**AC-5 — One owner carries compatible status wording.** Evidence: diff final files against both revised tasks: this task contains Paseo notice classification/flags/no-ack/error distinction; sibling contains only its shared Current peer facts rule and no duplicate paseo insertion. Exercise same-question correction versus new notice, held go-live, stale or duplicate status and source-unavailable cases using the sibling's accepted source rules. Falsifier: old listing restriction survives in any entry/prerequisite, duplicate sibling pointer lands, freshness bypasses send authority, or a no-action finish generates Captain work while an error is discarded. Current: sibling file and newest gate read; no sibling edits. Its fresh-FO loading and after-delivery real-use checks remain separately owned and unverified here.

**AC-6 — Point-of-use cost and existing orchestration remain visible.** Evidence: independently reproduce complete draft/shipped-file counts and the five common fixture rows; capture real source/error/message word addends in AC-3/AC-4; recount combined sibling/roster/surface changes once. Run shipped design_surfaces.py check, render/inspect final Mermaid; at implementation run existing lint-skills.py and applicable test_lint_skills.py/test_sd_dispatch.py with the declared Spacedock root, and verify worker section/defaults/template unchanged by this task. Verify the new FO-reserved ADR records the actual ruling without rewriting 0038. Falsifier: measuring only one shrinking file, omitting moved/status/output words, stale count treated as final, missing graph branch/criterion, disabled worker signal, guessed ADR number, or changed sibling/frontmatter. Current: draft counts and common fixtures measured; final candidate/native/ADR evidence still pending.

## Stage Report: ideation

- DONE: A design for making the peers rule on new Paseo asks match practice, comparing listing paseo in adopters whose peers run inside Paseo against relaxing the clause, including default steer and finish-notice behaviour and a Captain-named outbound ask; each round-004 event in .notes/fo-feedback/round-004.md replayed as allowed or refused by a stated rule; the choice returned as a Captain decision with a recommendation
  Design compares both options; recommends explicit routine selection plus direct named one-off exception, explicit steer/false and one deliberate callback escape; round table maps every recorded section without retroactive compliance.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (batch10-after-release-obligations, names-check-says-what-it-skipped, peers-paseo-rule-matches-practice, peer-status-reaches-fresh, model-roster-per-repo, paseo-human-surfaces-visible-and-reachable) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Three extension/adoption paths plus future reserved ADR; direct shared edits with status/model/surface tasks, all named siblings classified, adopter sync separate; no sibling changed.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Embedded recount and shipped scratch fixtures ran exit 0: listed-exchange startup 2416→2391, idle/open 2646→2621, idle/merged 2995→2970, archive 2345→2320, merge ask 2977→2952; unlisted policy +155 and adoption +66, with corpus/output limits stated.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Six criteria separately name evidence/falsifiers; one coupled policy decision returns to Captain, with adoption effort, worker-policy effect and increased unlisted reading disclosed.
- DONE: AC-1 design evidence and limit
  Pinned 0.33.1 source plus read-only relay/web/qnow refs confirm the list gap; future selection replay fails on auto-enable or unsolicited unlisted send; candidate/adopter behavior not verified.
- DONE: AC-2 design evidence and limit
  Proposed named-question rule permits qnow's exact reported case; falsifiers substitute relayed authority, recipient or question; no native send performed.
- DONE: AC-3 design evidence and limit
  Live tool schema and exercised CLI help expose steer/default callbacks and no callback-disable CLI flag; omitted flags, deadline reset or unrelated finish fail the proposed replay; delivery behavior remains unverified.
- DONE: AC-4 design evidence and limit
  Round-004 table covers five FOs, worker complaints, interview disclosure and evidence limits; an omitted event or retroactive authorization fails it; peer-session originals and independent replay not read/run.
- DONE: AC-5 design evidence and limit
  Draft recount and five routine control-text fixture counts executed; eight installed measurement inputs match pinned main bytes; falsifier is hidden moved text/output; complete live-session totals and notification savings remain unmeasured.
- DONE: AC-6 design-stage evidence and implementation limit
  design_surfaces.py check: "peers-paseo-rule-matches-practice.md: design surfaces presentable", exit 0; current Mermaid rendered/visually read (19 nodes); original 55 lines/frontmatter preserved; no product test, ADR reservation or adoption performed.
- SKIPPED: Live GitHub pull-request inventory and native peer-send trial
  gh pr list failed "error connecting to api.github.com"; dispatch prohibits other-session messages. Existing native defaults are documented, not experimentally certified here.

### Summary

Pilot ideation only: the design, Mermaid, full event replay, reproducible word ledger, six acceptance criteria and overlap ordering are in this entity. Recommendation awaits the Captain; package code, adopter READMEs and task frontmatter remain unchanged, and no implementation, live delivery or rollout is claimed. This state-only report must be path-scoped committed/synced before handback; FO retains gate and implementation dispatch ownership.

## Stage Report: ideation (cycle 2)

- DONE: Revise the design under the Captain's ideation-gate revise of 2026-10-30 (「准」); the asks are in this task's newest ideation gate question (review/ideation, newest briefing); do exactly those asks, update criteria and the stop condition to match, and name anything that would go beyond them as a return to FO rather than designing it; this task now carries the peer-status text under one owner, so coordinate the wording with peer-status-reaches-fresh by reading its task file
  Latest gate and Captain 「准」 govern: confirmed-Paseo asks need no listing; new unnumbered ADR reverses only 0038 listing choice; native ask/reply/notice and failure visibility stay validation obligations; sibling paseo text has this sole owner.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (batch10-after-release-obligations, names-check-says-what-it-skipped, peers-paseo-rule-matches-practice, peer-status-reaches-fresh, model-roster-per-repo, paseo-human-surfaces-visible-and-reachable) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Five package paths plus new FO-reserved ADR enumerated; every named task read/classified, journey-server limited to available dispatch records; shared peers/paseo/adoption/README hunks require ordered integration and recount; sibling unchanged.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Independent reconstruction plus rerun control-text fixtures passed: listed startup 2416→2477, idle/open 2646→2707, idle/merged 2995→3056, archive 2345→2406, merge ask 2977→3038; unlisted +234, listed +61; real output costs remain unmeasured.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Six criteria separately state evidence and falsifiers; no unresolved in-scope choice remains after the grant; native failure or broader mechanism change returns to FO, without a worker-invented remedy.
- DONE: AC-1 design evidence and limit
  Current source/adopter refs and full draft remove the listing prerequisite; future replay fails on unlisted refusal or accidental worker activation. Actual candidate/native behavior is not yet verified.
- DONE: AC-2 design evidence and limit
  Round-004 was reread and every event row revised; busy/authority/source stops retained. Independent replay must fail on omitted events, deadline reset or historical unknowns promoted to approval; not yet run.
- DONE: AC-3 design evidence and limit
  Gate explicitly authorizes one real two-agent ask/reply/notice during validation; exact pair, arguments and both-side receipt/answer evidence required. Recorder-only success fails; no live send performed in this stage.
- DONE: AC-4 design evidence and limit
  Paseo primary docs/schema confirm callbacks carry errors/holds; false-mode visibility remains unverified. A hidden error or unavailable safe failure route holds acceptance and returns to FO, not success.
- DONE: AC-5 design evidence and limit
  Read sibling task and newest revise question; only this task carries its Paseo insertion, while sibling owns shared freshness, fresh-FO test and after-delivery observation. Duplicate/contradictory wording fails integration; sibling bytes untouched.
- DONE: AC-6 current-stage proof and implementation limit
  design_surfaces.py check: design surfaces presentable, exit 0; independent five-file counts match, worker section unchanged, common fixtures exit 0, Mermaid rendered/visually inspected. Product lint/native behavior/new ADR remain future checks; frontmatter and old report preserved.
- SKIPPED: Live GitHub pull-request inventory
  gh pr list failed error connecting to api.github.com; local git/state/adopter sources used and live overlap remains unverified.
- SKIPPED: Product implementation, native peer traffic and sibling/adopter changes
  Ideation writes only this entity body/report; the Captain-authorized native check belongs to validation, while this dispatch prohibits other-session messages.

### Summary

Revised Pilot design implements the exact 2026-10-30 revise direction: transport-based peer permission, no listing campaign or named exception, one owner for Paseo status wording, a new ADR at implementation, and real native/failure proof before validation passes. The previous report and frontmatter remain unchanged; no host, product, adopter or sibling mutation occurred. FO retains transition ownership under the existing grant; hidden-error evidence or any broader redesign returns to FO.
