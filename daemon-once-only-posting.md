---
title: Route daemon posting through the once-only path
status: validation
source: slice 1 of 3 for daemon posting safety; unblocks once-only-daemon-preauth-gate. Found while closing PR3 (#56), 2026-07-25
started:
completed:
verdict:
worktree: .worktrees/w7-daemon-once-only
issue:
pr: https://github.com/iamcxa/kc-claude-plugins/pull/59
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

## Stage Report: implementation

- DONE: AC-1 — an interrupted daemon iteration does not produce a second review.
  `review-post.test.sh` drives an autonomous-gated post whose POST lands and whose session records no result, then a second iteration: `posted_reconciled`, store count stays 1. The same fault injection #56 already proved, now reachable by an autonomous caller.
- DONE: AC-2 — rollback still governs the autonomous path.
  With `KC_PR_FLOW_ONCE_ONLY_POST` unset, a *valid* autonomous gate is refused (exit 3) and writes no review, so the flag stays the operator's kill switch rather than something a gate can re-enable.
- DONE: Authorization is typed, not prose. `reference/pr-review-loop.md` no longer says "Approve posting the review"; it enables the once-only path and builds `review_autonomous_post_gate`, added as absolute safety rule 11. Step 7 documents both authorizations side by side.
- DONE: `human_confirmed` stays unforgeable. The autonomous gate omits the field entirely (not `false`), and its closed key set refuses one smuggled in — tested from both the recipe side and through `review-post.sh`.
- DONE: The gate authorizes one review, not any review. `review_post_gate_valid` compares `review_key` + `head_sha` against the request; gates bound elsewhere, claiming a non-daemon authorizer, or carrying an extra field are all refused, and none of them posts anything.
- DONE: Docs state what exists and what does not. CLAUDE.md / README / reference / docs each record the bound gate **and** the still-missing event ceiling, expiry, fresh head recheck, and coverage refusal, so this is not readable as finished preauthorization.
- DONE: Verification. 902 passed / 0 failed across all 7 suites. ShellCheck **v0.9.0 — CI's pinned version — clean on all eight files the workflow checks** (run from the release tarball natively; the Docker daemon was down, and the fallback is now documented). CI doc-safety greps all match; the shadow suite still sees exactly one interactive-post-gate reference in Step 7; skill frontmatter lint passes.
- DONE: Corrected this entity's own premise during ideation — it could not be pure wiring, because the gate hard-requires `human_confirmed == true`. That correction is recorded in the Ideation section rather than quietly absorbed.

### Found and fixed beyond the slice
The `typed-interactive-seam` test group ran only when named explicitly (`--case typed-interactive-seam`). `CASE_FILTER` defaults to `all` and comes from a positional argument, and CI invokes the script with none — so **56 assertions never executed in CI**, covering interactive confirmation validity, post-gate authority, forged-confirmation rejection, and the Step 7 receipt requirement. `all` now includes the group. All 56 pass unchanged, so nothing was masked; the exposure was that a future regression in posting authority would have gone unseen. Without this, the slice's own new assertions would have been decoration too.

### Not done, by scope
No event ceiling and no expiry on the autonomous gate (slice 2, `once-only-daemon-preauth-gate`); no fresh head recheck or coverage refusal immediately before an autonomous post (slice 3, `daemon-preauth-freshness-coverage`). The concurrency residual named in #56 is unchanged and still tracked there.

### Summary
The daemon now posts under an authorization that says who granted it and which review it covers, instead of instructing a model to approve the human gate on the user's behalf — and it inherits #56's once-only machinery, so an interrupted iteration reconciles rather than reposting. Four commits: the gate schema plus the revived test group, the bound acceptance in `review-post.sh`, the daemon wiring and doc sync, and the Docker-free lint fallback.

## Stage Report: validation

Verdict: **PASS, with one decision for the captain.** Coordinator-driven: two fresh-context reviewers on distinct lenses, my own adversarial probing of the real CLI path, a claim-breaking spot-check, a cross-model round, and citation verification. Six defects were found and fixed during the round; none survives.

### Per-AC results
- **AC-1 — an interrupted iteration does not produce a second review.** PASS. `review-post.test.sh` drives an autonomous-gated post whose POST lands with no recorded result, then a second iteration: `posted_reconciled`, store count 1. Proven to bite: deleting the binding comparison in a scratch copy turned three assertions red (`expected [3], got [0]` twice, `expected [0], got [1]`), so the tests guard the invariant rather than decorate it.
- **AC-2 — rollback still governs.** PASS. With the flag unset, a *valid* autonomous gate is refused (rc 3, zero reviews) — verified both by suite assertion and by hand against the real CLI.

### Adversarial probing (mine, through the real CLI, not the function in isolation)
Eight refusals with zero reviews written: null binding fields, missing binding fields, non-JSON, empty input, a JSON array, a smuggled `human_confirmed`, schema confusion (autonomous payload under the interactive schema name), and a wrong head. A positive control (correctly bound gate → posted) proves these are real discriminations, not blanket refusal.

### Defects found and fixed this round
1. **P1 — a forgeable interactive gate.** `review_post_gate_valid`'s interactive branch checked three predicates, so any process could hand-write `{schema, human_confirmed: true, effective_event}` and obtain unbound posting authority. The strict validator lives in SKILL.md, which runs only if the calling agent chooses to run it. Pre-existing code — but **this entity newly asserted it as a security property**, so the documentation was claiming a guarantee only prose enforced. Fixed at the enforcement point (closed key set + a confirmation object of the right schema agreeing on the event) rather than by softening the claim.
2. **P2 — the binding was sound only by accident.** An unresolved (empty) head would have been matched by an equally empty gate field, with the later live-head check as the only thing preventing consequences. The branch now asserts the 40/64-hex shapes itself.
3. **nit — `review_autonomous_post_gate` aborted** on an unbound variable under `set -u` when called with fewer than four arguments, contradicting its own comment. Arguments defaulted.
4. **Coverage gap I found by checking my own intent**, not from any review: the outer key set is closed while the confirmation's is deliberately open (a real typed confirmation carries a decision and blocker evidence). Nothing pinned that, so a future tightening of the inner object would have silently rejected the typed path. Now covered.
5. **Single-document input.** Unslurped, `jq -e` takes its status from the last document of a stream. I could not construct an exploit — any accepted stream still had to contain a genuinely valid, correctly bound gate — but "safe if you follow this argument" is a poor property at an authorization boundary. Both stages now slurp and require `length == 1`.
6. **Verdict, not crash.** String type-guards now precede the hex tests; a non-string binding was already refused, but via a jq runtime error rather than a decision.

### Reviewer disagreement, adjudicated against code
The two reviewers split on defect 1. `silent-failure-hunter` called it P1; `code-reviewer` reported no P1, reasoning that the interactive path's validation happens upstream in SKILL.md. I sided with the former: that upstream is **prose**, executed only if an agent complies, while `review-post.sh` is by its own header the sole holder of posting authority. Worth recording that **all three of us — both reviewers and me — first tested only smuggling `human_confirmed` into the *autonomous* schema** (correctly refused). The hole was in the path everyone assumed legitimate.

The cross-model round mislabelled the unguarded `$3`/`$4` as a CRITICAL BUG; it is latent, since the sole caller passes four arguments. Fixed for consistency, severity corrected here. Its genuinely new contribution was the jq stream semantics in defect 5.

### Citations verified
Every load-bearing `file:line` from both reviewers was checked against the file: the three-predicate interactive branch, zero `.confirmation` references pre-fix, the unguarded positional parameters, and CI invoking `review-shadow.test.sh` with no arguments (workflow line 192). **Zero fabricated citations**, so no reviewer round was discarded.

### A red test that was wrong
My own "empty head binding is refused" assertion failed, and the cause was the test, not the code: `write_auto_gate`'s `${2:-$HEAD}` substitutes a real head for an empty one, so the test had been sending a perfectly valid gate. Rebuilt with jq directly. Recording it because acting on that red signal would have meant breaking correct code to satisfy a broken test.

### Evidence
review-post **122 passed / 0 failed** (106 before this round), shadow **213 / 0**, full suite green. ShellCheck **v0.9.0 — CI's pinned version — clean**, run from the release tarball natively since the Docker daemon was down. **CI green on every pushed commit**, including the final `0d3eaac`; the CI log confirms `Run shadow parity tests: 211 passed` at `3cf6a2a`, so the 56 previously-dead assertions genuinely execute on Linux.

### Correction-round budget
One round. Estimate: bounded fixes to a slice already implemented. Actual: two fix commits plus a cross-model pass. Disposition: 6 found, **6 fixed, 0 declined, 0 fabricated**. Within tolerance; no design reset.

### Named residual for the captain
`review_post_cmd_post`'s pre-POST reconcile **fails open** when the reviews list read is unusable, where `resume` fails closed for the identical condition. Pre-existing from #56 — not introduced here — and it requires two coincident conditions: local durable state unavailable (wiped or reconfigured state dir) **and** an unusable remote list at that moment. The local cross-run check independently blocks the common crash-then-retry case. Making it symmetric would refuse even a genuinely first post while the reviews API is degraded, and would change availability for **every** caller, not just the daemon. Recommendation: carry it into slice 2 (`once-only-daemon-preauth-gate`), which is already building the preauthorization contract and is the right place to decide degraded-mode behaviour. Captain's call.
