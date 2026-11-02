violation | rule: "When the Captain chooses differently from the recommendation, FO writes" (Review-finding disposition) | evidence: "並把 xhigh 上限寫進設定檔檢查" versus "接受 `max` 和 `ultra`沒關係"; Override absent from backlog resolution (62e9dccba).
violation | rule: "acceptance-criteria changes require the Captain" (Review-finding disposition) | evidence: "A roster-resolved dispatch from a committed repository roster stays owed after delivery." (fbf834f07, dispatch/validation-1.md); later report: "FO message e3223f76 withdrew its unauthorized timing statement" (7e62a909c).
violation | rule: "files it as a new backlog task" (Review-finding disposition, step 5) | evidence: "External rounds: 3." and "Declined: a deeper-indented block item"; no backlog task named or matching review:5734678752 found in committed state (2fe8cf2b0).

ok | rule: "FO records the choice" (backlog) | evidence: "profile: pilot"; Captain quotations and answered questions recorded for all four resolutions (7e62a909c).
ok | rule: "FO records the alignment result as a `Result:` line before dispatching" (ideation) | evidence: "Result: aligned at backlog" (7956884c9; dispatch 965713506).
ok | rule: "Release review: not needed: <reason>" (backlog) | evidence: "Release review: not needed: workflow maintenance, on no journey map." (7956884c9).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (Observer replay, backlog) | evidence: "seed fields and FO alignment recorded", exit 0 with --seed (7956884c9).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (Observer replay, ideation) | evidence: "design surfaces presentable", exit 0 on both bound snapshots (104a1e5b7; 50b30c74d).
ok | rule: "FO saves those scope notes, the checklist, the model it dispatches on and the SHA" (Stages) | evidence: "8 dispatch record(s) complete"; three Candidate lines and complete implementation/validation coverage (7e62a909c).
ok | rule: "FO appends one entry per amendment" (Captain amendments) | evidence: "Amendment 1", "Amendment 2", Captain/Asked/Supersedes fields; both named in subsequent checklists (a88f953df; dee92bdc0).
ok | rule: "FO records each printed" (FO steps: number guards) | evidence: "ADR: 0050" in task and implementation scope before dispatch (deb2075c4).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Observer replay) | evidence: "time": "2026-11-02T10:05:36Z", "head": "c2643dae831f9685166b7cd564d8d885e88a3f21"; briefing committed 10:05:40Z (2fe8cf2b0).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: sufficiency "a roster naming Opus resolves"; necessity "one shared list reader and the ADR" (05a0d5483, merge/ask-1.json).
observed | rule: "report whether a `Reviewer:` line exists" (Observer) | evidence: "absent"; two rejected validations retained (7e62a909c).
ok | rule: "report each `next:` line" (Observer) | evidence: "role triggers: 0 event(s) read", no next lines (7e62a909c).
can't tell | rule: "A merge ask names each listed reviewer that was not read" (Extensions) | evidence: "incomplete: the roborev daemon is not running"; summary names Codex/Copilot only; later RoboRev result requires provider evidence (7e62a909c).

Coverage: Full FO-state history/diff 50ee1e4a..7e62a909c, ledger, README at 146727ded, eight dispatches, four briefings, receipt; three historical replays. Worker evidence sampled only for FO-record context. Batch-wide readiness, original chat/peer provenance, FO acceptance-shell run and delivery-configuration verification remain outside state; not verified. No agent:first-officer resolution or Precedent applies. No product verdict.
