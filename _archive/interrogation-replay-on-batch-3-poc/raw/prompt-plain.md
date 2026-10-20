You are a stranger to this project, asked to interrogate 1 user story before anyone builds it. You only ask questions; you do not design, fix, or write code.

Project snapshot (read ONLY this directory; do not read any other path on this machine, and do not use git): /tmp/replay-w0OHE1/snap
- Story map: none. The story is given below; no questions are recorded under it yet.
- Architecture decisions: /tmp/replay-w0OHE1/snap/docs/adr
- Code: /tmp/replay-w0OHE1/snap/kc-dev-flow-2, /tmp/replay-w0OHE1/snap/docs/dev2, /tmp/replay-w0OHE1/snap/docs/dev2-poc, /tmp/replay-w0OHE1/snap/scripts (the rest of the snapshot is readable too).

The stories:
Story id: captain-question-load
Card: The Captain answers fewer FO questions per delivered task, without losing a decision that is his
Filed for batch 3 on the Captain's 「先走批次三規劃」 (chat, 2026-10-19), after FO reported that most of his turns in batch 2 were answering FO's questions rather than reviewing PRs. His goal for batching (chat, 2026-10-16): 「這樣我才可以從一直在追每個 FO 過程中解放出來」.
Scope:
- Measure first, from the batch-2 decision ledger rows and the gate briefings of this workflow (2026-10-17 to 10-19): every Captain decision per task, split into stage gates, Needs decisions, amendments, merge asks, and procedural asks (a push the permission check refused, a throwaway repository, a PR-body edit, a waiver), and how many he answered with a plain approval of FO's recommendation.
- Then find which kinds a written standing rule could settle without him (for example a delivery gate that carries the merge grant by default, or a repair inside an approved design), and which must stay his (ADR 0011: authority, approval, merge, outward-facing actions, irreversible changes and money).
- Existing pieces: batch sittings (memory note fo-batch-sittings-interim), pre-authorized merges at delivery gates, the qnow R11 batching numbers the qnow FO owes.
- Non-goals: to be set at ideation.

Task: find the questions whose answer would change what gets built, reveal a gap between a story and the code, or expose behaviour nobody has decided. Ground every question in something you read: quote the story/decision line or name the code symbol that raises it. Cover product behaviour, data/concurrency, security/permissions, operations, cost, and testing. Skip questions the snapshot already answers clearly.

Time box: stop after about 15 minutes or 40 file reads, whichever comes first.

Output: write nothing to disk. Reply with a numbered list, at most 25 questions, most consequential first. Each item:
Q: <question, one sentence>
Story: <story id or "all">
Grounds: <quoted line or code symbol + file>
Why it matters: <one sentence>
End with one line: "Reads: <n>, minutes: <n>".
