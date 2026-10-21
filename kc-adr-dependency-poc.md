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

## Acceptance criteria

These restate the Scope's bar line by line and add no requirement; FO omitted the section from the seed (the dev2-poc route has no ideation stage to write it), and the implementation report's design check exited 1 on its absence.

**AC-1** Each arm's install is observed on Claude Code and on Codex. Evidence: report.md result table, Installs column, one observed row per arm and host. Falsifier: a cell filled from documentation alone is marked as such.

**AC-2** For each arm, whether a kc-adr update reaches dev2 is observed on both hosts. Evidence: the result table's update column. Falsifier: an update run where dev2's resolved kc-adr version does not change.

**AC-3** For each arm, whether an absent kc-adr refuses loudly is observed on both hosts. Evidence: the result table's absent column with the printed message or state. Falsifier: an absent kc-adr that exits 0 or prints nothing.

**AC-4** For each arm, whether an incompatible kc-adr version is caught is observed on both hosts, and the report recommends one arm and names what a move would change in the four adopters' READMEs and pins. Evidence: the result table's version column, the Ruling and the adopter section. Falsifier: an out-of-range version that runs.

## FO alignment

Not needed before implementation. The Captain asked for this POC (「好，開」, 2026-10-21) after FO showed him its four questions, arms and bar, restated above. Release review: not needed: the task belongs to no release.
Surfaces: none
Visible change: none

## Stage Report: implementation

- DONE: Answer the four questions in the task Scope with real installs, one arm at a time (native dependency if either host has one, symlink, run-time resolution, wrap-not-move as the control), on Claude Code and on Codex, each claim citing the tool's own docs, `--help` or the observed install result
  Claude has native dependencies (docs plugin-dependencies; observed install, update, uninstall, conflict). Codex has none (manifest docs, `app-server generate-json-schema` types, observed install). Symlink survives Claude install only as a frozen copy and is dropped silently by Codex. Run-time resolution met the bar on both hosts. Table in report.md.
- DONE: A report under the task folder in the state checkout (report.md) with one row per arm and host against the bar (installs, update reaches dev2, absent kc-adr refuses loudly, incompatible version caught), the recommended arm, and what a move would change in the four adopters' READMEs and pins
  `kc-adr-dependency-poc/report.md` in the state checkout. Recommends run-time resolution; adopter counts verified for three of four (carlove-v1 has no checkout locally, stated as unverified).
- DONE: Every probe runs with throwaway plugin roots and an isolated config (for example a temporary HOME or CLAUDE_CONFIG_DIR and a temporary Codex home), never the Captain's real ~/.claude or ~/.codex installs, and each probe directory is removed after; the report states the isolation used
  Temporary HOME, CLAUDE_CONFIG_DIR, CODEX_HOME under /tmp; directory deleted; real config files grep-clean and unmodified. One slip (a command ran once against the real config with a nonexistent path, wrote nothing) is disclosed in report.md.
- SKIPPED: roborev, comment_ratio.py, number_guards.py, doc_impact.py
  No repository diff exists (the POC writes only report.md in the state checkout); the task has no `## Number guards` section and `Surfaces: none`.
- FAILED: `python3 <package>/scripts/design_surfaces.py check <task>`
  Exit 1: `missing '## Acceptance criteria' section`. The POC route skips ideation, so the task never had one; I did not add one (task body is FO's). Returns to FO.

### Summary

Run-time resolution is the only arm that meets all four bar items on both hosts; Claude's native dependency works as an install-time add-on but Codex has no equivalent, and a symlink fails on both. A tag-name mismatch (Claude needs `<plugin>--v<version>`, release-please cuts `<plugin>-vX.Y.Z`) would affect the native arm and was read from files, not run. Not proved: a live model session, auto-update, disabled-but-installed kc-adr, carlove-v1 READMEs.

## Stage Report: implementation (cycle 2)

- DONE: kc-dev-flow-2/scripts/design_surfaces.py check on the task file: FO added `## Acceptance criteria` restating the Scope's bar; run the check and record its output and exit code
  `python3 -B <package>/scripts/design_surfaces.py check .spacedock-state/kc-adr-dependency-poc.md` printed `kc-adr-dependency-poc.md: design surfaces presentable` and `scope check not run: stage is implementation, not ideation`; exit code 0 (cycle 1 exited 1 on the missing section).
- DONE: Map AC-1 to AC-4 to report.md's result table, Ruling and adopter section, one line each, without changing report.md
  AC-1 -> result table, Installs column: one row per arm and host (A, B, C Claude and Codex; D control as one row for both hosts), each cell observed or marked (doc).
  AC-2 -> result table, "kc-adr update reaches dev2" column: observed on both hosts for C (Claude `update kc-adr` 2.3.0 to 2.4.0; Codex `marketplace upgrade` 2.2.0 to 2.3.0); A on Claude yes only by `update kc-adr`; B Claude no (copy stayed 2.0.0); n/a where install failed or nothing couples (A and B on Codex, D).
  AC-3 -> result table, "Absent kc-adr refuses loudly" column: C exit 3 with the printed install message on both hosts; A on Claude partly (dev2-native `failed to load`, no live model session); B bundled so never absent; n/a for A and B on Codex, and D.
  AC-4 -> result table, "Incompatible version caught" column (C exit 4 on both hosts, A on Claude at install and update) plus the `## Ruling` (run-time resolution) and `## What a move would change (the four adopters)` (three of four verified by `git grep`; carlove-v1 has no checkout and is marked unverified).

### Summary

The design check now exits 0 on the task file with FO's acceptance criteria in place. AC-1 to AC-4 each point at the existing report.md section that holds their evidence; report.md, the other task sections and every repository file are unchanged. Cells marked n/a in report.md (Codex native, Codex symlink, wrap control) are not observed failures of the criteria, they are arms with no mechanism on that host; AC-3's falsifier (exit 0 or silence) did not occur in any observed cell.
