---
title: Invert the PR daemon into an attended blocking wait
status: backlog
source: captain proposal 2026-07-26, during the vf once-only-daemon-preauth-gate backlog gate — supersedes the reason vf and x0 exist
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 4p6g3w9tak3zbsn8rh8gr7cq
---

`pr-review-daemon.sh` runs an unattended `while true` loop that invokes `claude -p`
with `reference/pr-review-loop.md` as its prompt (`:190`), so a model reviews and
posts with no human at the `kc-pr-review` §6c confirmation gate. That single fact is
the entire reason the daemon posting-safety arc exists: slice 1 (`daemon-once-only-posting`,
merged #59) had to invent `kc-pr-flow.autonomous-post-gate/v1` because a daemon cannot
honestly assert `human_confirmed: true`, and slices 2 (`vf`) and 3 (`x0`) exist to give
that autonomous authorization an event ceiling, an expiry, a fresh-head recheck, and a
coverage refusal.

The captain's proposal removes the caller instead of bounding it. The daemon stops
invoking `claude -p`. What survives is its bash pre-flight gate (`:145-190` — open
non-draft PRs whose `ci-gate` status passed), extracted as a standalone blocking wait
that exits when a PR becomes actionable and costs zero model tokens while idle. An
attended session arms that wait in the background, is woken by the harness when it
exits, runs `kc-pr-review` with the captain present at §6c, takes his direction, and
re-arms. Authorization is then the ordinary interactive receipt, honestly earned.

Two secondary claims to test rather than assume: that this saves tokens (idle
iterations are already free — the pre-flight gate already skips `claude -p`; the real
savings are not re-feeding the loop prompt every iteration, and not spending a full
review on a PR the captain would have redirected), and that a harness-agnostic exit
contract lets codex / agy / other harnesses reuse the same wait.

Consequences to weigh at the gate, not after: unattended throughput drops to zero by
design; a long-lived attended session's context grows where a fresh `claude -p` had a
fixed per-iteration cost; and #59's autonomous gate becomes dead code that should be
removed rather than left dormant documenting a guarantee nobody exercises. The
acceptance condition is that the captain accepts being present for every post — if a
"review these five without asking me" mode is ever wanted, preauthorization returns,
and `vf` / `x0` are deferred rather than dropped.

Blocks: `vf` (once-only-daemon-preauth-gate) and `x0` (daemon-preauth-freshness-coverage)
stay in backlog pending this decision. Once-only posting itself (#56) is unaffected and
stays valuable — an attended session can also die mid-POST.
