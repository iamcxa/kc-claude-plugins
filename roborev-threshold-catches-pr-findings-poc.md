---
title: The local roborev Codex review catches the findings Codex's PR review later posted, once its severity threshold includes medium
variant: kc-dev-flow-2
profile: poc
merge: pr
status: validation
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
        - id: gate:roborev-threshold-catches-pr-findings-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:roborev-threshold-catches-pr-findings-poc-validation-1
              briefing:
                id: briefing:roborev-threshold-catches-pr-findings-poc:validation:attempt-1:revision-1
                digest: sha256:f443497b5f87b1ecb6c8bead8ac93858fb7a14a8a08a2c1a7df46c23140e25ad
                room-ref: ./roborev-threshold-catches-pr-findings-poc/review/validation/briefing-1
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

## Stage Report: validation

- DONE: Independent verdict on the POC result in report.md against AC-1 and AC-2 and the Scope's bar, read from saved jobs without rerunning any review (`roborev show --job` for 992, 1005, 1014 to 1019; roborev DB `review_jobs` read-only for agent, `git_ref` range, `min_severity`, `command_line`, injected prompt text)
  Tokens, finding text, agent `codex`, model gpt-5.6-terra, range base..head and threshold (`min_severity` medium/low on 1014 to 1019) all match report.md; jobs 992 and 1005 have empty `min_severity` and a prompt line "Severity filter: Only include High and Critical findings", jobs 1017 and 1018 (low) carry no filter line.
- DONE: Match each caught / missed / extra cell against the Codex PR findings (`gh api repos/iamcxa/kc-claude-plugins/pulls/<N>/comments --paginate`, reviews 5608166400, 5608491991, 5603366440)
  Five Codex findings confirmed with `original_commit_id` equal to the three heads: #693 P1 `codex_review.py`, P2 `pr_watch.py`; #694 P2 `pr_watch.py` fenced `## FO alignment`; #698 P2 `./`/`/` lookbehind, P2 `#rationale` fragment. Only the fragment finding matches a local finding (1016, 1017, same problem; line 56 vs 49); the report's 1 of 5 caught, 1 of 3 heads stands.
- DONE: Check AC-1 yourself: `.roborev.toml` `review_min_severity` at the three heads, and roborev's own source or docs for the default threshold and the meaning of `SEVERITY_THRESHOLD_MET` (quote file and version)
  `git show <head>:.roborev.toml` at 1c57c156, 589c54e5, 3120bd18 (job 1005's reviewed head), a3ce3c8b: `review_min_severity = "high"`; `roborev_gate.py` at 1c57c156 passes no `--min-severity`. Fetched roborev v0.62.0 (`roborev version` matches) `internal/config/workflow.go`: `ResolveReviewMinSeverity` "Priority: explicit > per-repo config > global config > "" (no filter)"; `SeverityThresholdMarker` "is output by agents when all findings in a review are below the configured minimum severity"; `SeverityInstruction` "Returns "" for empty, "low", or unrecognized input (no filtering needed)"; `docs/guides/reviewing-code.md` § Severity Filtering "The cascade order is: CLI flag > per-repo config > global config." The recorded high threshold for 992 and 1005 is also in their stored prompts. AC-1 holds.
- DONE: State the verdict (PASSED or REJECTED) naming the bar's reading, and findings classified by the workflow's Review-finding disposition
  Verdict PASSED. AC-1 and AC-2 are met as written. Bar's reading: "catches PR findings on at least two of the three heads" is not met (1 head, #698, at medium and low), so a threshold change is not supported by this evidence; for #694 and #693, which caught none at any threshold, the cause is not the threshold. This verdict is on the POC's evidence, not on whether to change the threshold.
- DONE: Run the stage's package scripts at the unchanged candidate (worktree HEAD c27e7659, no diff from base c27e7659)
  `adr_lint.py docs/adr --since c27e7659` exit 0 (28 files); `comment_ratio.py` exit 0 (0 code lines, 0 comment lines); `doc_impact.py` exit 0 (0 documents); `number_guards.py check` exit 0 (PASS, no migrations-path); `design_surfaces.py check` exit 0; `dispatch_records.py` exit 1 (F1).

### Findings

- F1 Polish: `dispatch_records.py` exits 1: `dispatch/implementation-1.md` lacks the roborev worker instruction or a line `roborev not run: <reason>`. The task changed no code, so roborev had no candidate to review; the record needs one line from FO, not a repair.
- F2 Deferred risk: the one local extra finding (#694, `IDEATION_STAGE` regex at `kc-dev-flow-2/scripts/pr_watch.py`, exact match, so `name: "ideation"` is missed) is not checked as a real defect; the regex line reads as the finding describes. It becomes Material if a supported workflow quotes or comments the stage name.
- F3 Polish: PR #698's current base is e66c9b32 (main moved); the reviewed base 7244594b equals job 1005's `git_ref` base and is an ancestor of the head, so the runs are on the stated bases.
- F4 Deferred risk: the gate ran at `high` and printed `SEVERITY_THRESHOLD_MET` on #698 while the same tree at medium surfaced a finding Codex's PR review also posted; one head, one sample per cell. It becomes Material if a second head repeats it. Whether to change `.roborev.toml` is a Captain call, not this task's.

### Minimal acceptance script

No user-visible surface; the smallest observable commands read the saved jobs (roborev v0.62.0, local daemon database, no review is rerun):

1. `roborev show --job 1015` -> prints `SEVERITY_THRESHOLD_MET` (#693, medium).
2. `roborev show --job 1016` -> prints one Medium finding about an ADR link with a fragment in `scripts/adr-path-check.py`.
3. `roborev show --job 1005` -> prints only `SEVERITY_THRESHOLD_MET` (same #698 tree at `high`).
4. `sqlite3 -readonly ~/.roborev/reviews.db "select id, min_severity, git_ref from review_jobs where id in (1005,1016,1017)"` -> 1005 empty, 1016 `medium`, 1017 `low`, 1005 and 1016 end in `..3120bd18...` / `..589c54e5...` respectively.
5. `git show 589c54e57fe969b6049bad737be8615e96b7b54e:.roborev.toml` in a kc-claude-plugins clone -> contains `review_min_severity = "high"`.

Does not cover: whether the missed #693 and #694 findings would be caught on a rerun, other agents, other repos, or whether the extra #694 finding is real.

### Summary

PASSED: the POC's evidence matches the saved jobs, the roborev v0.62.0 source and the Codex PR comments; AC-1 and AC-2 hold, and the bar of two heads is not met (1 of 3), so this run does not support a threshold change. No product bytes or roborev configuration were changed by this stage; the only open item for FO is the one-line roborev note in the implementation dispatch record (F1). `boundary-crossed:` none.
