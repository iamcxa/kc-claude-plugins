violation | rule: "A checklist or scope-notes line that names a package script writes `<package>/scripts/NAME.py` with the absolute root substituted" (Stages) | evidence: "A design for kc-dev-flow-2/scripts/dispatch_records.py" (08eb82963, dispatch/ideation-1.md; before 9ee99c0f6 allowed relative paths).
violation | rule: "Start in the assigned worktree; verify pwd and git root before edits." (paseo extension / Codex workers) | evidence: "absent" (3ed9a5f6a, dispatch/validation-1.md scope notes).
violation | rule: "The summary declares `External rounds: N`" (Delivery authority) | evidence: "absent" (3f622655f, validation briefing-1 summary; question replay exits 1).
ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "對，全准且全確認"; "准"; "可以" (c9a6f7bd9, 9ee99c0f6, 1b0112f69; each follows its recorded question).
ok | rule: "plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: "approving accepts that recommendation"; "approving accepts these asks" (f3686a132, 4b96c7fc3).
ok | rule: "a decision by `agent:first-officer` carries the grant it relies on" (Observer / Read) | evidence: "並授權改完直接進實作？要改哪張直接說。 — 准" (9108b6c5d, conn quote/source).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog / Seed check) | evidence: "seed fields and FO alignment recorded" (73aa6fd46; --seed replay exits 0).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (ideation / Gate content) | evidence: "design surfaces presentable" (058a22542, b08dc2ac8; both replays exit 0).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Observer / Read) | evidence: "2026-11-01T07:39:26Z"; "9f065b01f1c6d6561793a168f584075edb85bf1f" (877a024e2; briefing added 07:39:41Z).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation / Gate content) | evidence: sufficiency "shown by three replayed batch-9 incidents and 1281 pinned records"; necessity "mutations remove each retained behaviour and fail" (877a024e2, merge/ask-1.json).
ok | rule: "never counts as a clean result" (Extensions) | evidence: "copilot not run:"; "Copilot retry: available when the Captain confirms quota is back." (3f622655f; saved refusal matches).
observed | rule: "`Reviewer: <agent> <model> <date> — <question>`" (Stages) | evidence: "Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-30" (058a22542).
can't tell | rule: "wait for every member's sufficient committed evidence" (Batch gates) | evidence: "absent" (a6691c681; other members and actual sitting outside task state).
can't tell | rule: "FO commits task state only through SD commands" (Workflow State) | evidence: "state: update names-check-says-what-it-skipped" (3f622655f; actual shell invocation outside state).

can't tell | rule: "FO reads each round" (codex extension / Read) | evidence: "Codex review: no major issues on this head, comment:6521179906." (3f622655f; original PR evidence outside state).
can't tell | rule: "is landed as an ADR before the next gate is presented" (FO steps: decision records) | evidence: "No new ADR" (a6691c681; code-repository landing outside state).

Coverage: Window 14561dab3..a6691c681; README a66129489, package 0.33.1. Read history/diff, FO sections; read five dispatches, four briefings, ledger and receipt; sampled reports. Design replays passed; scope checks skipped outside Git. Role triggers: zero events. No overrides, precedents, declines, amendments or migrations recorded. Captain attribution is record-level; chat, batch readiness, review truth, decision-record landing and command invocation remain unverified. Excluded skill-listed chat-only rules; no product assessment.
