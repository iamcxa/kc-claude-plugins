# Feedback round 004

- Identity: round 004, status `open`, opened 2026-10-28, interviewer the kc-plugin dev2 FO (Paseo 2e87a82e), workflow docs/dev2 of iamcxa/kc-claude-plugins.
- Trigger: early targeted round under recorded Captain authority: his 「准」 (chat, 2026-10-28) to the fo-interviews-extension validation gate question, which named "the Captain asks for an early targeted interview round 4 under the candidate extension text (one or two extensions, the five FOs, about ten bundled sends, no test agents) as the evidence validation found missing". Cadence anchor: unset before and after (an early targeted round resets nothing without a recorded ruling; the extension is not adopted yet). Batch membership/completion: not used for this trigger.
- Policy under test: candidate `kc-dev-flow-2/extensions/fo-feedback/EXTENSION.md` at PR #745 head bd328daf6 (questions version 1). Package in use: kc-dev-flow-2 0.32.1.
- Topics: `peers` (required in every adopter) and `paseo` (optional; asked of each FO with "not enabled" an accepted answer). No core workflow topic this round.
- Frozen roster (source: rounds 1-3 records and Paseo `paseo ls -a`, 2026-10-28; transport: Paseo agent message to an idle peer, per the paseo extension):

| FO | Area | Paseo id | Status at freeze |
| --- | --- | --- | --- |
| kc-paseo-plugins dev2 FO | project-env | 8b2c2fc2 | idle |
| kc-ops-inbox FO | ops-inbox | 46c2ebdf | idle |
| subspace-web/v0 dev2 FO | web, v0 | 295b873d | running (deferred until idle) |
| relay FO | subspace-relay | 1671c3a9 | idle |
| qnow dev2 FO | qnow | 519ab4c8 | idle |

## Coverage

| FO | peers | paseo |
| --- | --- | --- |
| kc-paseo-plugins | answered | answered (not enabled) |
| ops-inbox | answered | answered (not enabled) |
| web/v0 | deferred (running) | deferred (running) |
| relay | answered | answered (not enabled) |
| qnow | answered | answered (not enabled) |

## Exchanges

Intent recorded before sending. Key: round 004 + FO + topic. One bundled message per topic, the four version-1 questions verbatim from the candidate EXTENSION.md, at most 300 answer words per topic with source links.

### kc-paseo-plugins (project-env) dev2 FO, 8b2c2fc2 — answered 2026-10-28 (Paseo agent message, sender stamped)

Labelled condensation of the operator's words.

peers (enabled):
1. 2026-10-28, no task: shared Paseo 0.13.2 plugin research with the Bridge FO (a88dedae) at the Captain's request; waited until it was idle, sent as information only (research/2026-10-28-paseo-0.13.2-plugins.md, state 478ffbf). 2026-10-28, project-env-pick-repository: sent the docs-staleness need; the reply relayed the Captain's 「讓他 dogfood 一兩輪」; treated as data, asked him directly, he answered 「試」 (local-ext/doc-site.md, state 87f0e98).
2. Skipped "record a work-changing exchange in the task" for both: the share belongs to no task; the docs exchange lives only in local-ext/doc-site.md. The rule names no place for an exchange without a task.
3. Treating a relayed quote as data stopped action: asked directly, the Captain first asked what a local extension was, then said 「試」. Keep.
4. Waiting for idle cost unmeasured time: the Bridge FO stayed running while waiting on the Captain; the only wait found was a 60 s polling loop (this session, 2026-10-28).

paseo (not enabled in its README):
1. Used Paseo tools as transport anyway (get_agent_status, send_agent_prompt, `paseo ls`) for the 0.13.2 share, the docs need, round 3 and round 004 replies, 2026-10-28.
2. Did not record `peers not run: Paseo binding not enabled`; used Paseo because the Captain asked to share and Paseo is the only route.
3. The idle check held the share so it did not interrupt a turn waiting on the Captain. Keep.
4. Replies go out with steer while the recipient is running (round 3, status "running"); if a reply should not steer, the rule should say so.

### kc-ops-inbox FO, 46c2ebdf — answered 2026-10-28 (two Paseo agent messages, sender stamped)

Labelled condensation of the operator's words.

peers (enabled):
1. ops-metric-event-protocol (archived 2026-10-27): qnow FO (519ab4c8) was the first-adopter reviewer, relayed through this FO only; review saved verbatim at _archive/ops-metric-event-protocol/qnow-review-2026-10-26.md; added decision D7 and showed qnow cannot send crossings without a per-period counter. ops-inbox-r1-setup-and-isolation, 2026-10-23: the vault question first went to relay FO before the Captain named 8b2c2fc2. 2026-10-26/27: interview and repro answers.
2. Skipped: Captain quotes relayed by qnow FO recorded as "via qnow FO" (protocol `### Sources` C2 to C6) because his originals live in qnow's session; no `Peer:` lines (exchanges sit in task sections); 2026-10-23 one message bundled several questions.
3. qnow's 2026-10-26 review caught the period-boundary mismatch (qnow's boundary 14:00:20Z on the 17th) before it was pinned into the contract id. Keep "FO relays; workers never message peers".
4. 2026-10-23 a question steered into relay FO's running turn was answered only after that turn; inferring an FO from its name sent a vault question to the wrong session (evidence in r1's `## FO alignment` and round 1). Owed peer notices are untracked: the contract v1 landing notice (d7eeeef2) to relay and qnow is held behind the Captain's go-live decision.

paseo (not enabled; enabling proposed to the Captain 2026-10-27, open):
1. No task ran under it; r1 (2026-10-23) needed it (steer into a running turn); r1 go-live will need relay to build the emitter.
2. Since 2026-10-26 checks `get_agent_status` before each send; sets `activeTurnBehavior` only on asked-for replies; has not used the 5-minute deferral.
3. None recorded.
4. `send_agent_prompt` defaults to `steer` for agent callers (tool schema, read 2026-10-27), so a forgotten flag steers into a running peer; "check status first" works only if remembered; a hook or wrapper refusing a routine send to a running peer would enforce it. Cost not measured.

### subspace-relay dev2 FO, 1671c3a9 — answered 2026-10-28 (two Paseo agent messages, sender stamped)

Labelled condensation of the operator's words.

peers (enabled):
1. 2026-10-28 room-menu-paired-computers with the web FO: action-kind name, shell-capability gate, signed-out-reader question (Web validation F1), merge of subspace-web#186 (state commits bd463939, 019c905e, 3276a960, d994810c). share-names-its-requester and pairing-scope-beyond-one-computer were born from the web FO relaying a Captain ruling (ad9df293, 92f8a5e3).
2. Worked around: the web FO relayed 「A＋C 開 Web 單排 0.2.37、B 給 relay 好」 and asked for confirmation "on your own line"; no rule says whether a relayed ruling counts as Captain alignment; quoted it as relayed, left alignment `pending`.
3. The web FO's order-risk fact (a relay sending a kind the shell refuses hits `failLoad` and breaks every signed-in Room) was verified in public/room-bootstrap.js and recorded as a capability gate before ideation; its path correction (public/room-identity.js) fixed the task body. Keep: peers send verified facts with the commit SHA read.
4. Status drift between FOs: told the Captain Web's half "waits on your merge" after it had merged (b71f912; web FO message 81dc0663 corrected it); web's status said "v0 0.16.2 等 CL 換 token" after CL had authorized the Captain. Proposal: a peer pushes its own state changes (merged, released, unblocked) when they happen; receipt-only acknowledgements cost more than they return.

paseo (not enabled; Paseo tools used for workers and peers anyway):
1. 2026-10-28 pair-pages-center-vertically: ideation worker de2208a9 (astra), implementation worker 34854d81 (sol), both create_agent; a PAT research worker 8f25fe85.
2. Impossible as dispatched: create_agent put every worker's cwd in the FO workspace (dhaka) while worktree and state checkout live under beirut-dev2, outside the sandbox's writable roots; the ideation worker staged under /tmp for FO to install; the implementation worker needed about 20 per-command approvals; the first create_agent failed with "cannot inherit mode 'auto' ... Pass an explicit mode".
3. Approving each command made FO read the scripts (writes inside the worktree, overwrite guards, no stash/reset): assurance, no defect caught. A terminal created under /tmp was invisible to the Captain (filed earlier).
4. Create the worker with cwd or writable root at the stamped worktree plus the state checkout; document the explicit mode as a dispatch parameter. Evidence: about 20 requests for one 4-line CSS change, 2026-10-28.

### qnow dev2 FO, 519ab4c8 — answered 2026-10-28 (Paseo agent message, sender stamped)

Labelled condensation of the operator's words.

peers (enabled):
1. 2026-10-27 r14-round-1 (spacedock-state/dev2-poc): at the Captain's request asked relay FO about Subspace mockup review; relay answered with an interim path (REVIEW.md via subspace:r), recorded in r14-round-1.md. 2026-10-28: answered the Bridge FO (a88dedae) on design-before-code, then sent an addendum.
2. Skipped: the relay ask and the Bridge addendum were new Paseo messages while paseo is unlisted (the rule allows answering incoming asks only); the Bridge exchange is recorded in no task and not in .notes/peer-exchanges.md.
3. The relay answer avoided building an own review path. Searching the backlog before opening: on 2026-10-28 searched zh and en before creating taiwan-holidays-preload; on 2026-10-27 skipped the search and created duplicate uat-per-candidate-deploys, deleted with the Captain's approval and merged into pr-deploy-previews. Keep search-first and peer words as data.
4. Add a carve-out for a Captain-named outbound ask when paseo is unlisted, or say "list paseo": the Captain's 2026-10-27 instruction had no compliant path.

paseo (not listed; Paseo is the worker transport and peer channel):
- Worked: one long-lived designer agent (3bf9522b) reused across mockup passes 1 to 5f, 2026-10-27/28, kept its context.
- Cost: each worker shell command needs an FO approval, about 3 to 5 per pass; FO scanned each script; one install script would have overwritten the 117-check evidence file (pass 5d), caught in review. Total cost not measured.

(answers pending: web/v0)

## Evidence comparison

(pending)

## Findings and close

(pending)
