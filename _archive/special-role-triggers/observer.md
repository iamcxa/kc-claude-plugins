Observer report: task `special-role-triggers`, window ef23231f (file added, 2026-10-16) to 97ddcb90 (state HEAD, 2026-10-18). RULES is the adopted README at `.../docs/dev2/README.md` (release marker kc-dev-flow-2 0.24.0, `extensions: [roborev, codex, copilot, learn, peers]`).

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings) | evidence: ledger rows quote 「准」 (backlog), 「那就照建議」 (ideation), 「批准並合併」 (validation). Each resolution `at` is later than its briefing commit: 952118f4 13:58 then 14:10; 772b7085 14:48 then 15:30; 47da8825 10:10 then 11:03 (becde7a3 11:03).

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: "Approving accepts profile pilot as recommended" (backlog); "Approving accepts the recommendations D1 ... D2 ... D3" (ideation); "Approving accepts FO's recommendation to decline the Deferred risks and Polish" (validation) (efdb3370, 670aaf4d, becde7a3).

ok | rule: "Override:", "Precedent:" and the grant for an `agent:first-officer` decision (FO steps: review findings; Delivery authority) | evidence: ledger `override: null` on all three rows; no `agent:first-officer` row; no `Precedent:` line. Validation question says "Approval also covers later external-review rounds on this PR, per Delivery authority", which matches the README sentence (becde7a3).

violation | rule: "FO names the amendment in the next dispatch's checklist." (Captain amendments) | evidence: the entry commit is 4c1b7183 (22:44:26) and the next dispatch is implementation-2.md, commit f4bb51b3 (22:44:36). Its `## Checklist` is only "Phase 1 only: reproduce the Codex P2 on #664 head 5afe7fd7 ... as a failing test". The amendment appears only under `## Scope notes` ("Apply Captain amendment 1 under ## Captain amendments"). The first checklist to name it is implementation-3 (32b899c0): "AC-10, Captain amendment 1".

violation | rule: "FO adds no words of its own" in an amendment entry; `Design:` is "<optional: the design paragraph it overrides>" (Captain amendments) | evidence: "Design: AC-2's date rule is changed so that an engineering-reviewer call dated no earlier than the amendment entry's date clears it, consistent with D3" (4c1b7183). The line is FO-composed, not a design paragraph. The Captain's recorded words are 「第四題同意」 and `Asked:` quotes the Chinese proposal.

ok | rule: amendment form (Captain amendments) | evidence: `Captain: 「第四題同意」 (chat, 2026-10-17)`, `Asked:` quoting the question (required, since his words do not name AC-2), `Supersedes: AC-2`. Later the worker moved the AC-2 block verbatim under `Superseded text:` and added AC-10 "Amended by Captain, amendment 1" (32ee3443).

violation (Polish items only; the two Deferred risks are ok) | rule: "FO may explicitly decline evidenced Deferred risk or Polish in the existing committed gate summary, naming the finding, reason, candidate revision and the lines or evidence it rests on." (FO steps: review findings, step 2) | evidence: summary reads "Declined, with reasons: Deferred risk, a fence opened with an unusual indent ... (no task writes one); Deferred risk, an uncommitted live task ... (as AC-4 specifies); Polish, a count of 16 vs 17 in the implementation report, design wording 'third line' vs N>=3, and one relay task where a call rather than a waiver is expected." The Polish items carry no reason or evidence in the summary (47da8825 briefing index.json). The revision is named at the top: "PASSED at b300d9ba".

ok | rule: step 5, "FO counts rounds and records the count in the committed gate summary"; step 3, distinct FO `fix` authorization, then independent validation (FO steps: review findings) | evidence: "External rounds: Codex 3 (round 1 two P2 ... round 2 one P2 ... round 3 clean)". Dispatches implementation-3 and implementation-5 read "phase 2 ... FO fix authorization"; validation-2 and validation-3 followed, each with its own `Candidate:`.

ok | rule: "FO records `second reviewer: <name> because <trigger>` ... in the gate summary" (Extensions) | evidence: "Second reviewer: copilot because the change alters review rules ... copilot not run: Copilot refused for quota on 2026-10-13 ..." The README form is lower-case; the summary writes "Second reviewer:".

ok | rule: FO saves each dispatch as `<task>/dispatch/<stage>-<cycle>.md` with SHA, Model, Checklist, Scope notes, `Candidate:` (Stages) | evidence: `dispatch_records.py` printed "9 dispatch record(s) complete"; `--names` over all nine exited 0; validation-1/2/3 each carry a `Candidate:` line; Model sonnet equals the README default.

ok | rule: `peers` extension, no Captain ruling quotes a peer | evidence: the three gate reasons and Amendment 1 quote only his words, marked "(chat, ...)". Whether the chat was a peer relay is outside state.

can't tell | rules: FO runs the minimal acceptance script as written and presents every step in full; `delivery_gate.py check` before the merge ask; `package_version.py` / `workflow_checkout.py` before dispatch; `design_surfaces.py` seed and ideation checks; FO confirms goal sufficiency and minimal necessity before recommending delivery; FO answers a question the Captain asks at a gate. | evidence: absent. The briefing summary says FO ran the script "in env -i bash"; no state line records the others. The ideation reason says he asked FO to restate the merge-gatekeeper D1 reasoning, and the answer is in chat. The word "necessity" appears nowhere in the task file or briefings.

can't tell | rule: Spacedock-owned `### Feedback Cycles` (not in RULES) | evidence: dispatches implementation-2 and implementation-4 say "The finding is under `### Feedback Cycles` in the task file", but `grep -c '^### Feedback Cycles'` at HEAD is 0. The Cycle 1 and Cycle 2 lines sit under the `### Words FO reads at each lifecycle moment` section (f4bb51b3, 30c10e74).

observed | rule: `Reviewer:` line (observer skill) | evidence: absent. No `Reviewer:` line in the task at HEAD. Surfaces is none, ideation ran on sonnet, and the two repair cycles followed PASSED validations, not rejections.

Coverage:
- Read fully: the task file at HEAD, the full window diff of the task file and `dispatch/`, the three briefing JSONs, the ledger rows for this task, the FO-subject README sections (Stages, backlog, ideation, validation, Review-finding disposition, FO steps, Captain amendments, Delivery authority, Extensions), and `special-role-triggers-followups.md`.
- Sampled: stage-report bodies, which are worker output and not judged.
- Not evaluated: PR, CI and chat events (ready-marking, merge, Codex review contents), and `role_triggers.py` calls owed, because that rule is not in this README.
