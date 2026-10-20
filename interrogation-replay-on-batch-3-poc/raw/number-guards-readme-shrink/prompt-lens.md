You are a stranger to this project, asked to interrogate 1 user story before anyone builds it. You only ask questions; you do not design, fix, or write code.

Project snapshot (read ONLY this directory; do not read any other path on this machine, and do not use git): /tmp/replay-ext-ycemcP/number-guards-readme-shrink/snap
- Story map: none. The story is given below; no questions are recorded under it yet.
- Architecture decisions: /tmp/replay-ext-ycemcP/number-guards-readme-shrink/snap/docs/adr
- Code: /tmp/replay-ext-ycemcP/number-guards-readme-shrink/snap/kc-dev-flow-2, /tmp/replay-ext-ycemcP/number-guards-readme-shrink/snap/docs/dev2, /tmp/replay-ext-ycemcP/number-guards-readme-shrink/snap/docs/dev2-poc, /tmp/replay-ext-ycemcP/number-guards-readme-shrink/snap/scripts (the rest of the snapshot is readable too).

The stories:
Story id: number-guards-readme-shrink
Card: The Number guards passage of the workflow README shrinks to what number_guards.py cannot tell its reader
Filed under D4 of workflow-budget-ratchet, approved by the Captain on 2026-10-17 (「那就照建議」 to the batch-2 ideation gates, whose question said approving accepts D4: "Number guards becomes a follow-up task").
Scope:
- Measured by workflow-budget-ratchet's ideation on 0.24.0: the Number guards passage of `kc-dev-flow-2/references/sd/workflow.md` is 745 words, 13.6% of the README, the largest single candidate for the ratchet's shrink rule; its script messages were not read there.
- Apply the ratchet's rule: read each `kc-dev-flow-2/scripts/number_guards.py` failure message first; a rule the script enforces and whose message tells the reader what to do shrinks to one pointer sentence; the budget falls by the words removed in the same change.
- Bite to confirm at ideation: the observer's count of number-guard violations (an ADR number reserved after the first implementation dispatch happened twice, on prod-security-review-gates 2026-10-16/17).

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

