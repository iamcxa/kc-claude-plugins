---
title: The local roborev Codex review catches the findings Codex's PR review later posted, once its severity threshold includes medium
variant: kc-dev-flow-2
profile: poc
merge: pr
status: backlog
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
                state: pending
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
