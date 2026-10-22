# roborev threshold vs Codex PR findings: POC report

Run date 2026-10-22. roborev v0.62.0, agent codex (model gpt-5.6-terra, reasoning medium, both from the repo's `.roborev.toml` at each head). Six runs, no rerun. Nothing changed in any repository or roborev configuration; nothing posted on any PR.

## Conclusion

Lowering the threshold to medium or low does not pass the recorded bar: the local run caught a PR finding on 1 of 3 heads (#698), not 2. The premise was also off: the gate's reviews were not unfiltered, they ran at threshold `high` because the repo's `.roborev.toml` sets `review_min_severity = "high"`.

## AC-1: default threshold and `SEVERITY_THRESHOLD_MET`

Source: roborev v0.62.0 (tag, commit 4be51372fd57e5fa1e0dd93eafd8e0253631d748), https://github.com/roborev-dev/roborev .

- Default is no filter. `internal/config/workflow.go`, `ResolveReviewMinSeverity`: "Priority: explicit > per-repo config > global config > "" (no filter)".
- The cascade is documented in `docs/guides/reviewing-code.md` § Severity Filtering: "The cascade order is: CLI flag > per-repo config > global config. The CLI flag overrides the config value."
- Marker meaning, `internal/config/workflow.go`, `SeverityThresholdMarker` and `SeverityInstruction`: the marker is "output by agents when all findings in a review are below the configured minimum severity"; the injected prompt text is "Severity filter: Only include Medium, High, and Critical findings. Ignore any findings below medium severity. If ALL findings in the review are below medium severity, output the exact text SEVERITY_THRESHOLD_MET and make no code changes." `SeverityInstruction` returns "" for `low`, so `low` injects no filter and the marker cannot appear at `low`.
- Consequence: `SEVERITY_THRESHOLD_MET` is the agent's own statement that nothing at or above the active threshold was found. It is not a "reviewed clean" verdict at every severity.
- What this repo's gate used: `kc-dev-flow-2/extensions/roborev/roborev_gate.py` passes no `--min-severity`, so the cascade falls to the repo file. `.roborev.toml` at all three heads (1c57c156, 589c54e5, a3ce3c8b) sets `review_min_severity = "high"`. Jobs 992 and 1005 therefore ran at `high`, and their `SEVERITY_THRESHOLD_MET` means "no High or Critical finding".

## AC-2: runs

Command shape (flags pinned; `--repo` is a throwaway detached worktree at the head under `/tmp`, removed afterwards): `roborev review --since <base> --repo <worktree> --wait --agent codex --min-severity <medium|low>`.
Bases (merge-base with origin/main at review time; for #694 and #698 it equals the base of the earlier jobs 992 and 1005, read from the roborev DB `git_ref`): #694 and #693 base c27e76590c1d2dc910e7fa2d332242a7534df0b0; #698 base 7244594bef4e1c9c42db0ed8ff42509ba6d48dd3.
Heads: #694 1c57c156d034fcd1a7a73efb9a70370a57c1f97f; #698 589c54e57fe969b6049bad737be8615e96b7b54e; #693 a3ce3c8b1747b8737fd01b275a4e1f3fb7a1d58d.
Note: job 1005 reviewed 3120bd18, not 589c54e5; the two trees are identical (`git diff 3120bd18 589c54e5` is empty).

| Job | PR | Threshold | Exit | Tokens in (cached) / out | Wall (client) | Result |
|---|---|---|---|---|---|---|
| 1014 | 694 | medium | 1 | 130.4k (97.3k) / 2.1k | 75 s | 1 Medium finding |
| 1019 | 694 | low | 1 | 148.7k (121.6k) / 1.3k | 60 s | 1 Medium finding |
| 1016 | 698 | medium | 1 | 90.8k (72.7k) / 2.4k | 95 s | 1 Medium finding |
| 1017 | 698 | low | 1 | 243.0k (205.8k) / 2.6k | 65 s | 1 Medium finding |
| 1015 | 693 | medium | 0 | 115.2k (84.0k) / 1.7k | 60 s | `SEVERITY_THRESHOLD_MET` |
| 1018 | 693 | low | 0 | 92.7k (62.7k) / 1.6k | 75 s | "No issues found." |

The three medium runs started together, then the three low runs; wall time includes queueing behind that parallelism. Full finding lists:

- Jobs 1014 / 1019 (#694): Medium, `kc-dev-flow-2/scripts/pr_watch.py:62` (1014) and `:320` (1019). Problem: ideation detection is an exact regex over the whole README, so `name: "ideation"` or a trailing comment is missed, while matching text outside frontmatter can falsely enable seed checks.
- Jobs 1016 / 1017 (#698): Medium, `scripts/adr-path-check.py:56` (1016) and `:49` (1017). Problem: an ADR link with a fragment such as `docs/adr/0001-example.md#decision` is treated as a nonexistent filename because the fragment stays in the checked path.
- Job 1015 (#693, medium): `SEVERITY_THRESHOLD_MET`. Job 1018 (#693, low): "No issues found."

## Match against Codex PR findings

Codex findings read with `gh api repos/iamcxa/kc-claude-plugins/pulls/<N>/comments --paginate` (reviews 5608166400, 5608491991, 5603366440; for #693 the comments' `original_commit_id` is a3ce3c8b).

| Head | Codex PR finding | medium | low |
|---|---|---|---|
| #694 1c57c156 | P2 `pr_watch.py` `FO_HEADING` search counts a fenced `## FO alignment` example as a real section | missed | missed |
| #698 589c54e5 | P2 `adr-path-check.py` lookbehind skips `./docs/adr/..` and `/docs/adr/..` paths | missed | missed |
| #698 589c54e5 | P2 `adr-path-check.py` fragment `#rationale` kept in the tracked-path lookup | caught (1016, same problem, line 56 vs 49) | caught (1017) |
| #693 a3ce3c8b | P1 `codex_review.py` newer unread comment not treated as the latest result | missed | missed |
| #693 a3ce3c8b | P2 `pr_watch.py` stale snapshot counted as a successful reread | missed | missed |

Extra local findings (not in the PR review): #694 the `IDEATION_STAGE` regex finding at both thresholds (different problem and line from Codex's `FO_HEADING` finding; I did not check whether it is a real defect). None on #698 or #693.

Per head and threshold: #694 caught 0/1, extra 1 (both thresholds); #698 caught 1/2, extra 0 (both); #693 caught 0/2, extra 0 (both).

## Bar's reading

- Bar "catches PR findings on at least two of the three heads": met on 1 head (#698) at both thresholds. Not met. A threshold change alone is not worth making on this evidence.
- Bar "a run that catches none at any threshold means the cause is not the threshold": #694 and #693 caught none at medium or low, so for those two heads the cause is not the threshold. For #693 even the P1 was missed at `low`.
- #698 is the one head where the threshold mattered: job 1005 at `high` printed the marker, while the same tree at medium or low surfaced the fragment finding. Codex's other #698 finding (`./` prefix) was missed at every threshold.
- Codex PR severity (P1/P2) and roborev severity (Critical to Low) are different scales; every local finding here came out Medium.

## What this does not prove

One sample per cell, no rerun (budget): a miss may be run-to-run variation, and a 6-run result cannot separate that from a real gap. Different model and context than Codex's cloud PR review (local gpt-5.6-terra at reasoning medium, diff since base, versus the PR reviewer), so the missed #693 and #694 findings may reflect that difference, not the threshold. Three heads from one repo and one week. The "extra" finding on #694 is not verified as real.

## Cleanup

The three detached worktrees under `/tmp/rr-wt` were removed with `git worktree remove` and `git worktree prune`; the roborev source clone under `/tmp` was deleted. roborev DB keeps jobs 1014 to 1019. Raw run output (command lines, stdout/stderr, timings) is in `/tmp/rr-runs`, outside any repository.
