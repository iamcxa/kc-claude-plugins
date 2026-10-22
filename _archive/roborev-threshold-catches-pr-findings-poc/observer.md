Observer report: roborev-threshold-catches-pr-findings-poc (window bc7c3985..c4ac8f95 on spacedock-state/dev2-poc, 12 commits). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-22.

violation | rule: "At a worker dispatch of its stage FO adds its instruction line to the scope notes" (Extensions; roborev listed) | evidence: `dispatch_records.py` on `dispatch/implementation-1.md` as committed prints "roborev worker instruction is absent; … or add a line 'roborev not run: <reason>'" and exits 1 (77d15805)
violation | rule: "FO runs `python3 <package>/scripts/dispatch_records.py <task folder>` before committing and fixes each part it lists" (Stages) | evidence: the exit-1 record was committed at 77d15805 and the validation dispatch followed at 7adde61c; the fix is the dated correction "roborev not run: the POC changes no code, so there is no candidate to review." (e9f5123f)
violation | rule: "A listed extension that cannot run … is reported as `<name> not run: <reason>` in the stage report or gate summary" (Extensions) | evidence: absent from the implementation Stage Report and the validation briefing summary (891d0f9d); only the dispatch correction (e9f5123f) and validator F1 (3916cefb) carry it.
violation | rule: "Record `id`, `title`, `status`, `variant: kc-dev-flow-2`, and the user's selected `profile`" (Schema) | evidence: no `id:` key (bc7c3985; unchanged at c4ac8f95).
can't tell | rule: "His plain approval accepts that recommendation only when the gate question says so" | evidence: the bound question says "FO recommends closing; approving accepts that recommendation …" (891d0f9d); the chat question 「roborev 門檻 POC 照結果結案、不改設定，可以嗎？我建議結案。」 carries no such sentence; same shape at backlog (660c1c04, 2b678e21).
ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put" | evidence: 「做」 answers 「要先做這個 roborev 門檻 POC 嗎？我建議做。」 (2b678e21); 「可以」 answers the closing question (c4ac8f95).
ok | rule: Override line | evidence: both approvals follow the recommendation; no `Override:` (c4ac8f95).
observed | rule: FO declines Deferred risk or Polish in the committed gate summary (step 2) | evidence: summary names F2 and F4 as open; F3 not mentioned; no `### FO declines` (891d0f9d).
can't tell | rule: "Preserve findings and assess the four evidence fields" (step 1) | evidence: no FO classification recorded beyond the validator's.
ok | rule: design_surfaces.py check --seed | evidence: "FO alignment recorded", exit 0 (bc7c3985).
ok | rule: FO alignment record (backlog) | evidence: "Alignment: not needed before implementation; …" (bc7c3985).
ok | rule: Package root, Send-to-main, Dispatched, Model lines (Stages) | evidence: both records carry them; validation record "Candidate: 90add27c…" (77d15805, 7adde61c).
ok | rule: role_triggers.py | evidence: "0 event(s) read at HEAD …" (c4ac8f95).
can't tell | rule: delivery_gate.py check; sufficiency and necessity | evidence: no merge ask and no `pr:`; a local-merge POC.
can't tell | rule: ADR landing for a ruling later work must respect | evidence: keeping `.roborev.toml` at high; the ADR directory is outside the state checkout.

Coverage: README in full; every state commit touching the task (12) as diffs; the task file at HEAD; both dispatch records; both briefing index.json; ledger rows; roborev, codex, copilot, peers, learn EXTENSION.md; replays of dispatch_records.py, design_surfaces.py --seed, role_triggers.py; briefing digests checked. Not read: report.md and worker reports for product content. Not evaluated: chat-only rules, second-reviewer/codex/copilot rules, learn, peers.
