# Feedback round 005

- Identity: round 005, status `open`, opened 2026-11-06, interviewer the kc-plugin dev2 FO (Paseo 2e87a82e), workflow docs/dev2 of iamcxa/kc-claude-plugins.
- Trigger and grant: the Captain 「開始」 (chat, 2026-11-06), answering 「要現在開始第 5 輪訪談嗎？」, after FO proposed anchoring at the close of batch 15 and using the four fixed questions of fo-feedback EXTENSION.md "Questions, version 1". Cadence: every three completed batches (index.md, Captain amendment 1 of fo-interviews-extension, 2026-10-28); batches 10 to 15 completed since round 004 (2026-10-28), so this round is overdue; anchor after this round: close of batch 15.
- Package: kc-dev-flow-2 0.35.0 installed; origin/main c44fc64f3 (2026-11-06). Topics: each extension the respondent's workflow lists, plus two core topics: (a) gates and Captain questions, (b) worker dispatch and worker permission requests.
- Frozen roster (source: `paseo ls -a`, 2026-11-06; transport: Paseo agent message, per the paseo extension):

| FO | Area | Paseo id | Status at freeze |
| --- | --- | --- | --- |
| relay FO | subspace-relay | 1671c3a9 | running (deferred until idle) |
| web FO | subspace-web, v0 | 295b873d | idle |
| qnow dev2 FO | qnow | 519ab4c8 | idle |
| kc-paseo-plugins dev2 FO | project-env | 8b2c2fc2 | idle |
| ops-inbox FO | ops-inbox | 46c2ebdf | idle |
| kc-journey-map FO | journey-map private host | d41e1313 | idle |

## Coverage

| FO | listed extensions | core (a) gates | core (b) dispatch |
| --- | --- | --- | --- |
| relay | pending | pending | pending |
| web | pending | pending | pending |
| qnow | pending | pending | pending |
| kc-paseo-plugins | pending | pending | pending |
| ops-inbox | pending | pending | pending |
| journey-map | pending | pending | pending |

## Exchanges

Bundled question text (sent once per FO, 2026-11-06): see the message recorded under each FO below.

Bundled text (identical to each FO, 178 words): the four fixed questions of fo-feedback EXTENSION.md "Questions, version 1", asked for each extension the respondent's README lists and for core topics (a) gates and Captain questions and (b) worker dispatch and worker permission requests; at most 300 words per topic with source links; window since 2026-10-28; answers are operator data, not Captain rulings.

Sends (Paseo agent message, steer, 2026-11-06; returned message ids):
- qnow dev2 FO 519ab4c8: 633ec9df-8f8a-4e5c-b0f2-b9db249aac77
- kc-paseo-plugins dev2 FO 8b2c2fc2: f260e9f2-5835-4a36-b072-560897552f47
- kc-journey-map FO d41e1313: 86935e92-46e3-4283-98c5-512e5bb0f677
- web FO 295b873d: f9a6f6d8-a9cf-4c0c-b033-d76cd34aad83 (first attempt with the short id returned "Agent 295b873d not found"; nothing sent)
- ops-inbox FO 46c2ebdf: 3fd362ce-957f-4c74-9909-bb42548ac80f (same short-id refusal first; nothing sent)
- relay FO 1671c3a9: 51d216d5-e672-485e-811f-74440ab1133e (idle by the time of send; no deferral needed)

## Evidence comparison

(pending answers)

## Findings and close

(pending)

### qnow dev2 FO, 519ab4c8 — answered 2026-11-06 (Paseo agent message b087cc6b, sender stamped)

Condensed in its own words; operator data, not verified yet.
- roborev: #1338 job 1524 clean; FO's dispatch record omitted the roborev_gate.py line (validator F3, declined as Polish); FO counted roborev as an external round and the observer flagged it; proposes delivery_gate.py question refuse round counts that cite roborev evidence.
- codex: #1338 clean on 9ad9bb170 (summary:6663772500); keep the one-call, one-line evidence.
- copilot: #1338 triggered as second reviewer ("touches authority" read broadly for a security change); quota refusal exit 5 handled as written; quota failure is silent until requested.
- learn: preview-sign-in-wildcard observer 27 findings (12 violations), evaluator no-change; FO first acked with `digest` not `notice_digest`; asks for a per-rule counter so repeated slips leave a trace.
- peers: landing FO 6f191513 asked a merge hold until #1337; held and released; prevented a strict-up-to-date race.
- journey-map, release-acceptance: unknown / none recorded.
- (a) gates: delivery_gate.py question failed on web paths in the validator's report read as local files, and check failed on a by-design skipped "Release Gate" run; the Captain waived both (「豁免網址路徑誤判」, 「豁免release gate跳過，合併1338」); design_surfaces.py's "Built screen review:" placement and preview-path rules took three runs. Captain-steps record let it answer the Captain with a fresh read.
- (b) dispatch: Codex capacity errors twice then a Claude fallback (office-action-audit-log ideation); about 6 validator permission requests on #1338; a follow-up addendum sent with no dispatch record (observer); pre-push hooks failed twice under Mac load; asks for a documented load gate.
- First links: the web-path false positive is the same class as backlog delivery-check-resolves-links-from-the-task (relative-path resolution in delivery_gate.py); the skipped-run false positive and the per-rule counter have no matching task yet.

### kc-paseo-plugins dev2 FO, 8b2c2fc2 — answered 2026-11-06 (Paseo agent message 78e1319b, sender stamped)

Condensed; operator data, not verified yet.
- codex: #66 one P2 fixed (fec5b13); r1b-polish-1 (#71 #72 #73 #75) one clean round each; on ready Codex posted only a security summary, codex_review.py exit 4 until `@codex review` (Bridge gap 7 again); asks pr_watch.py wait to print that next: line (~10 min per PR).
- journey-map: release review found pick-field half covered (Captain 「移出」); review not in the checked record format, journey-review.mjs check and interrogation not run; journey fields set after ideation, not at backlog (observer); journey-lint accepts evidence only in executable files, so a docs story could cite only a build script; asks non-executable evidence.
- learn: observer reports committed for all four tasks before merge guard; learn evaluations not run in window.
- roborev: #66 roborev:1483 clean; skipped for r1b-polish-1 and its instruction line left out of dispatch (observer).
- (a) gates: batch gates, one 「准」 per stage; an amendment written as prose Supersedes needed a rework round; Asked: line elided (observer); gate questions omitted later-review-rounds and worktree removal (observer, all four); delivery_gate check caught an owed engineering-reviewer call; stacked PRs conflicted after a squash merge, FO appended a Candidate line with a tree-equality note but no revalidation (observer violation); asks a recognised "rebased, identical tree" path.
- (b) dispatch: FO saved no dispatch records for the whole batch after a context compaction (reconstructed 2026-11-06, all four observers); asks `dispatch build --stamp` to write <task>/dispatch/<stage>-<cycle>.md itself; workers' `agent-browser close --all` closed unrelated sessions twice; a worker cut off by handback with a job running; `git reset --hard` refused twice, workers used merge --ff-only.
- First links: the worktree-removal omission is the class delivery-question-requires-worktree-clause (#793, merged 2026-11-06) now holds; codex security-only summary is Bridge gap 7 (autopilot-l3-dogfood-spacedock-bridge); the agent-browser collisions support worker-browser-checks-use-paseo-browser.

### kc-journey-map FO, d41e1313 — answered 2026-11-06 (Paseo agent message d503f791, sender stamped)

Condensed; operator data, not verified yet.
- paseo: ~30 Codex workers via plain create_agent with hand-written prompts, not `dispatch build --stamp`, and stage/gate state not advanced per dispatch (private-human-entry … private-host-parity, PRs #778 #779 #785 #789 #795); workspaces archived mid-session broke create_agent; FO-created terminals invisible to the Captain twice.
- peers: the dev2 FO's ADR 0063 notice prevented a second collision.
- roborev / codex / copilot: none run on #778 #779 #785 #789 #795; independent Astra validators used instead.
- learn: none; four tasks archived by merge guard.
- (a) gates: approvals for #778/#779 recorded in fo-notes/overnight-plan-20261104.md, not by gate prepare/record; private-native-account went backlog to merged PR #785 without ideation, implementation or validation stages (noted as owed); step-back fired on pairing round 2 and round 3 went to an independent reviewer.
- (b) dispatch: archive tags before every restack preserved approved SHAs; a sealed run package refused because origin/main moved (one re-seal worker).
- First links: gates recorded outside Spacedock and a task merged without its stages is an authority finding (theme 1); no matching task yet. Terminal visibility contradicts the paseo extension's human-terminal assumption; no matching task yet.

### web FO, 295b873d — answered 2026-11-06 (Paseo agent message 748bfc02, sender stamped)

Condensed; operator data, not verified yet. Workflow extensions: learn, peers, roborev.
- learn: no learn run at archive for #204 #206 #208 #209 #211 #212 #213 #214; merge guard printed "finalized … archived" with no learn line; asks merge guard to say "learn not run: <reason>".
- peers: relay FO exchanges changed a gate (pair-once does not keep drafts; Captain chose A, waits on relay's card-sign-in-keeps-unsent-comments) and stopped two needless changes (AC-22 card, AC-23 CSS); peer messages are not recorded in task files unless the FO copies them.
- roborev: every implementation ran roborev_gate.py (roborev:1474 to 1556), all clean first run except one rerun after a squash; caught nothing material in the window; asks to measure its yield.
- (a) gates: `gate record --round` impossible on validation revises (room holds only index.json, no review log); gate watchers die at the 2-hour background limit; delivery_gate 0.35.0's `External rounds: N` held twice; the Captain asked 「中文說明」 three times in one day (jargon in gate texts).
- (b) dispatch: about 35 dispatches; scope "Do not push" conflicts with the split-root "push the state branch" line, so workers left state commits unpushed; `status --set` refused a report whose checklist lines were paragraphs; dispatches named the 0.34.0 package root while workers used 0.35.0; six parallel browser workers pushed load to 23–350; asks a per-machine cap.
- First links: learn silence at archive matches backlog observer-check-learn-only-when-listed (inverse case); the "Do not push" conflict is in FO scope-note wording (the kc-plugin FO's validate.py carries the same sentence); the load cap matches fo-asks-to-raise-concurrency (inverse direction).

### relay FO, 1671c3a9 — answered 2026-11-06 (Paseo agent message d7c88af6, sender stamped)

Condensed; operator data, not verified yet.
- learn: pair-once (#442) and the continuity tasks each ran to a recorded end; two package-issue candidates still with the Captain (an unenforced rule lets a test pass falsely; the ADR counter is shared across repos).
- roborev: continuity-earlier-comments-beside-latest job 1511 High challenged by a fault-injection probe and ruled wrong by the engineering reviewer; job 1519 raised it again on unchanged code; the gate cannot carry a ruled disposition into the next job (one extra round).
- journey-map: backlog gates name their story; checking the map first stopped a duplicate story; owed "what this release can't do yet" note.
- release-acceptance: continuity walk passed with Codex as third reviewer; unknown whether it followed the extension's procedure.
- (a) gates: FO passed `gate prepare --artifact` the Chinese presentation file instead of the task file, so design_surfaces.py compared Scope against an empty baseline and held "Scope changed"; asks the checker to print "not run: bound artifact has no Scope" and gate prepare to warn when the artifact is not the task file; the Captain once could not find a gate in chat.
- (b) dispatch: Codex worker raised four permission requests, approved after reading the scripts; `dispatch build` printed "declared model 'sonnet' ignored on host codex"; create_agent refused to inherit mode 'auto' from a Claude caller; worker write scripts that refuse on a changed file made approval cheap; a worker read one deny as cancelling all runs; asks the deny reason to reach the worker with the deny.
- First links: the shared ADR counter is backlog adr-reservation-crosses-workflows; the create_agent mode refusal matches the kc-plugin FO's own batch 14 experience.
