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

## PARKED 2026-07-26 — the premise this entity rests on is wrong

Returned to backlog the same day it entered ideation. The captain's call, in his words:
unattended operation "真的是我日常需求之一" — it is one of his daily needs, so removing
the unattended caller is not a simplification, it is a feature deletion. The layer trace
below only established that the inversion is *buildable*; it never argued it was *right*,
and that is the question it fails.

What this entity got right and should be salvaged by whatever replaces it: the dilemma is
real. An unattended loop either lets a machine decide, or it stops. Both directions the
captain named are attempts to find a third answer — keep the loop unattended, but let a
human be present at the decision points without having to sit there.

**Directions to explore (captain, not yet designed):**

1. **Replace `claude -p` with `spacedock claude`.** The daemon's iterations become
   workflow-tracked instead of anonymous. Worth noting because spacedock already owns an
   approval-gate concept, and an approval gate is precisely the §6c authority the daemon
   cannot honestly produce for itself.
2. **A small purpose-built harness on spacedock + ACP**, for enough bidirectional
   communication that an unattended iteration can *ask* at a decision point and wait for an
   answer, rather than self-approving or aborting. This is the direction that actually
   dissolves the dilemma rather than choosing a side: unattended throughput for everything
   that needs no decision, a real human at everything that does.

Neither is designed. Do not treat this section as a plan.

**Consequence for `vf` and `x0`:** their premise survived. Unattended posting is wanted, so
a bounded autonomous authorization is still needed. See their own files for the narrower
coupling that remains.

---

## Original proposal (superseded, kept for the trace)

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

## Reverse-recovery layer trace (done 2026-07-26 against origin/main, still valid)

Six of seven layers already exist; the proposal was mostly deletion. Recorded because any
replacement direction inherits the same map.

| Layer | State | Classification |
|---|---|---|
| arm / re-arm the wait | Claude Code's `Monitor` (persistent; its own docs give GitHub PR polling as the example) | WORKING — and not ours |
| wait / poll for an actionable PR | `pr-review-daemon.sh:145-190` — open non-draft PRs whose `ci-gate` status passed | logic WORKING, **EXISTS_BROKEN as a reusable unit**: inline in `while true`, exits via `continue`+`sleep`, no exit-code or stdout contract |
| wake / notify the human | `notify()` `:81-108` plus signal detection `:221-228` | WORKING, but triggered by grepping the model's output text, which disappears with `claude -p` |
| review | `kc-pr-review` | WORKING, already interactive-first |
| §6c confirmation | `skills/kc-pr-review/SKILL.md:1723+` | WORKING — the layer the proposal existed to restore |
| post | `review-post.sh` interactive branch | WORKING; the autonomous branch `:221-243` would become unreachable |
| usage accounting | `:203-235`, parsing `claude -p --output-format json` | **dies with the proposal** |

Proof of absence for a reusable blocking wait: three strategies (wait/block naming,
`while true` + `gh pr list`, background-task/Monitor usage across all plugins). The only
match is `pr-review-daemon.sh` itself; every other hit is a `.worktrees/` copy of that same
file. Nothing to recover — extraction would be new work.

**Two findings that outlive the proposal.** First, the harness already owns arm/re-arm, so
the portable deliverable was never a skill but a script with an exit/stdout contract that
codex / agy / any harness can wire itself — that stays true for direction 1 and 2 above.
Second, `/kc-pr-daemon status`'s cost telemetry (all-time and month-to-date spend,
iterations, turns) is derived entirely from the per-iteration `claude -p` JSON envelope.
Any direction that stops invoking `claude -p` that way loses that number, and the loss was
unnamed until this trace. Direction 1 (`spacedock claude`) has the same exposure.
