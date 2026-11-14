Four workflow-record violations found; product correctness was not assessed.

violation | rule: "does not move or rewrite a criterion" (Captain amendments) | evidence: "Supersedes: AC-6", "Superseded text:", and replacement "**AC-9**" were committed with the amendment and its dispatch (92e8e8d99).

violation | rule: "before a worker reads it" (Stages) | evidence: "recorded after sending; the answer was sent at about 01:15" (implementation-1-message-1.md, c3b9b8c8c).

violation | rule: "Before asking the Captain outside a gate, FO runs" the ask command (Captain steps) | evidence: amendment "Asked:" exists; task asks.jsonl is absent throughout history (92e8e8d99..b5bdfa24b).

violation | rule: "this local gate never is" an external round (roborev extension) | evidence: "External rounds: 3" includes "roborev:1858" and "roborev:1860"; PR reviews/comments contain no posted RoboRev review (e6a568f38; GitHub).

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: complete bound-question matches for backlog "決定：要不要讓兩張任務" / "answering 「決定：要不要讓兩張任務"; ideation "決定：要不要核准" / "answering 「決定：要不要核准"; validation "決定：合併 #870" / "answering 「決定：合併 #870" (80c37df66, dc1de3fc1, abcf91379).

ok | rule: "distinct FO fix authorization" (FO steps: review findings) | evidence: "FO authorises all three repairs" in Feedback Cycles, retained rejection and message-4 checklist (c8afef4ab).

observed | evidence: "Reviewer: kc-dev-flow-2:engineering-reviewer not run 2026-11-14" with amendment-specific reason; role_triggers exits 0, no next lines (48cee4aea; b5bdfa24b).

ok | rule: "naming the finding, reason, candidate revision" (FO steps: review findings) | evidence: "FO declines Codex P2 Polish at 0b620345b" names nested-quote comparison and pre-adoption limitation; Captain's bound question explicitly includes that decline (e6a568f38).

ok | rule: "--reference <check record>" (Delivery authority) | evidence: reference:captain-question-outside-a-gate-is-an-open-record:validation:attempt-1:revision-1:item-2; time "2026-11-13T18:51:49Z"; head "0b620345b538b67f4c6522d8b97028038f1ec17d". Hash, head and both cleaned clause prefixes match (cabb09553).

ok | rule: "FO confirms both goal sufficiency and minimal necessity" (observer) | evidence: "an ask outside a gate is written as a record"; "the timeline helper, the design check" (cabb09553).

ok | rule: "merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it" (Delivery authority) | evidence: "carried: 4 of 4" (gh pr list, state refs).

can't tell | rule: "design_surfaces.py check" (backlog/ideation) | evidence: historical replay not executed: required temporary-file writes conflict with this assignment.

Coverage: 44c795094..b5bdfa24b. Read gates, eight dispatch records, amendments, relevant rules/extensions and FO changes; sampled worker evidence. Copilot refusal matches its saved receipt. Guarded merge_audit: exit 2 twice for API failure, then exit 0 using separately fetched identical gh output; fetch suppressed, local refs may be stale/invisible. Missing records may mean chat approval or state outside this repository. Historical design replay, original chat and hook registration remain unverified. No files or refs changed; state checkout clean.

```text
Remaining: Finding disposition and archive.
Next: Review findings (you, First Officer).
Closable: no
```
