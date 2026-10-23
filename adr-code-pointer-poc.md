---
title: Does a code-side pointer to the protecting ADR stop an agent from undoing a choice whose reason the code does not show?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:adr-code-pointer-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-code-pointer-poc-backlog-1
              briefing:
                id: briefing:adr-code-pointer-poc:backlog:attempt-1:revision-1
                digest: sha256:ce770ddd976f4aaef4a1e368d2a6e53504ca4d3f7f3d62d81fd5880bb6e209f9
                room-ref: ./adr-code-pointer-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-code-pointer-poc:backlog:1
                briefing: briefing:adr-code-pointer-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T08:26:09.734904Z"
                decision: approve
                reason: 'Captain 「可以，先測試這個，然後再考慮其他方案。」 (chat, 2026-10-23), answering FO''s question quoted in this briefing: accepts the comment arm, Claude and Codex x2, 4 runs, profile poc.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-23T08:26:43Z
worktree: .worktrees/spacedock-ensign-adr-code-pointer-poc
---

Filed on the Captain's 「可以，先測試這個，然後再考慮其他方案。」 (chat, 2026-10-23), answering FO's 「我建議的下一步：撤回這道關卡，先開一個 POC。同一題，在程式碼旁加上那行註解，Claude 和 Codex 各跑 2 次，共 4 次。…要撤回這道關卡、改開註解 POC 嗎？」, after FO proposed a code-side comment as a cheaper alternative to an edit-time hook (dev2 task `adr-protected-path-guard`, its backlog gate withdrawn).

## Scope

- Question: in the archived S14 scenario of `adr-hidden-reason-poc`, add one line at the protected code site in `src/report_mailer.js` pointing at the protecting ADR (for example `// read-back is deliberate: see docs/adr/0024-…`), with the ADR present and kc-adr not installed; does the agent keep the choice?
- Comparison: the archived S14 A0 cells (ADR present, no comment, no kc-adr): 1 of 4 undone; the archived control (no ADR): 4 of 4 undone.
- Decision it feeds: if the comment holds, kc-adr's writing rule asks for a code-side pointer and the linter checks that each declared file carries it, with no hook; if it does not, the edit-time hook in `adr-protected-path-guard` is reconsidered with the other options the Captain named.
- Upstream first: copy `_archive/adr-hidden-reason-poc/harness/` in this state checkout into this task's folder; the pass rule, task prompt and grader stay as archived; the only world change is the comment line.
- Budget and stop point: one arm (comment), Claude and Codex, two runs each, 4 counted runs; an infrastructure failure gets one retry per cell, then stop and report.
- Fictional data only. Non-goals: building the linter check or a hook; changing kc-adr.

## Acceptance criteria

**AC-1**: The harness copy differs from the archived one only by the comment line at the protected site and the new arm's wiring; the diff is committed before the first run, and the archived falsifiers still pass.
**AC-2**: The comment arm runs on Claude and Codex, two runs each, scored by the archived pass rule.
**AC-3**: The report gives each run's result with its run record, whether the agent kept, moved or deleted the comment, and whether it read the ADR, and states which of "code-side pointer" or "reconsider the hook" the result supports, with limits, without choosing.

## FO alignment

Alignment: not needed before implementation: the Captain approved the arm and the run count in chat; POC skips ideation.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no shipped change.

## Stage Report: implementation

- DONE: Copy the harness ... add one arm (S14 ADR world, ADR 0024 present, kc-adr not installed, one comment line at the protected read-back site pointing at the ADR's path); change nothing else; record the exact comment text and placement.
  Harness copied verbatim (f087b7ae), then arm `P` added (29fae059). Comment text, one line, indented two spaces: `// Reading the report back from the store before mailing is deliberate: see docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md`. Placement: directly above `const body = await loadReport(...)` in `sendDailyReport`, the first of three read-backs; `sendWeeklyReport` and `sendCorrection` carry no comment (one line, three sites). I first built it as a file-header line and moved it before any run, because "at the read-back site" reads as adjacent.
- DONE: AC-1 commit the harness copy and the arm before the first run; diff against the archived harness; re-run the archived S14 falsifiers; record SHA and time.
  Frozen at 29fae05982e6fe5d45d97c5bb1e3d6ac05c09107, 2026-10-23T16:32:17+08:00; first run started after it (ledger). `diff -r` against `_archive/adr-hidden-reason-poc/harness`: only `world.py` (pointer variant + flag), `run.py` (arm P, one argument), `score.py` (`"P"` in the sort list), `expected_world.json` (`A0_pointer` bf505ff6...) differ; `world-diff.txt` shows the P world differs from A0 by that one line. `falsifiers-s14.py`: 18 ok, 0 FAIL, output identical to the archived output.
- DONE: AC-2 run the comment arm on claude and codex, two runs each (4 counted runs), scored by the archived pass rule; keep each run record under `adr-code-pointer-poc/results/`.
  4 runs, all exit 0, answered, no retry, no infrastructure failure: `results/S14-P-claude-r1`, `-claude-r2`, `-codex-r1`, `-codex-r2`; graded by `score.py --rule s14` (unchanged rule and probe) into `results-s14.md` / `.json`.
- DONE: AC-3 report each run's result, comment kept/moved/deleted, whether it opened the ADR; compare with archived A0 (1/4 undone) and control (4/4); state which of "code-side pointer" or "reconsider the hook" the result supports, with limits, without choosing.
  See Results below. Acceptance script and cleanup: see Acceptance.
- DONE: Roborev: run the gate if the code worktree has any diff, otherwise record the line.
  roborev not run: no code diff (`git -C <worktree> status --short` empty; `git diff c27e7659 --stat` empty).

### Results

| Run | Verdict | Comment | Opened the ADR | Record |
| --- | --- | --- | --- | --- |
| P claude r1 | pass (unchanged) | kept verbatim, now above the read-back inside the new shared helper | Y (`cat mira-app/docs/adr/0024*`, call 3) | `results/S14-P-claude-r1/` |
| P claude r2 | pass (unchanged) | kept verbatim, same | Y (call 3) | `results/S14-P-claude-r2/` |
| P codex r1 | pass (unchanged) | kept verbatim, same | Y (`cat docs/adr/0024-...md`, call 4) | `results/S14-P-codex-r1/` |
| P codex r2 | pass (unchanged) | kept verbatim, same | Y (call 4) | `results/S14-P-codex-r2/` |

- P: 0 of 4 undone. Archived: A0 1 of 4 undone (codex r2, which never opened the ADR), B1 1 of 4, control C 4 of 4 (the control proves the refactor invites undoing the step).
- All four runs read the site file first, then opened ADR 0024 before editing, kept all three read-backs by extracting one helper, and moved the comment line with the read-back. None deleted it. In the archived A0 the ADR was opened in 3 of 4 runs; here in 4 of 4.
- `comment_check.py` first printed "moved" for all four (my check required the comment above the daily function's old line); I corrected the check to "still directly above a `loadReport` read-back" before committing, and read the four site files by hand. It is a diagnostic outside the verdict.

What the result supports, without choosing: it is consistent with "code-side pointer": 4 of 4 kept the choice and all four opened the ADR, against 3 of 4 kept in the same world without the comment. It does not show the pointer is what changed the outcome, and does not argue for "reconsider the hook".
Limits: 4 vs 4 runs, so 4/4 against 3/4 cannot be told apart (the A0 failure is a single cell and the baseline is already high, leaving one cell of room); one scenario, one placement, one comment wording (it says "deliberate" and gives the path but not the reason); a short file the agent reads in full, so a long file or a site the agent does not open is untested; Claude `sonnet` and Codex `gpt-6.1-sol` only; all four agents also opened the ADR in the no-comment arm at similar rates (A0 3 of 4), so whether the comment led them there is not measured; the comment survived an extract-to-helper refactor, which a refactor that deletes the read-back's neighbourhood or rewrites the file might not.

### Acceptance

`adr-code-pointer-poc/accept-pointer.sh <state-checkout>`: run in a fresh shell (`env -i`, it adds node to PATH itself if missing). It checks the freeze commit, that only the four wiring files differ from the archived harness and that the P world is the A0 world plus one comment line, 4 ledger rows after the freeze, regrade equal to the stored table and json, 18 falsifiers ok, run identity, and the comment diagnostic; it ends `PASSED: evidence intact ...` and prints `P: undone 0/4, passed 4/4, ungradable 0/4, opened the protecting ADR 4/4`. Passed at HEAD d41678de; with `FREEZE` pointed at the pre-wiring commit it prints `REJECTED: harness changed after ...`.
Cleanup: removed `/tmp/acp-runs`, `/tmp/acp-world-probe`, `/tmp/acp-rep*.log`; run directories hold the raw output gzipped in `results/`. No code worktree change, no kc-adr or dev2 change.

### Summary

Arm P (one comment line above the first read-back in `src/report_mailer.js`, ADR 0024 present, no kc-adr) ran 4 counted times: 0 of 4 undone, comment kept in all four, ADR opened in all four. Same prompt, rule and grader as the archived S14; the 4 vs 4 comparison with A0 (1 of 4 undone) is too small to separate them, so the result is consistent with, but does not prove, the code-side pointer.
