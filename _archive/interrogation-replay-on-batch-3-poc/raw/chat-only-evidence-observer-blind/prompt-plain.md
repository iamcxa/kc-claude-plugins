You are a stranger to this project, asked to interrogate 1 user story before anyone builds it. You only ask questions; you do not design, fix, or write code.

Project snapshot (read ONLY this directory; do not read any other path on this machine, and do not use git): /tmp/replay-ext-ycemcP/chat-only-evidence-observer-blind/snap
- Story map: none. The story is given below; no questions are recorded under it yet.
- Architecture decisions: /tmp/replay-ext-ycemcP/chat-only-evidence-observer-blind/snap/docs/adr
- Code: /tmp/replay-ext-ycemcP/chat-only-evidence-observer-blind/snap/kc-dev-flow-2, /tmp/replay-ext-ycemcP/chat-only-evidence-observer-blind/snap/docs/dev2, /tmp/replay-ext-ycemcP/chat-only-evidence-observer-blind/snap/docs/dev2-poc, /tmp/replay-ext-ycemcP/chat-only-evidence-observer-blind/snap/scripts (the rest of the snapshot is readable too).

The stories:
Story id: chat-only-evidence-observer-blind
Card: FO rules whose evidence lives only in chat leave the observer at can't tell
Filed from a learn package-issue candidate the Captain approved on 2026-10-13 (「按建議1,3」). The observer reports on tasks `fo-record-checks` (PR #640) and `learn-delivery-follow-through` (PR #639) both marked the same FO rules `can't tell`, because the rules require FO to do something in front of the Captain but not to leave a record in state.
Scope:
- Rules read as `can't tell` in both reports: the validation step "presents every step in full beside its observed output"; "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity"; Delivery authority "present the exact candidate and PR body before authorized push/create". In one report each: the head read before the merge ask, the backlog `design_surfaces.py check --seed` run, `pr_watch.py add`, and whether a gate ruling needs an ADR.
- Learn judged it no-change: the rules exist and attribution to an outcome is unknown. The package question is whether each rule should name the record FO leaves (for example a line in the committed gate summary), or be accepted as chat-only and dropped from the observer's checks.
- Non-goals: to be set at ideation.

Task: find the questions whose answer would change what gets built, reveal a gap between a story and the code, or expose behaviour nobody has decided. Ground every question in something you read: quote the story/decision line or name the code symbol that raises it. Cover product behaviour, data/concurrency, security/permissions, operations, cost, and testing. Skip questions the snapshot already answers clearly.

Time box: stop after about 15 minutes or 40 file reads, whichever comes first.

Output: write nothing to disk. Reply with a numbered list, at most 25 questions, most consequential first. Each item:
Q: <question, one sentence>
Story: <story id or "all">
Grounds: <quoted line or code symbol + file>
Why it matters: <one sentence>
End with one line: "Reads: <n>, minutes: <n>".
