The observer report for `extension-instruction-reaches-dispatch`: 2 violations, 9 ok, 5 can't tell, 1 observed. The window runs from `8d9bb764` (task file added) to the state checkout's `HEAD`, with the task still at `status: validation`.

violation | rule: "at a worker dispatch of its stage FO adds its instruction line to the scope notes" (Extensions) | evidence: `implementation-6.md` has no `roborev` token, and the cycle 4 stage report has neither an `evidence=` line nor `roborev not run:` (`bbae150b`, `cd03ba59`). The merge-main dispatch ran without the gate. The validation cycle 4 Polish notes that no roborev evidence line existed for that head.

violation | rule: same sentence | evidence: `implementation-7.md` Checklist says only "roborev evidence= line on the new head (run until clean or twice)". It has no `roborev_gate.py` path and no instruction bullet (`0680df30`). The worker still produced `evidence=roborev:756`. `implementation-1.md` carries the full instruction in Scope notes. `implementation-3.md` and `implementation-5.md` carry the path in the Checklist, not Scope notes.

ok | rule: "an approval read as accepting a recommendation has that sentence in its question" (FO steps: review findings) | evidence: backlog "Approving accepts profile pilot as recommended" (`306db49d`). Ideation "accepts Decision 1 … and Decision 2 … each as recommended" (`031421c9`). Validation 1 "Approving accepts FO's recommendation to decline the Deferred risks and Polish" (`ebbcded9`). Validation 2 "Approving accepts FO's recommendation to decline the two round-4 Codex P2" (`2732fed1`). All four are `by: person:captain` and the ledger shows none by `agent:first-officer`.

ok | rule: "FO writes `Override:` … when the Captain chooses differently" (FO steps: review findings) | evidence: `override: null` on all four rows in the ledger. Each reason records acceptance of the recommendation, so the rule did not apply.

ok | rule: "`Precedent: ADR <number> — 「<Words line>」`" (FO steps: review findings) | evidence: both validation briefings carry "Precedent: ADR 0013 — 「不等 Copilot，也要修復它額度不足時的應對方式」". That string is the first Words quote in `docs/adr/0013-*.md`, and the ADR is not an always-asked kind.

ok | rule: "FO appends one entry per amendment … names the amendment in the next dispatch's checklist" (Captain amendments) | evidence: `### Amendment 1 — 2026-10-17, chat` has `Captain:`, `Asked:`, `Supersedes: AC-6` and `Design: none` (`9e98e7c7`, an add-only diff). `implementation-7.md` Checklist opens "Captain amendment 1 applied: AC-6 moved under it…" (`0680df30`).

ok | rule: "FO counts rounds and records the count in the committed gate summary" and the round-3 decline rule (FO steps: review findings, step 5) | evidence: briefing 2 says "External rounds: Codex 4 (… round 4 on ef7a360e two P2, declined under the round-3 rule)". `extension-instruction-followups.md` holds both P2s with decline reasons (`51a5fef8`). Cycles 1 and 2 show investigation, then "FO fix authorization" (`implementation-3.md`, `implementation-5.md`).

ok | rule: "Before the `gate prepare` that asks for merge, FO runs `delivery_gate.py check`" (Delivery authority) | evidence: I ran the check on briefing 2 at head `ef7a360e`. It exited 0 with "no second reviewer outcome is missing". Briefing 1 now exits 1 only because validation-5 is the latest record. Whether FO ran it before the ask is outside state.

ok | rule: peers listed under `extensions:` (Extensions) | evidence: no ruling in the task quotes a peer. The filing note quotes the Captain's own 「確認」.

can't tell | rule: "A Captain ruling is his reply to the question it settles" | evidence: the amendment's `Captain:` and `Asked:` lines are marked "(chat, 2026-10-17)", and the validation 1 reason quotes 「Ａ准」, whose "Ａ" names an option the briefing does not list. Both exchanges are in chat.

can't tell | rule: "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: absent from both briefing summaries and the task file (grep for "necessity" and "sufficien" finds nothing).

can't tell | rule: "FO runs `package_version.py` and `workflow_checkout.py` before each worker dispatch" (Stages) | evidence: all 13 records carry `Dispatched: 1383c911…`. That is the README's own commit, and the run output is not recorded in state.

can't tell | rule: second reviewer "joins only when a trigger holds" (Extensions) | evidence: "Second reviewer: copilot because the change alters the check run on every dispatch record at validation (dispatch rules)". The README list names "authority, approval, merge or review rules". Whether dispatch rules fall under it is a judgement.

can't tell | rule: FO "may explicitly decline" Deferred risk or Polish in the gate summary (FO steps: review findings, step 2) | evidence: absent. These validator findings appear in no briefing decline and not in `extension-instruction-followups.md`: the unbounded `find_readme` walk (cycles 4 and 5), the AC-8 note-skip with no distinguishing test (cycle 5), and the cycle 4 Polish items. Nothing in the rule makes declining mandatory.

can't tell | rule: Schema "Record `id`, `title`, `status`…" | evidence: no `id:` in the frontmatter of this task or of any of the 30 other tasks in the checkout. This is not an FO-subject sentence.

observed | `Reviewer:` line | evidence: absent. Ideation ran on sonnet and Surfaces is none. Validation was re-entered in cycles 2 to 5.

Coverage: I read the task file fully, all 13 dispatch records, all 4 briefings, the ledger rows for this task and the README sections that name FO. The `extension-instruction-followups` body and ADRs 0013 and 0014 I read only in part. The installed 0.23.0 `dispatch_records.py` lacks `--readme`, so I could not run the extension check itself. It passes without it: 13 records complete, exit 0. Chat, PR and CI evidence is not evaluated.
