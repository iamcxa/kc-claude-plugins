---
title: A peer FO's status reaches other FOs fresh, so a stale line is not relayed to the Captain
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:peer-status-reaches-fresh:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:peer-status-reaches-fresh-backlog-1
              briefing:
                id: briefing:peer-status-reaches-fresh:backlog:attempt-1:revision-1
                digest: sha256:fab4edc4bff6684565f1a88b14d19171662102bf71f1305a2d93f6b1874ba04d
                room-ref: ./peer-status-reaches-fresh/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:peer-status-reaches-fresh:backlog:1
                briefing: briefing:peer-status-reaches-fresh:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-30T08:18:32.199545Z"
                decision: approve
                reason: The Captain 「對，全准且全確認」 (chat, 2026-10-30), answering FO's joint batch-11 backlog sitting of six gates whose ask was 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」; accepts FO's recommendation and the confirmations stated in the gate question.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:peer-status-reaches-fresh:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:peer-status-reaches-fresh-ideation-1
              briefing:
                id: briefing:peer-status-reaches-fresh:ideation:attempt-1:revision-1
                digest: sha256:3e50dff325abef10e54c5ae07c48421c8ed1f1c1a48faa6b17c25dec6c108313
                room-ref: ./peer-status-reaches-fresh/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:peer-status-reaches-fresh:ideation:1
                briefing: briefing:peer-status-reaches-fresh:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-30T09:31:42.445165Z"
                decision: revise
                reason: The Captain 「准」 (chat, 2026-10-30), answering FO's joint batch-11 ideation sitting of six gates whose ask was 「決定：六張全照建議，同意放寬 Paseo 規則和真實測試，並授權改完直接進實作？要改哪張直接說。」; accepts the direction and the revise asks named in this gate's question, and grants that a revised design staying within those asks goes to implementation without another sitting.
            - id: gate-attempt:peer-status-reaches-fresh-ideation-2
              briefing:
                id: briefing:peer-status-reaches-fresh:ideation:attempt-2:revision-1
                digest: sha256:1f0c1cb4c661bd69e5d9a8619ca239dfb547af6d2437a4f3a6ae5591c22cdb35
                room-ref: ./peer-status-reaches-fresh/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:peer-status-reaches-fresh:ideation:2
                briefing: briefing:peer-status-reaches-fresh:ideation:attempt-2:revision-1
                by: agent:first-officer
                at: "2026-10-30T10:00:25.221662Z"
                decision: approve
                reason: 'FO read the newest ideation report: the revision applies the 2026-10-30 revise asks, names no new Captain choice and returns anything wider to FO; the design check passes.'
                conn:
                    quote: 決定：六張全照建議，同意放寬 Paseo 規則和真實測試，並授權改完直接進實作？要改哪張直接說。 — 准
                    source: the Captain, chat, 2026-10-30, FO's joint batch-11 ideation sitting
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-30T10:12:16Z
worktree: .worktrees/spacedock-ensign-peer-status-reaches-fresh
pr: iamcxa/kc-claude-plugins#756
---

## Scope

- Source: interview round 004 finding (state .notes/fo-feedback/round-004.md, 2026-10-28), proposed by FO; the Captain chose theme B for batch 11 (「那就 B 可以」, chat, 2026-10-30), whose row named 「FO 之間狀態過期」.
- Bite: on 2026-10-28 relay told the Captain Web's half waited on his merge after it had merged (b71f912), and web's status named a v0 step CL had already cleared; web corrected relay twice. Their originals sit in their sessions; this is the two-sided account.
- Upstream first: `extensions/peers/EXTENSION.md`, `extensions/paseo/EXTENSION.md`, Paseo agent labels (next, next-owner).

## Non-goals

- A shared status store or a new service; receipts for every message.

## Budget

- One package PR changing only the shared Current peer facts section in `kc-dev-flow-2/extensions/peers/EXTENSION.md`; no new script. `peers-paseo-rule-matches-practice` owns all Paseo binding/notice wording. Natural-use observation follows delivery.

## Stop condition

- Before delivery, the two admitted 2026-10-28 events replay as prevented: AC-1 begins with an FO that has not read peers and proves normal point-of-use loading before the source query/report; AC-2 preserves the boundary between an authorization and a completed release. Complete AC-3, AC-5 and AC-6 at their designated stages. A preloaded-rule replay is insufficient.
- If the cold FO never loads peers, or a required replay/source/transport check fails, stop the dependent acceptance and return evidence to FO. Do not design or implement a startup preload, new hook, watchdog, script, host repair or broader send permission here.
- AC-4 is explicitly after delivery: FO retains the observation obligation in the existing task/exchange record and observes the first natural transition after normal adoption. No event or unavailable authority means not run, not acceptance and not a pre-delivery hold. Do not delay delivery waiting for a natural event or claim real-use proof from fixtures.

## FO alignment

Alignment: not needed before ideation: text inside the extensions' existing authority.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-30 — batch-11 review before the joint ideation sitting: approve, revise, split or hold each task, the Captain's decisions, overlap and order
Reviewer: kc-dev-flow-2:engineering-reviewer gpt-6-astra 2026-10-30 — does amendment 1 withdraw what the Captain approved, and what changes in the build?
Reviewer: kc-dev-flow-2:engineering-reviewer gpt-6-astra 2026-10-31 — does amendment 2 withdraw what the Captain approved, and what changes in the build?

## Design

### PRFAQ

**Proposition — proposed, not implemented.** A First Officer (FO, workflow coordinator) stops repeating another project's cleared Captain action. Before naming that action in a status or gate question, the receiving FO checks the action's original source in the current reporting turn. The originating FO sends a short, sourced change notice to previously involved peers when its own merge, release or unblock changes their next step; every relayed status carries its observation time. These are instructions for existing hosts, not an enforced freshness service.

**Who uses it?** FOs already exchanging a dependency fact, including relay and web in the two admitted 2026-10-28 incidents. One integrated slice runs from source transition through a permitted notice or missing notice to a checked Captain-facing statement. There is no shared status store, new script, timer, fleet broadcast, delivery guarantee, extra gate or background service. No claim is made that every historical status becomes current.

**Why all three measures?** A push reduces the time peers hold an obsolete fact, but can be unavailable, deferred or lost. An observation time shows the age of a fact, but a one-second-old fact can already be wrong. A source check directly answers whether the Captain still owes that particular action; if unavailable, the FO reports uncertainty without assigning the action. Use all three with the source check as the necessary condition for relaying an action, not a time-to-live heuristic.

| Option | Useful effect | Failure and cost |
| --- | --- | --- |
| Push changes only | Involved peers learn merged/released/unblocked early | A lost, held or out-of-order notice leaves the old action; creates sends |
| Observation time only | Makes old observations visible | Age alone does not determine validity; adds a few words |
| Check action at source only | A missing notice cannot justify a stale Captain request | A source read per reporting turn; unavailable source leaves uncertainty |
| Recommended combination | Checked action plus faster bounded updates and visible age | Adds reading and notices; remains a human/agent policy, not a delivery guarantee |

**What does “fresh” mean here?** The reader queried the relevant original source during the turn composing the statement, after processing relevant received changes. Show an ISO 8601 observation time with timezone and source revision/link. Do not substitute send time, an old pasted `as of`, a display label or another FO's finish timestamp. A subsequent concurrent change can still race this observation; report the observation rather than a timeless guarantee. Read once per unchanged source within that composing turn; a conflicting notice requires another check before using it.

**Which source?** For merge, the repository-qualified pull request (PR) state and merged revision; a local commit's presence does not prove hosted merge. For release, the actual tag/release or installation evidence relevant to the claim; merged does not mean released. For an unblock, the blocking task or original decision and the exact question it settled. An original authorization clearing a token-rotation step does not prove the credential changed or a release shipped; do not read secrets. Keep separate remaining steps separate. Missing access or disagreement yields `unverified as of <time>: <source gap>` and an FO-owned check, not “Captain must do X.” Existing Captain-source rules still apply to any authority claim.

### Captain revise and ownership

The 2026-10-30 ideation resolution at 09:31:42.445165Z records the Captain's 「准」 to the joint sitting. Its newest `peer-status-reaches-fresh/review/ideation/briefing-1/index.json` asks exactly: delete the paseo insertion and let `peers-paseo-rule-matches-practice` carry it under one owner; start AC-1 with an FO that has not read peers because startup does not preload it; move AC-4 after delivery. The resolution permits FO to move a design staying within those asks to implementation without another sitting. This worker neither applies that transition nor grants acceptance.

This cycle replaces the active design/criteria while preserving the entire earlier Stage Report. That report's two-file plan, reading totals, unlisted-send restriction and pre-delivery natural-use requirement are historical, not this cycle's instructions. The sibling's cycle-2 design at state commit `da23dd127b929a0d580fa181ce1c3d8879fc71d6` owns all Paseo-specific wording, including the transferred notice pointer, confirmed-transport permission without optional paseo listing, send flags and quiet-mode failure visibility. This task retains only transport-neutral Current peer facts and its loading/freshness proof. No duplicate paseo insertion is proposed.

### Upstream chain and current evidence

Read order this cycle: Spacedock 0.27.3 ensign/shared/Codex contract and first-officer shared/Codex runtime, then kc-dev-flow-2 framework/profile and source, then sibling adopters. Spacedock owns state, gates, dispatch and worker completion verification. Its boot marks counts possibly stale and does not preload peers. No worker notification or dispatch change is proposed.

`git fetch origin` succeeded. `origin/main` is `a6612948936a4f075625147b21aabd3b10b19eee`; `kc-dev-flow-2/.claude-plugin/plugin.json` is **0.33.1**. Source was read with `git show`; stage checks use `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1`. The unrelated colombo branch `iamcxa/trim-kc-dev-flow-third` has pre-existing `.gitignore` and `.gstack/browse-startup-error.log` changes, preserved. The only writable durable artifact here is this entity body in the dispatched split-root state checkout on `spacedock-state/dev2`.

Bounded existing-capability check: required peers already checks cited sources, preserves original human authority, records exchanges and bounds busy-peer deferral; the package README routes it before opening a task or exchanging peer facts. The workflow Extensions section requires following listed extensions at their due steps. Neither this source read nor a keyword proves an FO composing a status discovers the rule. AC-1 therefore measures that entry path from a cold FO, without preloading peers or hinting its path. If it fails, return the loading gap to FO; no entry-point repair is designed here. The new content adds current-turn timing, sourced observation and bounded transition corrections to the existing mechanism.

Paseo primary evidence is its own `/Users/kent/.agents/skills/paseo/SKILL.md`, especially Connected hosts, Agents, Waiting and CLI semantics: queued sends are not answers, steering may fall back to interruption, and completion callbacks also carry errors/permission requests. Labels are display hints, not proof that a Captain action remains owed. The sibling owns callback policy and its authorized native failure-visibility test; this design supplies no alternative transport or silence-is-success rule. No sends, labels or native trials ran in this ideation.

Read-only local origin/main snapshots, not newly fetched remote truth: relay `/Users/kent/conductor/workspaces/subspace-relay/beirut-dev2` `a448ea34391653fc71b0760c048f29c781fbe50a`; web `/Users/kent/conductor/workspaces/subspace-web/dev2-fo` `f2e1a4ccce8af1d9ab4ffb6591f8c84ff18d619a`; qnow `/Users/kent/conductor/repos/qnow-adopt-dev2` `f364b6e8bfa072db46374dccfcc566d10667cf40`. Relay/web `docs/dev2/README.md` and qnow `docs/dev2-poc/README.md` list peers and omit paseo. After the sibling's published policy is adopted, omission no longer blocks confirmed-Paseo peer messaging; it still does not enable optional worker procedures. No adopter edit or listing campaign is proposed.

`gh pr list --repo iamcxa/kc-claude-plugins --state open --limit 100 --json number,title,headRefName` failed this cycle: `error connecting to api.github.com`. Current open PR ownership is unverified; FO must reconcile it before implementation. Local state and git evidence remain usable. Round-004's relay/web accounts were reread; historical original sessions remain unread, so the two incidents are admitted replay inputs, not independently authenticated history.

Read accepted Architecture Decision Records (ADRs, durable repository rulings) 0011, 0020, 0035, 0038 and 0042 at the pinned source; relevant task/gate records show no contrary Override. ADR 0038's existing listing restriction is superseded only through the sibling's new Captain-authorized ADR, owned there. This task requires no ADR number/index, workflow budget change or new permission. Preserve human authority, non-Paseo routes and worker completion.

### Reviewable extension text

Proposed exact insertion in `kc-dev-flow-2/extensions/peers/EXTENSION.md`, immediately before `## Claude Code binding`. Keep existing transport, record, authority and deferral text. All text below is candidate wording, not an already adopted instruction.

<!-- candidate-fresh-peers-start -->
```markdown
## Current peer facts

A relayed status names its source and observation time with timezone. Before naming a Captain action from a peer, check that action at its original source in the current reporting turn, after relevant notices. A label, timestamp, queued receipt or finish notice is not that check. If inaccessible or conflicting, mark the fact unverified and keep the check with FO; do not assign the Captain the unverified action. A merge proves neither release nor another step's completion.

When your verified merge, release or unblock changes a previously involved peer's next step, record the changed fact, source revision, observation time and affected exchange in the existing task or peer-exchanges note. Send one information-only correction to those confirmed peers through the authorized binding; no broadcast. A correction answering the same question follows its reply route; a new notice needs new-send authority. If held, unavailable or uncertain, record the unsent or uncertain notice and reason; do not infer delivery or retry automatically. At the next attended resume, reconcile pending notices before any authorized send. No timer or background retry is added.

On receipt, match the source and exchange, check before using the fact, and update the affected status at its next authorized write. Duplicates or older observations do not restore a stale action; conflicting or unordered evidence requires a source check. Preserve a bound briefing and record the correction in the existing note. Do not send receipt-only acknowledgements or surface a no-action peer finish to the Captain; report a material change, blocker or decision instead. Worker completion follows its own contract.
```
<!-- candidate-fresh-peers-end -->

**Paseo wording has one owner.** This design contains no candidate paseo block and changes no Paseo binding. The sibling's current candidate carries the status pointer in its peers Paseo binding and optional paseo pre-worker text. Integrate that owner first, then this shared peers insertion once; reconstruct/recount the combined bytes. Its chosen transport permits confirmed-Paseo asks and notices without listing the optional extension, while retaining identity, authority, idle/deferral and requested-reply rules. No listing exception, callback default or native failure remedy is independently designed here. If that sibling cannot deliver its chosen policy, FO reconciles the dependency; do not silently retain its superseded restriction or transplant its text into this task.

### Sequence and stops

```mermaid
flowchart TD
    O[Origin FO verifies merge, release or unblock] --> R[Record source, observation time and affected exchange]
    R --> A{Existing binding permits notice?}
    A -->|no or uncertain| H[Record held or uncertain; no automatic retry]
    A -->|yes| N[Send one scoped notice through sibling-owned policy]
    N --> I[Receiver matches source and exchange; holds correction until checked]
    I --> F[FO composes peer-derived status or Captain action]
    H --> F
    L[Old peer line; notice absent or delayed] --> F
    F --> B[Cold FO follows ordinary workflow entry; peers not preloaded]
    B --> C{Loads peers before relying on peer fact?}
    C -->|no| X[Acceptance fails; return loading gap to FO]
    C -->|yes| J{Names a Captain action?}
    J -->|no| T[Check fact before use; report source and observation time or uncertainty]
    J -->|yes| S[Read original action source in this turn]
    S --> D{Source result?}
    D -->|still pending| P[Report sourced action and time; preserve Captain gate]
    D -->|cleared| E[Remove only cleared action; report source and time]
    D -->|unavailable or conflicting| V[Mark unverified; FO owns check; no stale Captain request]
```

The cold-entry nodes describe the AC-1 proof obligation, not a runtime guard or new loading mechanism. A warm FO can reuse already-read policy; the source observation still must belong to this composing turn, with recheck after conflicting changes. A status without a Captain action still names its source and observation time, and an unverified fact stays marked unverified.

The binding retains the five-minute ceiling, one natural recheck and stop without independent work. A same-question correction uses the requested-reply route; a new notice uses the new-send route. On receipt, duplicates/older observations do not restore stale actions; conflicting evidence triggers a source read. No receipt-only acknowledgement or no-action Captain reply is due, but errors/permission holds remain material under the sibling's policy. Do not edit a bound briefing, infer delivery, retry automatically or turn an observation into gate authority. These rules govern existing records, not a durable notice service.

### Two admitted incidents replayed as prevented

These are policy walkthroughs of `.notes/fo-feedback/round-004.md`, not new original-session or native messaging evidence. Times below are placeholders to be filled from the actual read, not invented historical timestamps.

| Incident and admitted input | Proposed execution and observable result | Falsifier |
| --- | --- | --- |
| 2026-10-28: relay repeats Web “waits on your merge / Review approval”; Web #186 had merged at b71f912, correction reference 81dc0663 | Web verifies its merge, records a sourced correction for the existing relay exchange, and sends if permitted. Even if absent/delayed, relay queries `spacedock-dev/subspace-web` PR 186 before the Captain request; a merged result removes only that merge/approval action and reports `as of <observed time>`. | Relay outputs the old action after reading MERGED, or trusts the timestamp/label without a query. If the provider is unreachable it must say unverified, not ask Captain to merge. |
| 2026-10-28: web still says “v0 0.16.2 等 CL 換 token” after the relevant authorization cleared that step (CL is the operator named in the account) | Originating FO records the precise unblock and source. Web reads the original authorization plus the question answered, or the authoritative blocking record carrying that source. It removes the cleared CL step; it does not claim token rotation or v0 release complete. If the original is inaccessible, report that source gap and do not repeat the old Captain/CL action as current. | Treating a finish notification as the authorization, assigning the old cleared step, reading a secret to verify it, or turning authorization into a “released” claim. |

A live read of current history cannot prove what a 2026-10-28 actor saw. The source-check rule prevents the admitted false action under the stated replay inputs; behavior by an actual fresh FO remains an implementation/validation proof obligation. Neither adding a phrase nor this diagram proves compliance.

### Decisions and returns to FO

No unresolved material choice remains within the three revise asks. Recommendation: implement the single shared peers insertion, require cold-entry and stale-action proof before delivery, and retain the natural-use observation after delivery as the Captain directed. Costs: extra source reads and explicit unverified outcomes remain; a loading failure can block candidate acceptance; real-use benefit is still unproven at delivery.

Return to FO rather than design here: startup preloading or an entry-path repair if AC-1 fails; changing quiet-mode flags or error surfaces; a watcher, timer, status store, new script or delivery guarantee; host changes, broader send authority, adopter enablement or an ADR beyond the sibling's owned ruling. The sibling's real two-agent transport test remains its pre-delivery obligation; moving this task's AC-4 does not move or waive that test. No second sitting is required for this faithful revision; any broader remedy needs FO to route the new decision.

### Words FO reads at each lifecycle moment

Counts are Python `len(text.split())`, including headings/syntax. The shared peers insertion remains **262** words. This task alone changes peers **805 → 1067** and leaves paseo **562 → 562**; its former 67-word paseo insertion is deleted. With the sibling's current exact blocks, peers is **1039 → 1301**, paseo stays **389**, and primary Paseo skill sections add **607**. Combined unlisted exchange: original **1412 → 1908**; listed full-file exchange: **1974 → 2297**. This task adds **262** to either sibling-only route (1646 or 2035), once. Neither task may count the transferred pointer twice.

The common fixture program was rerun this cycle with the dispatched 0.33.1 package and Spacedock 0.27.3, exit 0. It exercises mocked provider/Spacedock responses in temporary repositories: startup 442, idle/open 672, idle/merged 1021, after archive 371, merge ask 1003. The durable program is the Python block starting `import sys, importlib.util, subprocess, json, re` in `peers-paseo-rule-matches-practice.md` at state commit `da23dd127b929a0d580fa181ce1c3d8879fc71d6`; extract with `git show <commit>:<task>`, run `python3 -B <extracted-program> <package-root> <spacedock-plugin-root>`. Missing observer refusal or a failed delivery fixture changes/fails the outputs. It is a control-text fixture, not live freshness or delivery proof.

| Lifecycle moment | No peer event, original → combined | Listed event, original → sibling only → combined |
| --- | ---: | ---: |
| startup | 442 → 442 | 2416 → 2477 → 2739 |
| idle, open PR | 672 → 672 | 2646 → 2707 → 2969 |
| idle, merged PR / observer refusal and rerun | 1021 → 1021 | 2995 → 3056 → 3318 |
| after archive | 371 → 371 | 2345 → 2406 → 2668 |
| merge ask | 1003 → 1003 | 2977 → 3038 → 3300 |
| unrelated dispatch without peer fact | unchanged | no extra load unless a peer fact is used |

For unlisted exchanges add 1412 before, 1646 sibling-only and 1908 combined to each common row. A fresh FO using peer status pays the due load at that moment, not at an artificial startup preload; AC-1 records which entry/README passages it actually reads. This table is a bounded instruction/output corpus, not entire live-session totals. Add actual source/error response words and changed status/notice words from AC-1/AC-2/AC-3; retain those same addends in the later AC-4 observation. Do not wait for AC-4 to measure pre-delivery replay costs or price unavailable responses as zero. No reading-time, callback-count or runtime saving is claimed. No CI change or measured cost per PR is in scope.

Reproduce exact policy counts with Python 3; pass the pinned git repository, this task, the sibling task extracted from the state commit above, and Paseo's primary skill. Candidate strings are assembled in memory only. Recount after any subsequent sibling/model/surface or control-output change.

```python
import json, subprocess, sys
from pathlib import Path
repo, task, sibling, host = sys.argv[1:5]
base = 'a6612948936a4f075625147b21aabd3b10b19eee'
t, b = Path(task).read_text(), Path(sibling).read_text()
def source(name):
    return subprocess.check_output(['git', '-C', repo, 'show', base + ':kc-dev-flow-2/extensions/' + name + '/EXTENSION.md'], text=True)
def block(text, marker):
    part = text.split('<!-- ' + marker + '-start -->', 1)[1].split('<!-- ' + marker + '-end -->', 1)[0]
    return part.split('```markdown\n', 1)[1].rsplit('```', 1)[0]
p, x = source('peers'), source('paseo')
added = block(t, 'candidate-fresh-peers')
p_s = p.split('## Paseo binding', 1)[0] + block(b, 'candidate-peers') + '\n## Other host binding' + p.split('## Other host binding', 1)[1]
x_s = block(b, 'candidate-paseo') + '\n## Codex workers through Paseo' + x.split('## Codex workers through Paseo', 1)[1]
p_only = p.replace('## Claude Code binding', added + '\n## Claude Code binding', 1)
p_all = p_s.replace('## Claude Code binding', added + '\n## Claude Code binding', 1)
h = Path(host).read_text(); w = lambda z: len(z.split())
hw = sum(w(k + h.split(k, 1)[1].split('\n## ', 1)[0]) for k in ['## Connected hosts', '## Agents', '## Waiting', '## CLI semantics'])
assert '<!-- candidate-fresh-paseo-start -->' not in t.split('## Stage Report:', 1)[0].splitlines()
print(json.dumps({'peers': [w(p),w(p_only),w(p_s),w(p_all)], 'paseo': [w(x),w(x),w(x_s)], 'host': hw, 'added': w(added), 'unlisted': [w(p)+hw,w(p_s)+hw,w(p_all)+hw], 'listed': [w(p+x)+hw,w(p_s+x_s)+hw,w(p_all+x_s)+hw]}, indent=2))
```

### Batch overlap

Proposed product change set: **only `kc-dev-flow-2/extensions/peers/EXTENSION.md`**, inserting the transport-neutral Current peer facts section before Claude Code binding. The sibling is sole owner of the transferred Paseo pointer and all Paseo binding/extension edits. No executable checker, workflow template, ADR file/index, provider setting, adopted README or label schema changes. Runtime exchange records use the existing task or `.notes/peer-exchanges.md` path under the existing authority; they are not new package files. Only this task body is writable in ideation.

| Batch/live task (routing slug; short meaning) | Same file or check; implementation ordering |
| --- | --- |
| batch10-after-release-obligations — post-release proof and repairs | No direct file overlap: laws_check/dispatch_records and native spawn proof. Same release/adopter timing; its evidence is not freshness evidence. |
| names-check-says-what-it-skipped — dispatch diagnostics | No direct file overlap: dispatch_records and its checks. A new freshness paragraph is not a new pre-send diagnostic. |
| peers-paseo-rule-matches-practice — peer send/selection policy | Direct overlap in peers only and peer replay/reading checks. Its cycle-2 ruling permits confirmed-Paseo messaging without optional selection and owns flags, notice pointer, ADR and native failure test. Apply that binding first, then this shared section once; no independent paseo insertion. |
| peer-status-reaches-fresh — this freshness design | Owns one shared peers insertion, cold-FO loading proof, two stale-action replays and post-delivery observation; no sibling state edits. |
| model-roster-per-repo — role model selection | No direct file overlap in its revised eight-file stage-worker slice; shares workflow reading corpus, test_sd_dispatch and package lint through integration. Its paseo/model/adoption changes require a final combined recount. |
| paseo-human-surfaces-visible-and-reachable — visible terminals/pages | No direct file overlap now that this task deletes its paseo insertion. Its paseo surface edits still affect combined reading counts; integrate with that file owner before recount. |
| adoption-asks-which-extensions — historical extension checks | Current narrowed task owns dispatch_records/number_guards/tests/laws, not these extension files. No shared file; normal adopter selection remains its existing authority. |
| adr-required-statement — decision evidence at completion | No direct extension overlap; existing ADR/report checks may apply at implementation. No ADR number or shared index is requested here. |
| adr-silent-undo-probe — fictional refactor experiment | No peers file overlap: local record remains ideation for its fictional refactor harness/scenario; do not infer closure from an earlier overlap table. |
| comment-check-reaches-delivery-gate — exact-head comment evidence | No overlap: delivery_gate/tests/validation principles. Rerun the reading fixture if its output lands first; do not change its check. |
| journey-canvas-hosted-poc — hosted canvas experiment | No overlap: kc-journey-map hosting artifacts and its own state. |
| journey-server-host-pilot — private server adapters | No peers overlap established: top-level/archive task absent locally; sibling cites validation dispatch records for local server adapters. Current remote ownership remains unverified; return ownership check to FO. |
| ops-inbox-r1-setup-and-isolation — signed ops intake | No product-file overlap. Its relay/qnow notices are a concrete shared **authority case**: go-live-held notices cannot be sent merely to satisfy freshness. |
| pr-review-lite-value-pilot — bounded review experiment | No overlap: kc-pr-flow review capability and trial state; no shared checker or numbering here. |

Recommended order: sibling owns and integrates peer-send/notice policy under its accepted revise, then add this shared peers section once; model-roster/human-surface owners reconcile their own paseo changes and recount combined reads. Require this task's cold-entry replay before delivery; retain natural-use observation after delivery. Other code/check tasks may proceed independently; if delivery-gate output changes, rerun the common fixtures. FO rechecks live task and PR ownership before implementation. All sibling files were read only; active designs can change after this snapshot.

## Acceptance criteria

## Captain amendments

### Amendment 1 — 2026-10-30, chat
Captain: 「可以」 (chat, 2026-10-30)
Asked: 「決定：#756 改成在工作流 README 加這 38 個字並放寬上限，可以嗎？」, which FO had stated as: 「**建議：加這一句，共 38 個字。** #756 其餘文字留在 peers 檔，用來規範發更正通知的那一方。」
Supersedes: AC-1
Design: Proposed product change set: **only `kc-dev-flow-2/extensions/peers/EXTENSION.md`**, inserting the transport-neutral Current peer facts section before Claude Code binding.

Superseded text:

**AC-1 — A cold FO loads the rule and removes a cleared Web merge.** Before delivery, start a fresh isolated FO context that has not read peers (no inherited history, peers content, path hint, current-turn source answer or replay verdict). Provide ordinary adopted workflow entry, a Captain status request, the admitted stale relay line and logged read-only source access; expose the exact combined candidate through normal package paths. Do not put this task's criteria or answer in the FO prompt. Capture initial context, file/tool read trace, package SHA, fixture bytes and resulting Captain-facing status. Require an observed read of peers before reliance on the peer fact, followed by a current-turn source query for `spacedock-dev/subspace-web` PR 186. Run notice present, absent and delayed with MERGED/b71f912; all remove the cleared merge/approval and include source/time. OPEN negative control retains the pending action without merge authority; unavailable source yields unverified and an FO-owned check. Falsifier: preloading/hinting peers to make the run pass, failure to discover it, no query, stale request after MERGED or suppressing the OPEN action. A harness that injects the rule or expected response proves nothing about loading. If the normal entry fails, report the trace to FO; do not add a loader here. Current evidence: planned cold test and incident walkthrough; no fresh FO has been launched in this ideation.

### Amendment 2 — 2026-10-31, chat
Captain: 「756可以。」 (chat, 2026-10-31)
Asked: 「現在只等你回覆 #756：改放 `dev` 入口技能、不放寬上限，可以嗎？」, which FO had stated as: 「**建議：把這句話改放 `dev` 入口技能，撤掉工作流 README 那句和放寬上限。**」
Supersedes: AC-7

Superseded text:

**AC-7** — A cold FO checks a peer-derived Captain action through the workflow entry. Amended by Captain, amendment 1. Before delivery, FO reruns the cold runs on the new head: start a fresh isolated FO context without inherited history, peers preloading/path hints, a current-turn source answer or a replay verdict. Provide ordinary adopted workflow entry carrying the exact candidate workflow sentence, a Captain status request, the admitted stale relay line and logged read-only source access. Do not put this task's criteria or answer in the FO prompt. Capture initial context, file/tool read trace, package SHA, fixture bytes and resulting Captain-facing status. Require a current-turn source query for `spacedock-dev/subspace-web` PR 186 before naming its Captain action; reading peers is no longer a pass condition. Run notice present, absent and delayed with MERGED/b71f912; all remove the cleared merge/approval and include source/time. OPEN negative control retains the pending action without merge authority; unavailable source yields unverified and an FO-owned check, with no Captain action assigned. Falsifier: injecting the rule or expected answer into the prompt, no query, stale request after MERGED, suppressing the OPEN action or assigning the inaccessible action to the Captain. Retain the shared peers section for transition corrections. If the ordinary entry/source test fails, report the trace to FO; do not add a startup preload, hook, watchdog or other loader. Current evidence: earlier FO-run cold cases in `peer-status-reaches-fresh/cold-fo/README.md` are on the prior head or scratch wording; new-head reruns are pending.


## Stage Report: ideation

- DONE: A design for a peer FO's status reaching other FOs fresh, comparing a peer pushing its own state changes (merged, released, unblocked) when they happen, a status line carrying its time, and checking a Captain action named from a peer at its source before relaying it; the two 2026-10-28 events in Scope replayed as prevented; receipt-only acknowledgements and no-action finish notices considered; overlap with peers-paseo-rule-matches-practice's design named
  PRFAQ compares push/time/source-check; both admitted incidents replay to a removed action or explicit uncertainty; receipt/finish suppression and the sibling send-policy dependency are named. Original-session and native delivery proof are not claimed.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (batch10-after-release-obligations, names-check-says-what-it-skipped, peers-paseo-rule-matches-practice, peer-status-reaches-fresh, model-roster-per-repo, paseo-human-surfaces-visible-and-reachable) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Batch overlap lists both proposed extension files and all 14 named batch/live task rows, shared replay/reading checks, authority-held notices and an explicit integration order; other state files were read only.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Embedded recount exit 0: peers 805→1067, paseo 562→629, listed with host 1974→2303. Executed common lifecycle fixtures exit 0: startup 442, idle/open 672, idle/merged 1021, archive 371, merge ask 1003; real source/message output remains unmeasured.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Six individually falsifiable criteria distinguish design, recording-transport, fresh-agent and native-use evidence. One Captain choice recommends current-turn source checks and states extra reads/unverified holds as its cost.
- SKIPPED: AC-1 — Fresh-agent Web merge replay.
  Design walkthrough supplied; execution awaits an approved implementation. A MERGED source followed by a Captain merge request is the named failure.
- SKIPPED: AC-2 — Fresh-agent unblock replay.
  Design walkthrough supplied; originals/native replay not read or run. Authorization becoming a release claim is the named failure.
- SKIPPED: AC-3 — Recorded transport/duplicate/authority behavior.
  Reproducible cases defined; no peer send or implementation performed. An unlisted new notice, duplicate action or forbidden send would fail.
- SKIPPED: AC-4 — One real adopted peer transition.
  Requires later authorized normal adoption and a natural event; fixture success does not satisfy it. Repeating a disproved Captain action would fail.
- DONE: AC-5 — Design-stage reading evidence; final behavior proof deferred.
  Exact draft counts and common fixture outputs measured above; hidden source/notice text would invalidate a full-total claim. Candidate lint and real S/M totals remain not run.
- DONE: AC-6 — Current design is presentable and scoped.
  design_surfaces.py check exit 0: "peer-status-reaches-fresh.md: design surfaces presentable"; original 2655 bytes/frontmatter preserved, only this entity modified, git diff --check clean.
- DONE: Render and inspect the required diagram.
  Mermaid 11.16.1/Playwright 1.62.1 rendered 18 nodes, SVG 36849 bytes, exit 0; inspected origin/receiver, permitted notice, current-turn query and unavailable-source stop against prose. Initial sandbox launch failed; authorized temporary-browser retry succeeded.

### Summary

Designed mandatory current-turn source checks for peer-derived Captain actions, timestamped facts and bounded change notices inside the two existing extension files. Design and reading fixtures pass within their stated limits; implementation, original-event verification, actual peer delivery and real-use acceptance are not claimed. FO must present the single freshness-standard recommendation, coordinate the sibling send-policy gate and integrate shared extension edits before implementation; no gate was resolved here.

## Stage Report: ideation (cycle 2)

- DONE: Revise the design under the Captain's ideation-gate revise of 2026-10-30 (「准」); the asks are in this task's newest ideation gate question (review/ideation, newest briefing); do exactly those asks, update criteria and the stop condition to match, and name anything that would go beyond them as a return to FO rather than designing it; peers-paseo-rule-matches-practice now owns the shared text, so read its newest design and stay consistent with it
  Newest briefing and 2026-10-30 revise govern: deleted owned paseo insertion, cold-entry AC-1, post-delivery AC-4; stop/criteria match; sibling cycle 2 at da23dd127 owns transport wording. Out-of-scope loading/host remedies return to FO.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (batch10-after-release-obligations, names-check-says-what-it-skipped, peers-paseo-rule-matches-practice, peer-status-reaches-fresh, model-roster-per-repo, paseo-human-surfaces-visible-and-reachable) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Batch overlap names the sole changed product path, all 14 required task rows and shared reading/replay checks; sibling owns Paseo, while model/surface tasks have no direct file overlap with this narrowed change.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Recount exit 0: own peers 805→1067 (+262), own paseo unchanged; integrated listed route 1974→2297. Common mocked lifecycle fixtures reran exit 0: 442/672/1021/371/1003; actual replay/native response words remain pending.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Six individually falsifiable criteria name evidence and stage timing; no unresolved material choice within the revise grant. Added reads, cold-loading failure risk and delayed real-use evidence are explicit costs.
- SKIPPED: AC-1 — Cold-FO loading and cleared Web merge replay.
  Not run at ideation; before delivery require unhinted entry/read trace and MERGED/OPEN/unavailable controls. Preloading peers or repeating the cleared action fails acceptance.
- SKIPPED: AC-2 — Cleared unblock replay.
  Inputs and falsifiers specified; original-session/native behavior unverified. Treating authorization as release completion fails.
- SKIPPED: AC-3 — Integrated correction/authority behavior.
  Candidate recorder and sibling-owned native checks are later work; no sends performed. Unlisted-only refusal under the delivered sibling policy, forbidden send or hidden material error fails.
- SKIPPED: AC-4 — Natural adopted transition after delivery.
  Captain explicitly moved this observation after delivery; FO retains it without a pre-delivery hold. No natural event is not run, never proof of value.
- DONE: AC-5 — Design-stage reading evidence.
  Embedded independent reconstruction and pinned common fixture program executed; double-counted pointer or omitted due text changes the counts. Final candidate lint/behavior and response-word evidence remain pending.
- DONE: AC-6 — Presentability and scoped revision.
  design_surfaces.py check exit 0: peer-status-reaches-fresh.md: design surfaces presentable; frontmatter and whole prior report preserved byte-for-byte; git diff --check clean; only this entity is modified by this worker.
- DONE: Render and inspect the revised diagram.
  Mermaid 11.16.1 / Playwright 1.62.1 / Chrome rendered 18 nodes, SVG 37,210 bytes; inspected cold-loading failure, notice/hold, status-only and action-source exits. Sandbox browser launch failed; permitted temporary-browser retry passed.
- DONE: Use the dispatched local fallback after GitHub API failure.
  gh pr list failed: error connecting to api.github.com; git fetch/source and local state checked, remote ownership remains for FO to reconcile before implementation.

### Summary

Revised only the active state design under the Captain's three asks: shared peers text only, cold-FO loading proof before delivery, and natural-use observation after delivery. Current-stage design/diagram/recount checks pass; fresh-agent behavior, native delivery and real-use value are not claimed. FO can dispatch within the recorded revise grant, after reconciling shared-file/PR ownership; any loading or transport remedy beyond the asks returns to FO.

## Stage Report: implementation

- DONE: Implement the approved design and acceptance criteria in the task file; the revised design approved under the Captain's 2026-10-30 grant (「准」, recorded at the ideation gate): shared peers text only, no paseo insertion, consistent with the wording PR #754 owns; only the files the design names
  Candidate 8f42107b1cc9ae0b3a7d10ad2a2408b46fcbe0cd on spacedock-ensign/peer-status-reaches-fresh, base 4c182bc66a1384d8a677b6a83a2b8dbd2088a7df; adds the exact approved 262-word Current peer facts section to kc-dev-flow-2/extensions/peers/EXTENSION.md; no other product path changed.
- DONE: Commit locally, no push; PR text written for FO; stacked on PR #754, so write the PR text with base branch spacedock-ensign/peers-paseo-rule-matches-practice
  Scoped Conventional Commit made locally; /tmp/impl-peer-status-reaches-fresh-pr.md contains title/body and the stacked base. No product push or PR creation; fetched source and live open-PR inventory confirmed #754 owns the base and no open PR uses this task branch.
- SKIPPED: One Draft PR in iamcxa/kc-claude-plugins; FO pushes, opens the Draft PR, runs RoboRev and reads CI
  Explicit Paseo/Codex dispatch assigns publication, exact-head review and CI to FO; prepared text is concrete for that handoff. No PR opened: no worker push grant.
- SKIPPED: Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
  Full acceptance is not green. Four exact-byte/scope controls refuse base-without-change, duplicate insertion, missing current-turn wording and missing worker boundary; these are structural checks, not behavioral falsifier proof. AC-1/AC-2/AC-3 behavior and their mutations remain not run.
- SKIPPED: AC-1 — A cold FO loads the rule and removes a cleared Web merge
  Dispatched to FO: unhinted cold entry/read trace plus notice present/absent/delayed, MERGED/OPEN/unavailable controls. No fresh FO launched, source queried or cold-entry/source/status words measured by this worker; failure must return to FO without a loader repair.
- SKIPPED: AC-2 — A cleared unblock does not become a release claim
  Accessible/unavailable/unrelated original-source behavioral replays and mutations not run; no historical authorization authenticated or credential read. The candidate preserves original-authority rules; this textual preservation does not prove compliant behavior.
- SKIPPED: AC-3 — Transition corrections preserve the integrated binding
  Recording-transport merged/released/unblocked, recipient/authority/duplicate/conflict/uncertain/error cases and behavioral mutations not run. FO retains independent replay and the sibling's native transport/error-visibility duties; no peer experiment, send retry or host change performed.
- SKIPPED: AC-4 — After delivery, observe one natural adopted peer transition
  FO owns this post-delivery obligation in this task: first natural authorized pair transition, source/notice-or-held reason, receiver query, Captain-facing result and actual word counts. No event/adoption here; not real-use success and not a pre-delivery hold.
- DONE: AC-5 — Reading cost and ordinary orchestration remain visible: independent recount and pinned common fixtures
  Embedded programs extracted from this task and sibling state da23dd127b929a0d580fa181ce1c3d8879fc71d6 ran python3 -B, exit 0. Actual stacked-base→candidate peers 1039→1301; paseo 389 unchanged; primary host addend 607; unlisted 1646→1908 and listed 2035→2297. Original route totals 1412/1974; pointer counted once.
- DONE: Record the five lifecycle rows
  Startup/idle-open/idle-merged/archive/merge-ask common fixture rows remain 442/672/1021/371/1003; listed original→base→candidate rows 2416→2477→2739, 2646→2707→2969, 2995→3056→3318, 2345→2406→2668, 2977→3038→3300. Missing observer refusal changes/fails the fixture; these are mocked control-text counts, not callback/runtime savings.
- SKIPPED: AC-5 actual cold-entry/source/error/status/notice word addends
  Behavioral replays were not run, so these addends are unmeasured, not zero; FO must append them with AC-1/AC-2/AC-3, and later AC-4. Existing capability audit was completed in the accepted design; no new mechanism or missing-capability claim is introduced.
- DONE: kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), applicable test_lint_skills.py/test_sd_dispatch.py with the dispatched Spacedock root
  All exit 0: workflow 5781/5781 words; 45 lint tests and fresh/reused dispatch/Team/authority/report/refusal fixtures. Final test rerun uses python3 -B and fresh empty PYTHONPYCACHEPREFIX directories; Spacedock CLI 0.27.2, plugin root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3. Logs: /private/tmp/peer-status-reaches-fresh-evidence/{lint-tests,dispatch-tests}.log.
- DONE: adr_lint.py docs/adr --since <base> exit 0; number_guards.py check exit 0
  Dispatched 0.33.1 scripts at exact base/candidate: 45 ADR records, no legacy; number guard PASS/no findings with --base 4c182bc66a1384d8a677b6a83a2b8dbd2088a7df. Initial default-trunk check wrongly included sibling ADR 0046 and failed R4; explicit stacked base correctly excludes it. No ADR added/reserved by this task; existing 0020/0037/0038/0042/0046 read at candidate, with 0046 narrowing 0038.
- DONE: comment_ratio.py within its maximum; affected-document disposition; scope and AC-6 preservation checks
  comment_ratio.py base HEAD exit 0: code 0, comments 0, 0.0%, maximum 5% not enforced below 20 code lines. doc_impact.py exit 0, 0 documents listed; peers is updated. design_surfaces.py exit 0/presentable (implementation scope check not run); diagram and AC-6 ideation receipts remain unchanged. Existing transport/authority/worker bytes, workflow budget and sibling/adopter files preserved; git diff --check clean.
- SKIPPED: RoboRev complete review evidence
  Required post-commit roborev_gate.py --repo <assigned worktree> --base 4c182bc66a1384d8a677b6a83a2b8dbd2088a7df exited 3: incomplete: the roborev daemon is not running. Preflight absence was sent to FO; no clean review or repair is claimed.
- DONE: CI cost measured or stated as not measured; split-root state boundary
  CI cost per PR not measured; no CI trigger changed. State root/branch verified spacedock-state/dev2; append after status --read total_lines 339, preserve all previous bytes/frontmatter, commit and sync this entity path only. Task remains implementation; no acceptance, transition or gate resolution claimed.

### Summary

The exact approved single-file insertion is committed locally at 8f42107b1cc9ae0b3a7d10ad2a2408b46fcbe0cd, stacked on #754, with PR text prepared for FO. Structural, dispatch and reading checks pass within their stated boundaries; cold loading, independent behavior/mutations, native transport, actual replay word addends, exact-head RoboRev and CI remain for FO before accepted delivery, while natural-use observation remains after delivery. This is an implementation handoff, not a claim that every acceptance criterion is green.

## Stage Report: implementation

- DONE: Apply Captain amendment 1 and commit one follow-up on the existing PR #756 branch; keep the peers section and use only the authorized files.
  Candidate 362418e024e61f842ba44ece845adf3063b31517 on spacedock-ensign/peer-status-reaches-fresh; stacked base c804241d24a2b378604409c17340db29c096ac51, prior head 153e3b0d90904e55cac9000bf7d94ce4fd5ffc31. This commit changes only workflow.md and lint-skills.py; full base diff also retains the prior peers insertion.
- DONE: Add the unchanged 38-word sentence at the top of Extensions and record the +38 budget raise with the Captain's amendment words.
  Exact text compared with cold-fo/README.md; workflow 5781 → 5819, Extensions 224 → 262; the step quotes 「可以」 and its exact Asked question, and names startup/resume and Extensions reads. It replaces no existing sentence and answers the admitted stale-action incidents; no script enforces FO behavior. No version bump, new script or ADR added.
- DONE: Move superseded AC-1 into amendment 1 verbatim and write its replacement under a fresh id.
  AC-7 says “Amended by Captain, amendment 1”; it preserves cold unhinted ordinary entry, current-turn source and MERGED/OPEN/unavailable controls, and removes peers loading as a pass condition. Frontmatter, other criteria, diagram, prior reports and sibling files remain unchanged; design_surfaces.py check exits 0.
- DONE: Commit locally, no push; PR text written for FO.
  /tmp/impl-peer-status-reaches-fresh-pr.md contains the scoped Conventional Commit title and complete replacement body for existing Draft #756, retaining the stacked base and new full SHA; live PR before work was OPEN/Draft at 153e3b0d9. No product push, PR edit, review request, ready or merge performed.
- SKIPPED: One Draft PR implementing every acceptance criterion, with the PR text updated and FO cold runs on the new head.
  Existing #756 is reused; publication/body update, exact-head cold reruns, fresh RoboRev and CI are delegated to FO, not run or clean on this new head. The prepared text supersedes the old single-file scope and earlier-head evidence.
- SKIPPED: Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared).
  Full acceptance is not green: behavioral replays/mutations are not run. Four structural mutation controls with python3 -B and a fresh empty cache prefix refuse missing sentence, missing raise, missing Captain quote and missing loaded moment; they establish budget/scope checks only, not source-query behavior.
- SKIPPED: AC-7 cold-entry/current-source behavior, and AC-2 cleared-unblock/source controls.
  FO owns the new-head cold rerun; prior cold-fo results are earlier-head/scratch evidence. Accessible/unavailable/unrelated-original unblock transcripts, behavioral falsifiers and actual source/error/status word addends remain not run; no historical authority or release claim is authenticated here.
- SKIPPED: AC-3 recording-transport behavior and sibling native ask/reply/notice/failure visibility.
  Recipient, authority, uncertainty/resume, duplicate/conflict and error/hold controls and behavioral mutations remain not run. No peer experiment, secret access, auto-retry or host repair performed; recorder checks would not replace the sibling's native proof.
- SKIPPED: AC-4 after-delivery natural adopted transition.
  FO retains the existing post-delivery obligation: first natural authorized pair transition, source/notice-or-held reason, receiver query, Captain-facing status and actual words. No event/adoption here; not real-use success or a pre-delivery hold.
- DONE: AC-5 independent recount, five lifecycle rows and unchanged ordinary orchestration within the fixture boundary.
  Pinned embedded recount/common program ran exit 0; actual base → candidate peers 1058 → 1320, paseo 389 unchanged, host 607, unlisted 1665 → 1927 and listed 2054 → 2316. Shared insertion stays 262 words and the transferred pointer is counted once; native/output addends remain unmeasured.
- DONE: Correct the measurement limit exposed by the workflow addition, without changing the product fixture.
  Historical sec() matches the inline “## Extensions” reference (451 words), so its 442/672/1021/371/1003 rows miss +38. Independent anchored-heading recount gives 442/672/1021/371/776 → 442/672/1021/371/814; full README reads separately add 38. Scripts/logs: /private/tmp/peer-status-amendment-evidence/{common-anchored-base,common-anchored-candidate}.{py,json}; these are bounded mocked corpora, not session totals or savings.
- DONE: kc-dev-flow-2/scripts/lint-skills.py, applicable test_lint_skills.py/test_sd_dispatch.py with dispatched Spacedock root.
  All exit 0: 5819/5819 words, 45 lint tests, 10 fresh/reused route/stage/host handoffs plus Team/authority/report/gate refusal controls. python3 -B with fresh empty cache prefixes; /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3, CLI 0.27.2. Extensions is outside worker context sections; stage definition bytes are unaffected by this commit. Fresh logs: /private/tmp/peer-status-amendment-evidence/{lint-tests-fresh,dispatch-tests-fresh}.log.
- DONE: adr_lint.py docs/adr --since <base> exit 0; number_guards.py check exit 0; comment_ratio.py within maximum.
  Dispatched /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1 scripts at base c804241d24a2b378604409c17340db29c096ac51/candidate: 45 ADRs, 0 legacy; number guard PASS/no findings (no migrations-path); code 3, comments 0, 0.0%, maximum 5% not enforced below 20 code lines. git diff --check clean.
- DONE: Affected-document disposition and AC-6 preservation within implementation scope.
  doc_impact.py lists five: docs/adr/0020 and 0037 unaffected (rulings remain unchanged); kc-dev-flow-2/README.md unaffected (extension table and lint command remain accurate); skills/maintain-flow/SKILL.md unaffected (existing budget/replay procedure retained); learning.md unaffected (measurement practice followed). workflow and peers updated; AC-6 ideation render receipts retained, not rerun; body-only amendment/report preserves the diagram.
- SKIPPED: RoboRev evidence= line; FO exact-head review and CI.
  Required post-commit roborev_gate.py --repo <assigned worktree> --base c804241d24a2b378604409c17340db29c096ac51 exited 3: incomplete: the roborev daemon is not running. FO notified at preflight; no clean evidence or review finding asserted, and earlier-head clean evidence is not reused.
- DONE: CI cost stated as not measured; split-root report ownership and bounded handoff.
  CI cost per PR not measured; no CI trigger changed. Shared state checkout verified on spacedock-state/dev2; amend/report only peer-status-reaches-fresh.md, preserve all other bytes, path-scoped commit and sync. Task stays implementation; no acceptance, transition or gate resolution claimed.

### Summary

This report supersedes the earlier implementation report: the shared peers section remains, and the new local candidate 362418e024e61f842ba44ece845adf3063b31517 adds the Captain-approved workflow entry sentence with its +38 budget record and applies the AC-1 → AC-7 amendment. Static/dispatch/budget checks pass; the corrected measurement exposes the common fixture's earlier heading-match error. FO retains publication/PR update, new-head cold and other behavioral acceptance, exact-head RoboRev/CI, and later natural-use observation; full acceptance is not claimed.

## Stage Report: implementation

- DONE: Apply Captain amendment 2 on the existing branch of PR #756, using only the named files.
  Candidate 6f1f83522c673ecb19f1acb461137fbd4576b609 on spacedock-ensign/peer-status-reaches-fresh, stacked base c804241d24a2b378604409c17340db29c096ac51, prior local head 362418e024e61f842ba44ece845adf3063b31517; one follow-up commit, product tree clean. Net base diff is peers/EXTENSION.md and skills/dev/SKILL.md only.
- DONE: Remove the workflow sentence and budget raise with a git revert of unpushed 362418e02, then add the unchanged 38-word sentence to dev before “For existing work, preserve”; no workflow word budget change.
  git revert --no-commit 362418e024e61f842ba44ece845adf3063b31517 followed by the scoped commit; exact sentence compared with cold-fo/README.md. Workflow and lint-skills.py equal stacked-base bytes; workflow 5781/5781, dev 763→801; peers unchanged from prior candidate. No version bump, new product script or ADR.
- DONE: Move superseded AC-7 into amendment 2 and write its replacement under a fresh id, keeping retained duties and the no-dev-entry limit.
  AC-7 moved verbatim; AC-8 says “Amended by Captain, amendment 2”, changes only loading location and adds the limit. Cold/no-hint entry, source calls/trace, MERGED notice present/absent/delayed, OPEN/unavailable controls, correction text and failure returns retained; other criteria, frontmatter, diagram and all prior reports preserved.
- DONE: Commit locally, no push; PR text written for FO.
  /tmp/impl-peer-status-reaches-fresh-pr.md holds scoped Conventional Commit title/full replacement body for #756, branch/base/full SHA. Fetch succeeded; origin task head 153e3b0d90904e55cac9000bf7d94ce4fd5ffc31; live GitHub API read failed connecting to api.github.com. No product push, PR edit, review request, ready or merge performed.
- SKIPPED: One Draft PR with PR text updated; FO pushes, updates existing #756, runs exact-head review and reads CI.
  Dispatch delegates these steps to FO; prepared text is ready. Live PR/hosted CI not verified here; earlier-head evidence is not current proof.
- SKIPPED: Every acceptance criterion green with its named evidence; each behavioral falsifier shown failing by mutation with python3 -B and caches cleared.
  Full acceptance is not green. Eight temporary structural controls reject missing/misplaced sentence, retained workflow/budget changes, removed peers text, altered superseded text, removed OPEN duty and missing limit. These prove structure only; fresh empty cache prefixes and python3 -B used. Behavioral falsifiers not run.
- SKIPPED: AC-8 new-head cold-entry/current-source behavior, and AC-2 cleared-unblock/source controls.
  FO owns new-head cold and source-down/MERGED/OPEN/notice reruns; scratch runs are earlier-head evidence. No fresh FO launched; original-authorization/irrelevant/unavailable replays not run, actual read/output words unmeasured. No credential read or released claim; an FO resuming without dev does not get the sentence.
- SKIPPED: AC-3 recording-transport behavior and sibling native ask/reply/notice/failure visibility.
  Recipient/authority/busy/unknown/uncertain-resume/duplicate/conflict/error/permission-hold replays and mutations not run; sibling owns native proof. No peer experiment, permission response, retry or host repair performed.
- SKIPPED: AC-4 after-delivery natural adopted transition.
  FO retains first natural authorized pair transition, source/notice-or-held reason, receiver query, Captain status and actual word counts. No event/adoption here; not real-use success or a pre-delivery hold.
- DONE: AC-5 independent recount and pinned common fixture; record reading costs and five lifecycle rows.
  Embedded instruments ran exit 0. Actual stacked-base→candidate peers 1058→1320, paseo 389 unchanged, host 607, unlisted 1665→1927, listed 2054→2316; shared insertion 262, pointer once. Dev adds 38 per actual entry read separately; historical assembled design routes remain 1412/1974→1908/2297.
- DONE: Preserve ordinary orchestration and expose the historical common fixture's heading-match limit.
  Pinned startup/idle-open/idle-merged/archive/merge-ask rows: 442/672/1021/371/1003. Independent anchored-heading base/candidate runs both: 442/672/1021/371/776; inline Extensions reference caused overcount. Listed exchange corrected base→candidate: 2496→2758, 2726→2988, 3075→3337, 2425→2687, 2830→3092, before actual dev/output addends. Mocked corpora, not runtime/callback savings.
- SKIPPED: AC-5 actual cold-entry/source/error/status/notice output addends and real-use costs.
  Behavioral runs delegated; actual costs remain unmeasured, not zero. FO records with AC-8/AC-2/AC-3 and later AC-4. Accepted capability audit retained; no new mechanism or missing-capability claim.
- DONE: Repository CI copy of lint-skills.py, applicable test_lint_skills.py/test_sd_dispatch.py with dispatched Spacedock root.
  All exit 0: workflow 5781/5781, 45 lint tests, fresh/reused pilot/POC/host handoffs and Team/authority/report/gate/refusal controls. Python3 -B/fresh empty cache prefixes; Spacedock plugin 0.27.3, CLI 0.27.2. Logs /private/tmp/peer-status-dev-entry-evidence/{lint,lint-tests,dispatch-tests}.log; dropping a declared binding/report correction refuses its fixture. Not native worker/skill execution proof.
- DONE: adr_lint.py docs/adr --since <base> exit 0; number_guards.py check exit 0; comment_ratio.py within maximum.
  Dispatched 0.33.1 scripts: 45 ADRs/0 legacy; number PASS/no findings (no migrations-path, R4 no task reservation); code/comment lines 0/0, 0.0%, maximum 5% not enforced below 20 code lines. Existing 0005/0016/0020/0037/0038/0042/0046 read at pinned prior HEAD; no ADR added/changed/reserved. git diff --check clean.
- DONE: Affected-document disposition and AC-6 preservation within implementation scope.
  doc_impact.py exit 0, 0 listed documents; dev/peers updated, workflow budget restored. design_surfaces.py check exit 0/presentable; scope check not run for implementation. AC-6 ideation render receipts retained; unchanged diagram not rerendered. Final scripts/logs under /private/tmp/peer-status-dev-entry-evidence.
- SKIPPED: RoboRev evidence= line and FO exact-head review/CI.
  Required post-commit roborev_gate.py --repo <assigned worktree> --base c804241d24a2b378604409c17340db29c096ac51 exited 3: incomplete: the roborev daemon is not running. FO notified; missing evidence, not clean review; no review finding or repair asserted.
- DONE: CI cost measured or stated as not measured; split-root state boundary and bounded handoff.
  CI cost per PR not measured; no CI trigger changed. State root/branch verified spacedock-state/dev2; body-only amendment/report after status --read total_lines 437, path-scoped commit and state sync before signal, preserving sibling changes. Task stays implementation; no acceptance, transition or gate resolution claimed.

### Summary

This report supersedes all earlier implementation reports. Candidate 6f1f83522c673ecb19f1acb461137fbd4576b609 retains peers, moves the exact 38-word sentence to dev under amendment 2, and restores workflow/budget bytes to the stacked base; AC-8 retains AC-7's proof duties and the no-dev-entry limit. Structural/dispatch/reading checks pass within their boundaries; FO retains publication/PR update, new-head cold and other behavioral acceptance/mutations, exact-head RoboRev/CI and later natural-use observation.
