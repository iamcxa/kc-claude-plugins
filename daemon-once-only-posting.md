---
title: Route daemon posting through the once-only path
status: ideation
source: slice 1 of 3 for daemon posting safety; unblocks once-only-daemon-preauth-gate. Found while closing PR3 (#56), 2026-07-25
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: w7exen9fcfgbpz6c8z3j1kt9
---

The daemon gets **none** of the once-only protection shipped in #56. `KC_PR_FLOW_ONCE_ONLY_POST` defaults off, so `kc-pr-review` Step 7 takes the legacy `gh pr review` path: no idempotency marker, no durable `post.intent`, no reconcile-before-retry, no confirm window. `kc-pr-daemon` references none of the runtime's env flags or scripts (verified: zero matches for `KC_PR_FLOW_REVIEW_TYPED`, `KC_PR_FLOW_ONCE_ONLY_POST`, `review-post.sh`, `review-runtime.sh` in the daemon skill and `reference/pr-review-loop.md`).

Its only duplicate defence is next-iteration observation: "The skill's review post serves as the dedup signal ... Future iterations detect it via the `submittedAt` timestamp check" (`reference/pr-review-loop.md`). #56 proved that class of check insufficient — an iteration whose POST lands but whose session dies before recording the outcome leaves no local trace, and a lagging `GET .../reviews` shows no review, so the next iteration reviews and posts again. Each daemon iteration is a fresh stateless session, which makes the interrupted-mid-POST case the normal case rather than an edge one.

Scope: let a daemon iteration take the once-only path, reusing the shipped and tested machinery rather than adding a second mechanism. That requires Step 7's request/gate JSON to exist in daemon mode, which forces the daemon's approval to be represented as an artifact instead of the prose instruction at `pr-review-loop.md` ("Approve posting the review"). Keep that artifact minimal here — typing and bounding it is slice 2 (`once-only-daemon-preauth-gate`).

Out of scope: any change to what the daemon is allowed to review or fix, and the freshness/coverage gates (slice 3).

## Acceptance criteria

**AC-1 — A daemon iteration that is interrupted after its POST lands does not produce a second review on the next iteration.**
Verified by: driving two consecutive iterations against the recorded stub transport with the first killed after the POST lands and before it records a result; the PR ends with exactly one review. Falsified by: two reviews, which is today's behaviour.

**AC-2 — Rollback still works for the daemon: with the once-only path disabled the daemon posts exactly as it does today.**
Verified by: the legacy path text and the resulting review body are byte-identical with the flag off. Falsified by: any daemon-visible behaviour change when the flag is off.

## Ideation

### Correction to this entity's own premise
Filed as "pure wiring, zero new design". That is wrong, and the investigation is what showed it. Entering the once-only path requires a gate receipt, and `review_post_gate_valid` (`review-post.sh:180-187`) hard-requires `.human_confirmed == true`, while `review_interactive_post_gate_valid` additionally pins the exact key set `["confirmation","effective_event","human_confirmed","schema"]`. **A daemon cannot honestly assert `human_confirmed: true`.** So this slice must introduce one minimal new artifact after all. Everything else is reuse.

### Where the authority actually lives (reverse-recovery)
- `review_interactive_confirm_post` / `review_interactive_post_gate_valid` are **not** in a script. They live in `kc-pr-review/SKILL.md` inside the `# typed-interactive-recipe:start/end` markers, and `review-shadow.test.sh:56` extracts that block and sources it. The prose *is* the tested implementation — deliberately one text for both paths. Any change here therefore lands in that block and is covered by the existing 155-assertion suite, not by a new mechanism.
- Step 7 already states the invariant this slice restores: "Never reconstruct posting authority from the selected option or prose." The daemon violates it today via `reference/pr-review-loop.md` ("Approve posting the review"). This is not a missing feature so much as an existing invariant that the autonomous path bypasses.
- Layer trace: daemon loop (`pr-review-daemon.sh`) → `claude -p` → `Skill(kc-pr-review)` → §6c gate → Step 7 → legacy `gh pr review`. The only MISSING piece is a gate artifact an autonomous caller may legitimately produce; everything from Step 7 onward (durable intent, marker, reconcile, confirm window, retention, rollback) already exists and is tested.

### Design: a sibling gate, not a relaxed one
Add `kc-pr-flow.autonomous-post-gate/v1` alongside the interactive gate rather than loosening the interactive one. `review-post.sh` accepts either; the interactive schema and its `human_confirmed` semantics stay byte-identical, so "a human confirmed this" never becomes a value a daemon can set. The autonomous gate carries only what slice 1 needs: schema, effective event, and the review identity (review key + head) it authorizes. Binding rigor, event ceiling enforcement, and expiry are slice 2 (`once-only-daemon-preauth-gate`); freshness and coverage are slice 3.

Rejected alternative: reuse the interactive gate with `human_confirmed: true` set by the daemon. It buys less code and costs the one invariant the whole increment exists to protect.

### Gate decisions needed from the captain
- **D1 — sibling autonomous gate schema (recommended) vs. relaxing the interactive gate.** Recommend sibling.
- **D2 — event ceiling for autonomous posts in this slice.** Capping at COMMENT is the smallest blast radius but is a **behaviour change**: daemon reviews that would post REQUEST_CHANGES (typed decision reporting blockers) would post COMMENT instead. Alternative is to preserve today's event selection in slice 1 and introduce the ceiling in slice 2. Recommend preserving today's event here, so this slice changes exactly one thing (duplicate protection) and the ceiling arrives with the typed preauthorization that can express it.
- **D3 — opt-in mechanism.** Reuse `KC_PR_FLOW_ONCE_ONLY_POST=on`, set by the daemon script for its iterations, so there is one rollback switch rather than two. Recommend reuse.

### Test plan (RED first)
1. RED for AC-1: two consecutive daemon-mode iterations against the recorded stub transport, the first killed after its POST lands and before it records a result. Today's legacy path yields two reviews; the once-only path must yield one. This is the same fault the `review-post.sh` suite already injects, reused rather than reinvented.
2. RED for AC-2: with the flag off, the daemon's posting text and resulting review body are byte-identical to today.
3. Negative: an autonomous gate presented for a different review key or head is refused; a malformed one is refused. (Full binding is slice 2, but refusal on obvious mismatch belongs with the schema that introduces it.)
4. Verify with CI's pinned ShellCheck v0.9.0 (docker), not the local build — see kc-pr-flow/CLAUDE.md.
