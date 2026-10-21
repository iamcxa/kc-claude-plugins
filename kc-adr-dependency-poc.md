---
title: dev2 uses an independent kc-adr package for ADR writing tools, installed and updated on Claude Code and Codex, and refuses loudly when it is absent or too old
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:kc-adr-dependency-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kc-adr-dependency-poc-backlog-1
              briefing:
                id: briefing:kc-adr-dependency-poc:backlog:attempt-1:revision-1
                digest: sha256:d8d71475e10d32cce09012486c4aa2839131756a72eab60d9346a9a219f80c90
                room-ref: ./kc-adr-dependency-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kc-adr-dependency-poc:backlog:1
                briefing: briefing:kc-adr-dependency-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T13:01:23.915549Z"
                decision: approve
                reason: Captain 「好，開」 (chat, 2026-10-21), answering FO's question put before it (quoted in the gate question); this briefing binds that question and answer after the fact.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-21T13:01:50Z
worktree: .worktrees/spacedock-ensign-kc-adr-dependency-poc
---

## Scope

- Source: the Captain, 2026-10-21. He chose (in the kc-adr session, relayed by Paseo agent 1bcf070c and then put to him here) that kc-adr is the package for agents reading and writing ADRs, dev2 its first consumer and moneyflow its second. Here he described his picture: 「我原本想像是，kc-adr是獨立的套件，dev2直接使用它，永遠取用最新的版本，等於在檔案層面用ln之類的方式硬連結，所以如果它更新那dev2也會更新，不受影響。這樣合理嗎？等於例如以後我做了fin flow它可以照樣取得adr工具包？」, then 「先poc看看怎樣更好？」 and 「好，開」 to FO's POC plan.
- Questions, each answered by a real install on Claude Code and on Codex, not by reading a neighbour's setup:
  1. Can a plugin declare a dependency on another plugin natively (Claude Code plugin manifest and marketplace; Codex plugin manifest)? Cite each tool's own docs or `--help`.
  2. Does a symlink from dev2 to kc-adr files survive `claude plugin install`/`update` from the marketplace and the Codex local install, and does a kc-adr update reach dev2?
  3. Can a dev2 script resolve the installed kc-adr at run time on each install layout (Claude marketplace cache, `~/.claude/plugins/local`, `~/.codex/local-plugins`), and refuse with a clear message when kc-adr is absent?
  4. How does dev2 refuse a kc-adr too old or too new for it (a version floor read at run time, and a CI job that tests the two together)?
- Arms: native dependency (if one exists), symlink, run-time resolution, and wrap-not-move (today's tools stay in dev2) as the control.
- Bar: installs on both hosts; a kc-adr update reaches dev2; absent kc-adr refuses loudly; an incompatible version is caught. The report recommends one arm and names what a move would change in the four adopters' READMEs and pins.
- Inputs: the kc-adr boundary contract (PR #691, `docs/journey/kc-decision-log/boundary-contract.md`), its wrap proposal (relayed 2026-10-21), `number_guards.py` (one script and one reservation file for ADR and migration numbers, ADR 0002), `adr_lint.py`, the ADR template.
- Non-goals: moving any tool now; changing any adopter; splitting `number_guards.py` (the report only says what a split would need).

## FO alignment

Not needed before implementation. The Captain asked for this POC (「好，開」, 2026-10-21) after FO showed him its four questions, arms and bar, restated above. Release review: not needed: the task belongs to no release.
Surfaces: none
Visible change: none
