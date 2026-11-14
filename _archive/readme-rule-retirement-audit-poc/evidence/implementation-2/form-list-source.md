# Named form-check source

Source: `.context/dev2-reform/rework-ceremony.md`

SHA-256: `e507353495cee78897a983673b06d8501aee533a48fe769493d438e5fd4d27ec`

design_surfaces.py check --seed (B2-B4, B6); design_surfaces.py check (amendment form, AC id reuse, "Amended by Captain" marker, Worth questions) ; dispatch_records.py (bare script names, Package root line, main-completion line, checklist-not-pointer; --coverage = a record exists); decision_ledger.py --reason (reason must quote the bound question); delivery_gate.py question/steps (Sufficiency/Necessity clauses, External rounds: N, Captain steps: line, Unchecked counts: N); role_triggers.py (a dated `Reviewer:` line exists, not that the review changed anything); doc_impact.py (`updated|unaffected: reason` line); lint-skills.py word budget; laws_check.py (state-history shapes). OUTCOME checks: package_version, workflow_checkout, number_guards (migration numbers), delivery_gate head==Candidate and CI settled, adr_lint file exists, observer/merge_audit (audit after the fact).

B2 seed lines Non-goals / Budget / Stop condition (Schema; #740 seed-check-requires-schema-fields) E - FORM check
B3 `## FO alignment` need+reason (+ `Result:` line when needed) (### backlog; ideation principles hold otherwise; 4 tasks held on this) E - FORM
B4 `Surfaces:` and `Visible change:` lines (### backlog) E - FORM
B5 `Release review:` line or "not needed: reason" (### backlog; 204 of 246 tasks carry it) E - FORM
B6 `design_surfaces.py check --seed` before gate prepare (### backlog; #694 idle names failing seeds) E - FORM
B8 gate record: `decision_ledger.py --reason` + `Recommendation: followed` or `Override:` line (Review-finding disposition; "Override:" present in 109 tasks) E - FORM
B9 each number/claim in a gate summary or PR body names command + date (## Captain steps; #777 claims-name-their-source) E - FORM
D5 scope notes carry `Package root:` line + "send completion to main" line (#633) E - FORM
D7 `dispatch_records.py <task folder>` (record complete) E - FORM
D8 `dispatch_records.py --names --strict <record>` (bare package script names fail) E - FORM
D10 after each worker report `dispatch_records.py --coverage` (#743) E - FORM
I4 worker runs `design_surfaces.py check <task>`, cites output E - FORM
I5 FO runs the same check before `gate prepare`, includes output E - FORM
L2 `delivery_gate.py question ... --summary-file`; summary declares `External rounds: N` and second-reviewer outcome E - FORM
