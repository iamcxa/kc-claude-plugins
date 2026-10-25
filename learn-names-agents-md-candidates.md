---
title: learn can name an AGENTS.md candidate for the Captain and sees a task's operational records
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: proposal from the subspace-web/v0 dev2 FO (Paseo agent 295b873d), 2026-10-26, sent with the Captain's approval as relayed by that FO (「都做」), starting from his question, as relayed: 「這是否表示learn沒抓到這個問題，以及，learn可能需要幫忙找到應該要寫進去agents.md的教訓？」. Relayed words, not a ruling in this session; the Captain decides adoption.
- Bite (peer's account, 2026-10-25/26, subspace-web and relay): Web 0.2.32 was designed, reviewed and validated only on Web's test hosts and nobody opened the real relay page before release; a worker screenshotting production used up relay's per-network Room-entry limit and locked the Captain out; a validator's harness published to production by mistake. The Captain's fix is a few lines in relay's and Web's AGENTS.md (spacedock-dev/subspace-web#169 for Web).
- Why learn could not catch it (peer's reading of 0.30.0): it was not run; `skills/learn/SKILL.md` says "do not … edit AGENTS.md" and `skills/evaluate-learning/SKILL.md` says "A proposal to promote a rule into AGENTS.md does not establish that replacement" and "Do not edit AGENTS.md or learning.md", so there is no route for "this lesson belongs in AGENTS.md"; learn reads one task's merged PR and SD closure, while these lessons were FO-operational (dispatch scope, worker behaviour on production, an incident) and live in observer reports, dispatch records and gate summaries.
- Proposal (peer's, not decided): (a) evaluate-learning may mark an entry `AGENTS.md candidate` when a lesson is cross-task, repeated, operational (environment, production, authority) or says it applies to every agent in the repository; it still edits nothing, and the candidate goes to the Captain as one decision with the exact lines; (b) the evaluation pack includes the task's observer report, dispatch records and any incident FO recorded in task state; (c) optionally a periodic or release-time learn pass across tasks to find repeats.
- Upstream first: kc-dev-flow-2 `skills/learn`, `skills/evaluate-learning`, `scripts/learning.py`; kc-adr `read-adr` § Where new information goes (an operating instruction to agents belongs in CLAUDE.md or AGENTS.md); dev2 auto-learning design intent (package self-improvement is bridged by hand from learn no-change reasons).
- Non-goals: learn editing AGENTS.md itself; adopting any candidate without the Captain.
- Added 2026-10-26, results relayed by the subspace-web FO from six learn runs under 0.30.0: one add (hidden-file-draws-diagrams #157, a learning.md entry, waiting for the Captain); two not run (review-page-launch-polish #159, briefing-reads-like-a-page #160: `claim` refused behind job 1dc910b3, completed with delivery missing; one unsettled job per repository); three held (diagram-failure-says-why, web-serves-formats-list, briefing-frame-and-controls: FO appended Captain confirmations to the archived files after archive, and the closure check requires current bytes to equal the closure snapshot). Package-gap candidates named by that learn worker, not yet the Captain's to file: (1) the skill says `verdict: passed` while archives record `PASSED`; (2) no rule for an accounted, append-only Captain record added after archive, which holds learn; (3) one learning job in flight per repository; (4) no path for FO-operational lessons (this task). AGENTS.md-candidate examples from the same run: validators ran on Node 24 rather than the pinned 22.22.0 and 19 archive-build tests fail on 24; CI installs Chromium only, so Firefox and WebKit evidence never gates a merge; suite results under load averages of 40 to 100 are unreliable; a sibling session's `pkill` once killed a server mid-run.

## FO alignment

Alignment: needed before ideation: adoption, and which of (a) to (c), are the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
