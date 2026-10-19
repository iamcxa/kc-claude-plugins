Observer report: task `number-guards-readme-shrink`, window 4756c3bc (task file added) to a18013f1 (state HEAD, the validation gate record). No violations found, and three items are outside state. The task is still at `validation`, with its gate application `pending`.

ok | rule: "FO also records, under a `## FO alignment` heading in the task file, whether FO direction alignment with the Captain is needed ... a `Surfaces:` line ... a `Visible change:` line" (Stages, backlog) | evidence: "Alignment: not needed before ideation; the Captain approved filing it ... Release review: not needed: workflow maintenance, on no journey map. Surfaces: none Visible change: none" (4756c3bc..HEAD)

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put" (FO steps: review findings) | evidence: three rows from `decision_ledger.py`, all `by: person:captain` with his words quoted: backlog "「批准這些作為第三批」", ideation "「照建議」", validation "「准」". Each briefing commit predates its resolution: backlog 00:53+08 < 16:57Z, ideation 01:33+08 < 00:43:58Z, validation 09:01:53+08 (01:01:53Z) < 04:37:32Z. (e34a6dca, d07eb343, 2287b273, a18013f1)

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: ideation question "Approving accepts D1 (...), D2 (...), and FO's implementation order below"; backlog question "Approving accepts profile pilot as recommended"; validation question "Approving accepts FO's recommendation to decline the Polish below" (briefing-1 index.json of each stage)

ok | rule: "When the Captain chooses differently from the recommendation, FO writes `Override: ...`" (FO steps: review findings) | evidence: all three rows show `override: null`, and each reason says he accepted the recommendation (a18013f1)

ok | rule: "FO never records as his ruling ... consent he gave earlier to a different question" (FO steps: review findings) | evidence: the task body cites 「那就照建議」 for D4 of workflow-budget-ratchet. The ledger row for that task's ideation gate carries the same quote, and its question says "D4 (Number guards becomes a follow-up task)". (4756c3bc)

ok | rule: "FO counts rounds and records the count in the committed gate summary" (FO steps: review findings, step 5); the roborev extension says the local gate is never a round (`extensions/roborev/EXTENSION.md`, Limits) | evidence: "External rounds: Codex 1 (clean, comment 2026-10-19T00:57Z). RoboRev local (865), not counted." (4d51a472, briefing artifact digest matches `git show 4d51a472:<task>`)

ok | rule: "FO records `second reviewer: <name> because <trigger>` or `second reviewer: not triggered` in the gate summary" (Extensions) | evidence: "Second reviewer: not triggered." The words match, the first letter is capitalised, and frontmatter has `second-reviewer: copilot`. (4d51a472)

ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish in the existing committed gate summary, naming the finding, reason, candidate revision and the lines or evidence it rests on" (step 2) | evidence: "Declined, with reasons: Polish, the README says --help lists the flags ... [the base's wording, unchanged by this PR]; Polish, one step of the evidence script ac2_fixture.sh prints a fixture error ... [an evidence aid, not shipped; the real message is pinned by MisconfigurationTests]", beside "PASSED at 7e47e870". The two Polish items were also filed in `number-guards-readme-shrink-followups.md`. (4d51a472)

ok | rule: "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity from the same candidate's existing route evidence" (validation, Gate content) | evidence: "Sufficiency: the cut removes only clauses whose script message tells the reader the next step ... Necessity: it is the Captain's ratchet follow-up (D4 ...)" (4d51a472)

ok | rule: "Before the merge ask, FO runs `delivery_gate.py check` ...; exit 1 or 2 holds the ask, as does a head other than the latest `Candidate:`" (Delivery authority) | evidence: `merge/ask-1.json` and `ask-2.json` both read `"verdict": "ask"` with head `7e47e8704573e163353a6a5ff80b0e79ea78eebc`, which equals `Candidate:` in `dispatch/validation-1.md`. Their times, 01:02:29Z and 01:02:38Z, are after the briefing and before the resolution. (4d51a472)

ok | rule: "FO saves those scope notes ... as `<task>/dispatch/<stage>-<cycle>.md` ... (for validation a `Candidate: <full head SHA>` line)"; scope notes carry `Package root:` and the `Send your completion message to `main`` line (Stages) | evidence: all three dispatch files carry both lines. `validation-1.md` has `Candidate: 7e47e870...`. `dispatch_records.py` printed "3 dispatch record(s) complete", exit 0, and `--names` exited 0 on each file. (eea28c39, e36b77ed, e4c2ec65 and the dispatch-file commits)

ok | rule: "Approval of a validation gate is not permission to ... merge a PR, except as follows ... the merge still go[es] to him" (Delivery authority) | evidence: the grant is in the question he approved, "FO marks it ready and merges it, unless you say you merge?", and the reason records "so this approval carries the merge". No FO-recorded decision (`agent:first-officer`) exists in the task. (a18013f1)

observed | `Reviewer:` line | evidence: absent. None of the triggers holds: `Surfaces: none`, ideation `Model: sonnet`, one validation attempt. `role_triggers.py` printed "0 event(s) read at HEAD, each with a call or a waiver." No `next:` line, so no violation.

can't tell | rule: "Before `gate prepare`, FO runs `design_surfaces.py check --seed <task>`" (backlog Seed check) and "Before `spacedock gate prepare`, FO runs `design_surfaces.py check <task>`" (ideation) | evidence: absent in state. The ideation worker's report records the check exit 0, but the FO run is not recorded. FO's own run happens outside state.

can't tell | rule: "FO runs the stage's minimal acceptance script exactly as written in a fresh shell, then presents every step in full beside its observed output" (validation, Gate content) | evidence: the briefing says "FO ran the acceptance script as written in env -i bash: every step matched", and the script is in the pinned task-file artifact. No per-step observed output from FO's run is in state. What the Captain was shown is in chat.

can't tell | rule: a round is "one verdict of an external reviewer of the delivery on the PR head" (step 5) | evidence: "Codex 1 (clean, comment 2026-10-19T00:57Z)" has no `evidence=` id. Whether that comment was on head 7e47e870 is on the PR.

Not applicable in this window:
- Number guards: `Surfaces: none`, no ADR landed, and the task has no `## Number guards` section.
- Captain amendments: none, so there is no `Asked:` line.
- `Precedent:` lines: none.
- Peers: no ruling quotes a peer.
- Step 5 round-3 filing: only round 1 occurred.
- Merge or archive: not yet done.

Coverage: I read the task file in full (270 lines) and the three dispatch files, both merge asks, all three briefings and the follow-ups file. I read workflow README lines 1 to 595 in full and ran `decision_ledger.py` for the task rows plus the workflow-budget-ratchet ideation row. I read the codex, roborev and peers `EXTENSION.md` files and ran `role_triggers.py` and `dispatch_records.py`. I did not read the copilot extension or the learn extension. Whether the Decision records rule applies to the D2 ruling (ownership of the ADR-line check) is a judgement call I did not evaluate.
