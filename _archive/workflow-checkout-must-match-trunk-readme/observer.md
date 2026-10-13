Findings for `workflow-checkout-must-match-trunk-readme` over `cce8355a`..`f11f449c` (2026-10-13, 15:12 to 16:43). I read state only.

violation | rule: "A checklist or scope-notes line that names a package script writes `<package>/scripts/NAME.py` with the absolute root substituted, never the bare script name." (Stages) | evidence: "adr_lint.py docs/adr --require 0014 passes" (dispatch/implementation-1.md:9), "adr_lint.py docs/adr --since <base> run with its exit code" (dispatch/validation-1.md:10, validation-2.md:11, validation-3.md:11), "the roborev_gate.py evidence= line" (dispatch/implementation-2.md:11, implementation-4.md:11) (869e93c4, 19459e04, 25064587, 9bfe5855, e2c39f65, 18629f00)

violation | rule: "When FO dispatches validation and nothing was pushed for the task, FO records `Applied: none as of <candidate sha>`" (FO steps: number guards, Applied). The Number guards section applies because the task lands ADR 0014. | evidence: "## Number guards\n\nADR: 0014" is the whole section at TO; no `Applied:` line (f455c4aa, 9f3f52d9). Reading note: the rule is written around migrations, and the task has none.

ok | rule: "FO saves those scope notes, the checklist, the model it dispatches on and the SHA it dispatches from as `<task>/dispatch/<stage>-<cycle>.md` ... A follow-up message to a worker FO resumes is a dispatch too, and its record carries the same parts." (Stages) | evidence: nine records, ideation-1, implementation-1 to 5, validation-1 to 3. Each has a `Dispatched:` line with the full SHA `e2524e93025dd0d5d9217b4d722c2b169d01fda6`, a `Model: sonnet` line, and non-empty Checklist and Scope notes. Each was committed with its own `state:` commit. Observed: implementation-3 and implementation-5 are follow-ups. Their checklist reads "Same checklist as implementation-2." / "...implementation-4.", and their scope notes carry no `Package root:` line. The rule names that line only for dispatches FO builds.

ok | rule: "A Needs decision put to the Captain at a gate carries FO's recommendation. His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: ideation question: "Approving accepts the recommendations for D1 (fetch inside the check; unreachable remote holds), D2 (strict equality; ...) and D3 (FO shows the remedy and waits ...)" (ledger row, 63cf0479). Ruling: "Captain 2026-10-13: 「准」". No `Override:` line is needed, since all three recommendations were accepted.

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings) | evidence: each briefing commit precedes its resolution commit. Backlog: 9ec4deb5 15:12 then 538acf31 15:17. Ideation: 6b259def 15:24 then 63cf0479 15:40. Validation: 361f13b8 16:33 then f11f449c 16:43. Validation question: "Approval also covers later external-review rounds on this PR, per Delivery authority." (f11f449c)

ok | rule: "FO's delivery gate question says that approval also covers later external-review rounds on the same PR." (Delivery authority) | evidence: the sentence quoted above is in the validation question; head 20c9ec53 matches "candidate #631 20c9ec53" in dispatch/validation-3.md.

ok | rule: "From round 3 a finding that is neither does not start a repair cycle: FO declines it in the committed gate summary, naming the finding, and files it as a new backlog task with `spacedock new`" (FO steps: review findings, 5) | evidence: "FO declines at candidate 20c9ec53: Codex round 3 P2 unquoted origin/<trunk> in the remedy and P2 remedy does not resolve an uncommitted README edit, both filed as backlog task workflow-checkout-round3-followups with reasons" (361f13b8). The task file exists with both findings and reasons (3b213fd8). The `spacedock new` command itself is not visible in state.

ok | rule: "FO records `second reviewer: <name> because <trigger>` or `second reviewer: not triggered` in the gate summary" (Extensions) | evidence: "Second reviewer: not triggered (Surfaces none, profile pilot, no authority, approval, merge or review rule changed)" (361f13b8). The README names `second-reviewer: copilot`.

ok | rule: "FO records the choice ... `## FO alignment` ... `Surfaces:` ... `Visible change:`" (backlog) and "FO records each printed `ADR: NNNN` line under `## Number guards` ... and repeats the lines as dispatch scope notes" (FO steps: number guards) | evidence: "Alignment: not needed before ideation", "Surfaces: none", "Visible change: none" (cce8355a). "ADR: 0014" in the task and "ADR: 0014 (reserved; ...)" in the implementation-1 scope notes (f455c4aa, 869e93c4).

ok | rule: the extension `peers` is listed in the README | evidence: the three Captain rulings quote only his own 「准」 and 「批准」, and no peer's words or peer's report of him.

observed | rule: Reviewer: line (record, not a requirement) | evidence: absent. The task has no `Reviewer:` line. Ideation ran on sonnet and Surfaces is none, but validation went back to implementation twice (Feedback Cycles 1 and 2).

can't tell | rule: "Before each worker dispatch FO runs `python3 <package>/scripts/package_version.py <this README>`" (Stages) | evidence: absent. No state trace for the nine dispatches; the run would have been in the session.

can't tell | rule: "Before `spacedock gate prepare`, FO runs `design_surfaces.py check <task>`" and the backlog seed check (ideation, backlog) | evidence: absent. The validation report records `design_surfaces.py check` exit 0, but that is the worker's run.

can't tell | rule: "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity" and "presents every step in full beside its observed output" (validation) | evidence: absent. The gate summary says only "FO ran its acceptance script as written in env -i bash: every step matched" (361f13b8). Any confirmation or full presentation was in chat.

can't tell | rule: "Preserve findings and assess the four evidence fields above, separating materiality, ownership and disposition" (FO steps: review findings, 1) | evidence: absent. The Cycle 1 and Cycle 2 entries say "both to fix (rounds 1 and 2 fix every finding)" and "one P1, to fix", with no four-field or Material/Polish classification (29c55745, a0015193).

can't tell | rule: "FO adds each PR it opens or pushes to with `pr_watch.py add`"; "number_guards.py check ... on the PR head before FO asks for merge" (Delivery authority, Number guards) | evidence: absent in state.

can't tell | rule: the ideation approval quotes the Captain's reply to a "combined ideation gate question" for three tasks | evidence: the ledger holds the per-task question only. The combined question and his reply (「准」 and the parenthetical "三個都批准，接受下列建議，照 1 → 2 → 3 實作") were in chat.

Coverage: I read in full the ledger rows for this task, all nine dispatch records, the briefing JSON, the follow-up backlog file and every FO-written hunk in the task diff. I sampled the worker stage reports and the Design section. I did not evaluate the rules listed under can't tell above. The following did not apply in the window: Captain amendments, Precedent lines, FO declines under `### FO declines`, and `agent:first-officer` decisions. The task has no `Override:`, `Precedent:`, `Amendment`, `Asked:` or `FO declines` text; I grepped for each.
