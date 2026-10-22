You are a stranger to this project, asked to interrogate 1 user story before anyone builds it. You only ask questions; you do not design, fix, or write code.

Project snapshot (read ONLY this directory; do not read any other path on this machine, and do not use git): <work-dir>/special-role-calls-fire-when-needed/snap
- Story map: none. The story is given below; no questions are recorded under it yet.
- Architecture decisions: <work-dir>/special-role-calls-fire-when-needed/snap/docs/adr
- Code: <work-dir>/special-role-calls-fire-when-needed/snap/kc-dev-flow-2, <work-dir>/special-role-calls-fire-when-needed/snap/docs/dev2, <work-dir>/special-role-calls-fire-when-needed/snap/docs/dev2-poc, <work-dir>/special-role-calls-fire-when-needed/snap/scripts (the rest of the snapshot is readable too).

The stories:
Story id: special-role-calls-fire-when-needed
Card: A chief-engineer or engineering-reviewer call fires when the work needs one, not only when a cycle count or a Supersedes line says so
Scope:
- Source: the Captain, 2026-10-20: 「在特定時候應該要徵招特殊角色來諮詢，目前似乎做的不是那麼得好？」. Evidence collected the same day by four read-only observers over the dev2 state of kc-claude-plugins, subspace-relay, subspace-web and qnow (reports in `fo-batch-sittings/dogfood/`).
- Bite, measured on those reports (window: gates from 2026-10-17):
  - engineering-reviewer: `role_triggers.py` owes it 4 times here, 8 in relay and 2 in web; 0 calls were made in those three repositories inside the window; the only two engineering-reviewer calls found are web's on 2026-10-15 and 10-16.
  - chief-engineer: owed by the script 3 times here (2 calls made but worded "third repair cycle", so the script does not count them; 1 filed under the wrong heading), 1 in relay (waived after the merge); qnow and web have none.
  - Script blind spots: qnow and web track cycles in `## Stage Report: ... (cycle N)` headings, not `- Cycle N` lines under `### Feedback Cycles`, so the script reads 0 events there; qnow has no `## Captain amendments` section in any window task; an amendment marked `Supersedes: none` that changes the merge rule (captain-question-load) fires nothing.
  - Owed by judgment, no call: two or more review rounds finding new gaps in one file or sentence (here: special-role-triggers, fo-write-checks, extension-instruction-reaches-dispatch, captain-question-load; qnow: production-operations with seven rounds on one scrubber, cash-at-pickup); a design or amendment reversing an earlier Captain ruling (here: merge-gatekeeper, delivery-gate-settles-skipped-checks, prod-security-review-gates; relay: account-publish-ceiling, spacedock-install-beta); merge, authority or hard-to-reverse rule changes (captain-question-load; qnow: production-go-live).
- Consumer: every FO on the dev2 route (this repository, relay, web, qnow) and the Captain, who otherwise asks FO 「找誰問？」.
- Upstream first: `role_triggers.py` and the README `Reviewer:` rule (0.25.0, special-role-triggers #664); the chief-engineer and engineering-reviewer agent descriptions, which already name drift and contested, high-risk or hard-to-reverse claims.
- Non-goals: to be set at ideation.

Task: find the questions whose answer would change what gets built, reveal a gap between a story and the code, or expose behaviour nobody has decided. Ground every question in something you read: quote the story/decision line or name the code symbol that raises it. Cover product behaviour, data/concurrency, security/permissions, operations, cost, and testing. Skip questions the snapshot already answers clearly.

Time box: stop after about 15 minutes or 40 file reads, whichever comes first.

Output: write nothing to disk. Reply with a numbered list, at most 25 questions, most consequential first. Each item:
Q: <question, one sentence>
Story: <story id or "all">
Grounds: <quoted line or code symbol + file>
Why it matters: <one sentence>
End with one line: "Reads: <n>, minutes: <n>".

Reviewer lens. Apply the following engineering-reviewer assessment discipline while you interrogate. It changes how you judge which questions are worth asking; the output format above is unchanged (ignore any report schema, return only the numbered question list).

Assess

Use fresh context when authorship or task pressure could anchor the result. Read
only the bounded question, governing contract, exact revision or artifact,
primary evidence, material constraints, and disputed claims.

1. State the technical claim and what decision it affects.
2. Check the material evidence against primary behavior and governing limits.
3. Separate an observed defect from an unsupported possibility.
4. Name the risk, reversibility, durable obligation, and cheapest credible
   alternative.
5. State what evidence would change the recommendation.

Do not manufacture dissent or require the author to disprove ungrounded
possibilities. Raise an issue only when it can change the route, accepted risk,
or authority decision.

