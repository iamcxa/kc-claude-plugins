---
title: The local roborev Codex review catches the findings Codex's PR review later posted, once its severity threshold includes medium
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:roborev-threshold-catches-pr-findings-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:roborev-threshold-catches-pr-findings-poc-backlog-1
              briefing:
                id: briefing:roborev-threshold-catches-pr-findings-poc:backlog:attempt-1:revision-1
                digest: sha256:a1303f2d5f177088d9613b89b12077a78f7ba3dfd70efbb4243965a668e662d6
                room-ref: ./roborev-threshold-catches-pr-findings-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:roborev-threshold-catches-pr-findings-poc:backlog:1
                briefing: briefing:roborev-threshold-catches-pr-findings-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-22T04:33:18.976941Z"
                decision: approve
                reason: Captain 「做」 (chat, 2026-10-22), answering FO 「要先做這個 roborev 門檻 POC 嗎？我建議做。」, put after FO stated the three heads, the local-clean versus PR-findings gap and the threshold rerun; this briefing binds that answer after the fact.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-22T04:33:47Z
worktree: .worktrees/spacedock-ensign-roborev-threshold-catches-pr-findings-poc
---

## Scope

- Source: the Captain 「做」 (chat, 2026-10-22), answering FO's 「要先做這個 roborev 門檻 POC 嗎？我建議做。」, after FO reported that the roborev extension's local Codex review read clean on heads where Codex's PR review then posted findings. Consumer: the kc-dev-flow-2 roborev extension (`extensions/roborev/roborev_gate.py`, which runs `roborev review --since <base> --repo <repo> --wait` with no `--min-severity`).
- What exists: roborev jobs on those heads (dev2 task records): #694 head 1c57c156 job 992, #698 head 589c54e5 job 1005, both printing `SEVERITY_THRESHOLD_MET` and no finding; Codex PR reviews on the same heads posted one P2 (review 5608166400) and two P2 (review 5608491991); #693 round-1 head a3ce3c8b drew one P1 and one P2 (review 5603366440). `roborev review --help` lists `--min-severity critical|high|medium|low`; roborev's default agent here is codex (`roborev config list`, 2026-10-22). What `SEVERITY_THRESHOLD_MET` means and what the default threshold is are not yet read from roborev's own docs or source.
- The run: first read roborev's documentation or source for the default `--min-severity` and the meaning of `SEVERITY_THRESHOLD_MET`. Then, in throwaway worktrees at each of the three heads with the base each PR was reviewed against (its merge-base with main at review time), run `roborev review --since <base> --repo <worktree> --wait --agent codex` once with `--min-severity medium` and once with `--min-severity low`. Match each local finding against the PR review's findings on that head by file and problem.
- Bar: report, per head and threshold, which PR findings the local run caught, which it missed, extra local findings, and tokens and wall time; a threshold change is worth making only if it catches PR findings on at least two of the three heads; a run that catches none at any threshold means the cause is not the threshold.
- Budget: six runs (three heads, two thresholds), no rerun; stop there.
- Non-goals: changing roborev_gate.py or any roborev configuration; another agent than codex; posting anything on a PR.

## Acceptance criteria

**AC-1** The default threshold and the meaning of `SEVERITY_THRESHOLD_MET` are stated from roborev's own documentation or source. Evidence: a quoted passage with its file or URL. Falsifier: a statement with no roborev source.

**AC-2** Six runs on the named heads and bases with the pinned flags. Evidence: each run's command line, job id, agent `codex`, head and base SHAs, and the full finding list. Falsifier: a run on another head, base, agent or threshold.

## FO alignment

Alignment: not needed before implementation; the Captain approved the run (「做」, 2026-10-22) after FO stated its heads and comparison, restated above.
Release review: not needed: the task belongs to no release.
Surfaces: none
Visible change: none

## Stage Report: implementation

- DONE: Read roborev's own documentation or source for the default --min-severity of `roborev review` and the meaning of `SEVERITY_THRESHOLD_MET`; quote the passage with its file or URL (AC-1)
  Quoted in report.md from roborev v0.62.0 `internal/config/workflow.go` and `docs/guides/reviewing-code.md`: default is no filter; the marker means all findings are below the active threshold. The repo's `.roborev.toml` sets `review_min_severity = "high"` at all three heads, so the gate ran at high, not unfiltered.
- DONE: In throwaway worktrees outside every repository checkout, at heads 1c57c156 (#694), 589c54e5 (#698) and a3ce3c8b (#693 round 1) of iamcxa/kc-claude-plugins, each against the base the PR was reviewed on, run `roborev review --since <base> --repo <worktree> --wait --agent codex` with `--min-severity medium` and then `--min-severity low`; record each command, job id, agent, head, base, finding list, tokens and wall time (AC-2)
  Six runs, jobs 1014 to 1019, agent codex, one each, no rerun; commands, SHAs, finding lists, tokens and wall times are in report.md.
- DONE: Match each local finding against that head's Codex PR findings (read with `gh api repos/iamcxa/kc-claude-plugins/pulls/<N>/comments --paginate`, reviews 5608166400, 5608491991, 5603366440) by file and problem; write report.md in the task folder with the per-head, per-threshold caught / missed / extra table and the bar's reading; remove the worktrees
  report.md in `roborev-threshold-catches-pr-findings-poc/`: caught 1 of 5 PR findings, on 1 of 3 heads (#698 fragment finding, both thresholds); the bar of two heads is not met; #694 and #693 caught none at any threshold. Worktrees removed and pruned.

### Summary

Lowering the roborev threshold to medium or low catches a Codex PR finding on 1 of 3 heads, below the two-head bar; on the other two heads the cause is not the threshold. The task's premise was off: the gate's earlier reviews ran at `high` through the repo's `.roborev.toml`, not at roborev's no-filter default. Limits: one sample per cell, no rerun, one repo, and one local-extra finding on #694 not checked as a real defect.

No code or configuration changed, so `comment_ratio.py`, `doc_impact.py` and `number_guards.py` have no candidate to run on; no ADR added; no PR opened (no push grant). `boundary-crossed:` none. Cleanup done. Raw run output is in `/tmp/rr-runs`, outside any repository.
