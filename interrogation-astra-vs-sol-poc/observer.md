Observer report: interrogation-astra-vs-sol-poc (window 8464f7ce..HEAD 84de553a of the state checkout, 12 state commits). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-22.

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: backlog question "FO recommends yes; approving accepts that recommendation."; validation question "FO recommends closing; approving accepts that recommendation." Each briefing quotes the chat question it rests on, and each choice matches the recommendation (eea062cc, 180829c7).
can't tell | rule: "A Captain ruling is his reply to the question it settles, given after that question was put" | evidence: the backlog reason quotes 「可以但我還是不太確定，你說的是故事地圖套件的qa問答部分嗎？」, a hedged reply carrying his own question; state holds no later word of his before dispatch (46b25584, 8ab62bdf). Whether he re-affirmed is in chat.
can't tell | rule: same | evidence: the validation question adds "with the AC-2 caveat that the scorer knew the arm?" while the quoted chat question 「astra 和 sol 比較的那個 POC，要照結果結案嗎？」 names neither; briefing committed 4 s before the record (180829c7, 84de553a).
violation | rule: "FO records a Captain ruling only from his own words with their source" | evidence: the validation briefing summary says "the Captain kept sol on cost" with no quote, `Asked:` or gate question (180829c7).
violation | rule: Scope "scored against the same answer keys by a scorer blind to the arm" and AC-2 Falsifier "a score assigned with the arm known" | evidence: the validation dispatch named the arm and the sol totals; the validator recorded AC-2 as FAILED; no Captain amendment exists (71f2c79e, 773c3935, 180829c7).
ok | rule: "Scope, value, threshold … and acceptance-criteria changes require the Captain" | evidence: AC-1 and AC-2 unchanged; the unmet AC-2 named in the gate question and reason.
ok | rule: "Preserve the approved outcome, scope, non-goals, budget and stop condition in the body" | evidence: "Budget: one arm, five runs, one scoring pass; stop there." (8464f7ce).
ok | rule: FO alignment and design_surfaces.py check (backlog) | evidence: `check --seed` at 8464f7ce exits 0.
ok | rule: "A peer's words are never the Captain's ruling" | evidence: both reasons quote only him.
ok | rule: dispatch record lines (Stages) | evidence: `dispatch_records.py` "2 dispatch record(s) complete"; `--names` exit 0 on each.
ok | rule: roborev not run line | evidence: present in both records and reports.
can't tell | rule: sufficiency, necessity, delivery_gate before the merge ask | evidence: no merge ask; delivery is report.md.
can't tell | rule: ADR landing of a ruling later work must respect | evidence: keeping sol is a choice later work may follow; no ADR visible from state.
observed | `Reviewer:` absent; role_triggers 0 events.

Coverage: task file at HEAD and every state commit touching it, both dispatch records, both briefings, the ledger rows, the README sections named above and the peers EXTENSION.md; report.md and blind scores sampled by headings. Not evaluated: chat-only rules, the terminal ceremony.
