# peers interview, round 1 (2026-10-26)

Run by hand by the kc-plugin dev2 FO (Paseo 2e87a82e) after batch 6, at the Captain's 「由你直接問」 (chat, 2026-10-26). Answers are operator data, not rulings. Package at the time: kc-dev-flow-2 0.31.0, `extensions/peers/EXTENSION.md`.

## Questions (fixed set)

Sent as one message to each FO, only when it was idle:

1. Each time you sent or received a peer message about a task: date, task slug, counterpart, what it was for, what came of it.
2. Each time you needed another FO's knowledge or work but did not ask: date, task, why not.
3. Which peers rules you skipped or worked around, with the event and why.
4. One event where peers saved time or prevented a mistake.
5. One event where peers could not do what you needed.

Asked to answer from records, "none recorded" where empty, under 300 words, no state change.

## Answers (condensed, in each FO's terms)

## kc-paseo-plugins dev2 FO (Paseo 8b2c2fc2), 2026-10-26

1. Sent/received: 2026-10-23 remove-conductor-import, Comms Officer relay of the Captain's 「准」 (ideation gate, d-1mybcg), checked on the [User] line, recorded person:captain with source. 2026-10-24 same task, relay of 「准」 on merge (d-dd665o), same handling. 2026-10-25 from dev2 FO: 0.30.0 sync on #51, checked by git log and README marker. 2026-10-25 from dev2 FO: Codex-shows-running warning; checked #47 and #50, no hidden finding. Earlier, session only, date unrecorded: answered the qnow FO's L1 question; sent the dev2 FO the release-walk addendum.
2. Unasked needs: none recorded.
3. Rules skipped: never sent the one-time read-only probe and never wrote a `Peer:` line (addressed peers by ids already held). Messages did not open with "if this is not you, say so", and did not state read-only or name a commit.
4. Saved time: the dev2 FO's 0.30.0 notice (2026-10-25) told it the Package root changed, so next dispatches used 0.30.0.
5. Could not help: none recorded.

## kc-ops-inbox FO (Paseo 46c2ebdf), 2026-10-26

1. Exchanges: 10-20 relay FO → it: kickoff brief; later a read-only status ask (replied). 10-22 relay FO: event-input question (replied: not yet defined). 10-23 it → relay FO: r1 asks and contract v1 paths. 10-23 it → relay FO and kc-paseo-plugins FO: where to keep App keys; both answered (relay keeps nothing in 1Password; project-env ADR 0001 one vault per repo); the Captain then ruled relay's vault. 10-25 qnow FO → it, three times (Clerk SMS alert, protocol ownership, storage ranking); replied each; filed ops-metric-event-protocol.
2. Unasked need: 10-25 Paseo Hub POC; did not ask the spacedock-bridge owner (kc-paseo-plugins FO); a research worker read its repo instead.
3. Skipped: several questions per message; never opened with "if this is not you, say so"; misread "this FO" and sent the vault question to relay FO before the Captain named 8b2c2fc2; recorded qnow FO's relayed Captain quotes on ops-metric-event-protocol as "relayed" without checking his words at their source; the vault answers are recorded in r1's file only as the Captain's ruling, not as a peer exchange.
4. Saved time: the two vault answers settled key placement in one round, with evidence (relay grep, ADR 0001), before the Captain rotated keys.
5. Could not: 10-23 its question was steered into relay FO's running turn; that turn ended answering its own work and the answer came only in a later message. A relayed Captain quote cannot be verified from inside a peer message.

## subspace-web/v0 dev2 FO (Paseo 295b873d), 2026-10-26

1. About 150 messages, 2026-10-19 to 10-26; about 80 with relay FO 1671c3a9; others with the dev2 FO, doc FO 4f3ca85f, installer FO 72ebb1f2, a88dedae, bccc97d3, f8e8086f. Kinds: filing asks into a peer's workflow (10-23 publishedAt, dropdown label, CL's Try page; relay FO filed each and replied with the slug); release facts and blockers (10-25 paired-release fail on #167, relay FO: 0.3.29 already out); live notices to the doc FO for 0.2.29 to 0.2.32; inbound handovers filed (signed-out-card-shows-sign-in, rr-pairs-once); proposals to the dev2 FO (prototype contract; learn-names-agents-md). Work-changing exchanges noted in about 20 Web task files, not as `Peer:` lines.
2. Unasked needs: none recorded.
3. Skipped: the host binding (all messages via Paseo send_agent_prompt, not Claude Code ListAgents/SendMessage, because the Captain's sessions live in Paseo); never sent the probe (addressed ids the Captain named or that wrote first); often bundled two or three questions (e.g. 10-25 11:31); `Peer:` note never written.
4. Saved: 10-25 16:34 relay FO reported a possible Web 0.2.32 regression; it showed relay's own behaviour since 687559c3, stopping a false Web hotfix. 10-25 15:06 relay FO's limit facts traced "Too many visitors" to its own worker; screenshots moved to staging.
5. Could not: Codex sol implementation workers cannot be messaged mid-run; only wait for exit and re-dispatch.

## relay FO (dhaka, Paseo 1671c3a9), 2026-10-26

1. All with Web/v0 FO 295b873d over Paseo send_agent_prompt: 10-24 pair-once identity-card collision (joint direction the Captain approved; Web filed signed-out-card-shows-sign-in); 10-25 pair-once terminal-half handover (v0 task rr-pairs-once, Handover line in pair-once.md); 10-25 Paired computers as a menu kind, AC-25 (kind list frozen; became F4, slice 2); 10-25 "Too many visitors" traced to Web's screenshot worker, production stayed 150; 10-25 suspected Web 0.2.32 draft loss shown to be relay #368's remount; 10-26 the Captain's production check (Web returned owner and reviewer evidence). 10-24 and 10-25 with the dev2 FO: timing of the 0.27.0 and 0.30.0 landings.
2. Not asked: 10-26 PR #442, relay main's browser job failing since #440 on 14 room-route specs (part select moved in the Web shell); has not asked Web yet.
3. Skipped: most messages after the first lacked "if this is not you, say so"; 10-25 10:22 carried two items; used Paseo, not the covered Claude Code binding; whether every work-changing exchange reached the task file is not verified.
4. Saved: the 10-25 burst facts kept the Captain from raising production to 300, which he had already approved.
5. Could not: Web could not count production's store (needed the Captain's Netlify token); he ran the script himself.

## qnow dev2 FO (Paseo 519ab4c8), 2026-10-26

1. Exchanges: 2026-10-20 agents-md-adr-pointer, from the dev2 FO: the stale-ADR-branch finding plus the Captain's 「ADR 部分按你說的做」; it verified the facts (git ls-remote empty; local stale ref 3eaf303ad) and opened the backlog task (that task's Scope). 2026-10-21 debrief: product-analytics-posthog validation revise recorded on the Captain's 「qnow 按他建議做」, "relayed and verified". 2026-10-21 debrief: production-incident-agent hold; relay FO reported kc-ops-inbox names it first adopter; left to the Captain. 2026-10-26: this interview. No sends this session.
2. Unasked needs: none recorded.
3. Skipped: two Captain rulings recorded from relayed words, not his own (agents-md-adr-pointer Scope; posthog revise per debrief); no `Peer:` line in any qnow task file; no probe recorded; every exchange arrived as a Paseo agent message, a binding the extension does not list.
4. Saved: agents-md-adr-pointer; the finding exposed AGENTS.md sending agents to a deleted branch while a stale local ref served an old ADR copy; verification took two commands.
5. Could not: none recorded.

## FO reading (not a ruling)

Rule against practice, five FOs:

| Rule in EXTENSION.md | Followed | Note |
|---|---|---|
| Host binding: Claude Code `ListAgents`/`SendMessage`; other hosts not covered | 0 of 5 | All five used Paseo `send_agent_prompt`; none wrote `peers not run`. |
| One read-only probe, then `Peer: ... = <session id>` | 0 of 5 | All addressed ids the Captain named or that wrote first; the Address rule allows a Captain-named peer, not "wrote first". |
| Message opens "if this is not you, say so" | 0 of 5 | Paseo stamps the sender id (Paseo 0.12, see agent-peer-messaging memory); the opening line guards a Claude Code name that can change on restart. |
| One question per message | 2 of 5 | ops-inbox, web, relay bundled two or three. |
| A peer's words are never the Captain's ruling | 3 of 5 | qnow recorded two relayed rulings (agents-md-adr-pointer, whose relay came from this dev2 FO on 2026-10-20; product-analytics-posthog); ops-inbox recorded relayed quotes as "relayed" unverified. kc-paseo checked the Comms Officer's [User] line. |
| Record each work-changing exchange in the task file | partial | web in about 20 task files, not as `Peer:` lines; relay unverified; ops-inbox missed the vault exchange. |

Harms seen only by operators: a question steered into a peer's running turn was swallowed by that turn (ops-inbox, 10-23); Codex workers cannot take a message mid-run (web).

Value seen: four events where a peer's facts stopped a wrong action (web 0.2.32 false hotfix; production limit kept at 150 instead of 300; one-round vault answer; stale ADR branch found in two commands), and one release notice that saved a lookup (kc-paseo, 0.30.0).
