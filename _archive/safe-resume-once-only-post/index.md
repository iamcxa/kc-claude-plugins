---
title: "Safe resume and once-only post"
source: superseded ship-flow pitch 2.3-safe-resume-once-only-post (agent-native PR review kit PR3); builds on ship-flow 2.1 (PR #48) + 2.2 (PR #50)
id: 50n4g9vyzdd12h03r6wskfkq
status: done
started: 2026-07-24T10:20:35Z
worktree: .worktrees/spacedock-ensign-safe-resume-once-only-post
pr: pr-merge:56
completed: 2026-07-25T04:35:14Z
verdict: passed
---

Appetite: 2 working days.

### Vertical Slice

An interrupted exact-head review resumes and posts an approved payload at most once.

### Boundary

Replay only compatible state, retry only incomplete work, persist an exact pending payload under restrictive permissions, and reconcile a durable marker or remote receipt before retrying an ambiguous GitHub mutation.

### Done Signal

Head or payload changes invalidate authorization; successful or stale payloads are removed; failed pending payloads expire after a bounded retention window. Daemon integration is default-deny and requires explicit preauthorization plus typed state, current head, coverage, and idempotency gates.

### Rollback

The legacy path remains available while the new posting path is disabled; rollback never deletes evidence needed to reconcile an uncertain remote result.

## Ideation

### Scope authorship

Problem and boundary are captain-authored, not agent-inferred: the four sections above
(Vertical Slice / Boundary / Done Signal / Rollback) are copied verbatim from the sharp
ship-flow pitch `2.3-safe-resume-once-only-post` (`docs/ship-flow/2.3-safe-resume-once-only-post/index.md`,
`status: sharp`), itself a carve-out of parent pitch 2 (`docs/ship-flow/2-agent-native-pr-review-runtime/shape.md`,
W3 "Safe recovery" + line 206 naming the exact design surface: authorization hash,
idempotency marker, remote receipt authority, ambiguous-timeout reconciliation). No
fresh scope inference occurred; the open design decisions are surfaced as gate decisions
below rather than silently chosen.

### Appetite (forcing budget) and cut order

2 working days. Load-bearing safety core (never cut): pending-payload persistence, the
five receipt-event payload schemas, reconcile-before-retry, head/payload invalidation,
rollback flag + evidence preservation. If the budget is threatened, cut in this order and
park cleanly (re-enterable state, open findings recorded) — never extend silently, never
compress validation:

1. **Cut first — active daemon preauthorization wiring.** Default-deny is satisfiable by
   *absence*: ship "the daemon never takes the new posting path" (permanently denied, no
   preauthorization mechanism). This literally satisfies checklist item 3's default-deny
   while deferring the typed/head/coverage/idempotency preauthorization gate to a follow-up.
2. **Cut second — background retention sweeper.** Ship the bounded-expiry *policy* + a GC
   hook that runs on the next same-run invocation; defer an autonomous background sweeper.

A budget/scope variance is a drift signal to investigate at the gate, not a number to hit
by padding or stripping tests.

### Reverse-recovery audit (against merge target `origin/main`)

Audited against `origin/main` (fetched); the load-bearing kc-pr-flow files
(`review-runtime.sh`, `kc-pr-review/SKILL.md`, `gh-api-patterns.md`, `review-runtime.md`)
are byte-identical between this branch and the merge target (empty `git diff`), so the
verdicts below are read off the merge target, not a stale branch. #54/#55 on `origin/main`
touch only ship-flow/docs, not the runtime.

Layer trace of the "resume + once-only post" path, five-state classified with `file:line`:

| Layer | State | Evidence |
|---|---|---|
| Posting entry (skill Step 7) | WORKING, not once-only | `kc-pr-review/SKILL.md:1691-1700`; posts via `gh pr review` / `gh api .../reviews`, no idempotency/resume |
| Posting authority receipt (`interactive-post-gate/v1`) | WORKING, no idempotency surface | `SKILL.md:1644-1646` ("no ... idempotency, resume, lock-recovery, retention, or daemon surface") |
| GitHub review mutation payload | WORKING | `gh-api-patterns.md:84-129` — `POST .../reviews {commit_id,event,body,comments[]}`, no native idempotency key |
| Remote receipt readback | WORKING (reused) | `gh-api-patterns.md:148-165` — `GET .../reviews` returns each review's stored `body` + `commit_id` |
| 5 receipt event names (`head.observed`,`authorization.granted`,`post.intent`,`post.result`,`run.invalidated`) | STUB | `review-runtime.sh:554` recognizes the names; `reference/review-runtime.md:113` — "with empty payloads", grants "no ... authorization, or posting authority" |
| Durable event log / safe-I/O / reservation locks / idempotent-append convergence | WORKING (reused) | `reference/review-runtime.md:51-115` |
| Pending-payload store (mode-0600 file) | MISSING | no pending-post artifact exists |
| Ambiguous-POST remote reconciliation | MISSING | deferred, `reference/review-runtime.md:204` |
| Resume (replay-compatible-only, retry-incomplete-only) | MISSING | deferred, `reference/review-runtime.md:204` |
| Retention / GC of failed pending payloads | MISSING | deferred, `reference/review-runtime.md:204` |
| Daemon default-deny preauthorization | MISSING | daemon posts via legacy skill path today (`docs/daemon.md:24`), no new-path gate |

**Verdict: STUB-fill + scoped-MISSING additions, NOT greenfield.** The runtime reference
(`review-runtime.md:204`) already names this exact increment ("Increment 2.3 owns ... resume,
retention, once-only posting, remote reconciliation, and daemon mutation"). Reused as-is: the
event log, Python safe-I/O boundary, reservation/quarantine locks, idempotent-append
convergence, and the `interactive-post-gate/v1` authorization receipt. Greenfield is confined
to the pending-payload artifact and the posting/reconcile helper — the seams the reference
explicitly deferred. Implementation MUST re-verify the STUB claim (reserved names still
empty-payload) and the MISSING claims against a fresh merge target before building, and
escalate rather than build if a premise has collapsed.

### Design determination: `design: required`

Affects a contract (payload schemas for the 5 reserved event types), an interface (the
`pending-post/v1` file schema + permissions), and a protocol (idempotency marker in the
review body + remote reconciliation). Concrete design decisions attached:

**A1. Boundary-preserving placement.** `review-runtime.sh` keeps its stated network/GitHub/
posting/authorization boundary (`reference/review-runtime.md:11`). It gains ONLY the closed
payload schemas for the five reserved receipt events — filling the forward-compatibility
slots the reference reserved (`reference/review-runtime.md:113`). All network, posting, and
reconciliation authority lives in a NEW source-safe helper (`scripts/review-post.sh`) plus
`kc-pr-review` Step 7. The helper consumes an `interactive-post-gate/v1` authorization and
emits `post.intent` / `post.result` / `run.invalidated` receipt events; the runtime records
and replays them but never posts. Existing complete shadow receipts never contain these five
events, so tightening their payload schemas does not invalidate any receipt in the wild.

**A2. Idempotency key.** `idempotency_key = sha256(review_key | commit_id | payload_sha256)`
— binds exact review identity, exact reviewed head (`commit_id`), and the exact serialized
payload. Any of the three changing yields a different key (so a changed payload or moved head
can never collide with a prior post).

**A3. Remote receipt marker.** The POSTed review body carries an invisible receipt line
`<!-- kc-pr-flow-post-receipt: <idempotency_key> -->`. It is remotely readable because
`GET .../reviews` returns the raw stored body (not rendered HTML), verified by
`gh-api-patterns.md:152-155`. Reconciliation matches on `author == self` AND body contains
the marker; `commit_id` on the remote review object is the marker-independent fallback key.

**A4. Pending-payload schema (`kc-pr-flow.pending-post/v1`).** A closed file, mode `0600` in
a mode-`0700` dir under the run dir, written via private-temp + rename (same durability
discipline as accepted logs). Fields, exactly: `schema`, `review_key`, `run_id`, `commit_id`
(authorized head), `event` (APPROVE/REQUEST_CHANGES/COMMENT), the exact serialized review
payload (`body` + `comments`), `payload_sha256`, `idempotency_key`, `authorized_at`,
`expires_at`. Rejected: excerpts, prompts, diffs, raw model output.

### Design detail — once-only posting protocol (checklist item 1)

Designed against real GitHub mutation failure modes (timeout / unknown-outcome mid-POST); the
POST is treated as NON-atomic:

1. **Pre-POST (durable-before-mutate).** From a valid `interactive-post-gate/v1` authorization,
   append `authorization.granted` (bound to `commit_id` + `payload_sha256`, consumed exactly
   once) → append `post.intent` (carries `idempotency_key`, `commit_id`, `payload_sha256`) →
   write the `pending-post/v1` file. All durable before any network call.
2. **POST** `.../reviews` with the marker-bearing body.
3. **Classify the outcome:**
   - **Success (2xx):** append `post.result{outcome: posted, remote_review_id, idempotency_key}`; remove pending file.
   - **Definite non-retryable failure (validation 4xx):** append `post.result{outcome: failed}`; move pending to failed-retention.
   - **Ambiguous (timeout / network drop / 5xx / unknown):** do NOT assume either way; leave the pending file durable; do NOT blind-retry.
4. **Reconcile-before-retry (the crux).** On resume with a `post.intent` lacking a matching
   `post.result`: `GET .../reviews`, filter `author == self`, scan for the marker == our
   `idempotency_key`:
   - **Marker found →** the earlier POST landed → append `post.result{outcome: posted (reconciled), remote_review_id}`; remove pending. **No second POST.**
   - **Marker absent AND head unchanged AND payload unchanged →** safe to retry the exact same payload **once** (bounded), then re-reconcile.
   - **Head moved OR payload changed →** invalidate (below); never post the stale payload.

This guarantees the same `idempotency_key` produces no second GitHub review even across a
crash mid-POST, and never relies on an assumed-atomic POST.

### Design detail — resume/replay compatibility + authorization invalidation (checklist item 2)

**Replay-compatible state (the only state that resumes):** a run whose `events.jsonl` replays
to a complete terminal receipt (existing replay lifecycle), whose exact-head identity still
matches the current PR head, and whose latest `post.intent` (if any) has no matching
`post.result`. Anything incomplete/moved/invalid does NOT resume (fail closed). Resume retries
only *incomplete* work — never a completed post, never a moved-head payload.

**Authorization invalidation.** A fresh `head.observed` (exact-head re-check) is recorded at
resume and immediately pre-POST. Invalidation → append `run.invalidated{reason}`, pending file
removed, payload never posted:
- PR head SHA != authorized `commit_id` → `reason: head_moved`.
- Payload content hash != authorized `payload_sha256` → `reason: payload_changed`.
- Review-key / config drift → `reason: identity_changed`.

### Design detail — daemon default-deny + retention + rollback (checklist item 3)

**Daemon default-deny.** The new posting path is OFF for the daemon unless an explicit
preauthorization is present. Absence = denied → the daemon uses its existing notify/suggest
path (`docs/daemon.md`), never the new mutation path. When present, it posts only when ALL
gates pass: typed decision state present + complete required coverage, current head ==
authorized head (fresh `head.observed`), and clean idempotency reconciliation. Never daemon
APPROVE (parent pitch line 58). (Per the cut order, the minimal ship is default-deny by
absence; the active preauthorization gate is the first cut if over budget.)

**Retention / expiry.** Successful pending payloads removed immediately on
`post.result{posted}`; stale (invalidated) payloads removed at invalidation. A *failed*
pending payload that cannot reconcile expires after a bounded window
(`KC_PR_FLOW_PENDING_RETENTION_SECONDS`, proposed default 7 days) → GC removes it and appends
`run.invalidated{reason: expired}`. **Fail-safe invariant:** never GC a pending payload whose
`post.intent` lacks a reconciled `post.result` while its head still matches AND it is within
the window — that is exactly the evidence needed to reconcile an uncertain remote result.

**Rollback.** `KC_PR_FLOW_ONCE_ONLY_POST` (default `off`) gates the new posting path. Off →
the legacy `gh pr review` path stays authoritative and byte-identical to today. Rollback =
unset the flag; it disables the new path for fresh invocations but NEVER deletes pending-payload
files or receipt events, so an uncertain remote result from a prior new-path POST stays
reconcilable. Evidence preservation is the rollback invariant.

### Acceptance criteria (end-state properties, falsifiable, verified outside task prose)

- **AC1 (end value — exactly-once under fault).** Under an injected ambiguous-POST fault
  (request reaches GitHub, response lost), resume reconciles the remote receipt and the PR ends
  with exactly one review. *Verified by:* E2E fault-injection test driving the real posting
  helper against a controllable reviews endpoint returning timeout-then-present, asserting
  remote review count == 1. *Baseline that can move wrong:* blind retry without reconciliation
  yields 2 reviews.
- **AC2 (head-moved never posts stale).** Head changes after authorization → zero POSTs and a
  `run.invalidated{head_moved}` event. *Verified by:* test asserting zero mutation calls + the event.
- **AC3 (idempotency key is once-only).** The same `idempotency_key` submitted twice
  (crash-replay) yields no second GitHub review. *Verified by:* reconciliation test — marker
  match → `post.result` reconciled, zero second POST.
- **AC4 (pending artifact hygiene).** The pending file is mode `0600` in a mode-`0700` dir and
  validates against `pending-post/v1` with no excerpt/raw fields. *Verified by:* `stat` +
  schema-validation test.
- **AC5 (daemon default-deny).** A daemon iteration with no preauthorization takes the new
  posting path zero times. *Verified by:* daemon-gate test asserting the legacy path is used.
- **AC6 (retention fail-safe).** A failed pending payload past the window is GC'd and recorded;
  a within-window unreconciled pending payload with matching head is never GC'd. *Verified by:*
  retention test with two injected clock values.
- **AC7 (rollback preserves evidence).** With the flag off, legacy posting is byte-identical to
  today AND prior pending-payload evidence survives. *Verified by:* rollback test.

### E2E-first acceptance

This changes user-visible GitHub mutation behavior, so AC1 is verified by exercising the real
posting helper end to end (fault-injected), not unit-only. Constraint: CI must NOT post to a
real production PR. Gate decision D2 chooses the harness (recorded/stub transport preferred over
a throwaway test PR).

### Doc diff proposed (before/after)

- `reference/review-runtime.md:204` and `docs/review-runtime.md:250` — **before:** "This
  increment intentionally has no ... resume, retention, once-only GitHub mutation ... Increment
  2.3 owns ... resume, retention, once-only posting, remote reconciliation, and daemon
  mutation." **after:** move resume / retention / once-only posting / remote reconciliation
  from "deferred to 2.3" into documented capabilities, with the payload schemas of the five
  receipt events, the `pending-post/v1` schema, the reconcile-before-retry protocol, and the
  rollback flag; keep genuinely-future items (append/compaction perf, predecessor lineage) as
  deferred.
- `kc-pr-flow/CLAUDE.md` §"Typed Review Runtime" tail — **before:** "Crash-safe recovery ...
  once-only posting, reconciliation, and daemon mutation remain increment 2.3." **after:**
  document the shipped once-only posting seam, the rollback flag default-off, and daemon
  default-deny; narrow the "remains deferred" list.

Implementation applies these; validation verifies behavior diff and doc diff landed together.

### Spike — riskiest unverified mechanism

The load-bearing unproven claim is **remote-receipt reconciliation**: can we reliably detect
our own already-landed review after an ambiguous POST? *Spike result — feasible at API-shape
level:* `GET .../pulls/N/reviews` returns each review's stored `body` and `commit_id`
(`gh-api-patterns.md:152-155`); a body-embedded HTML-comment marker is stored verbatim in the
raw API body (comments are hidden only in rendered HTML), so it round-trips and is matchable.
*Residual uncertainty:* (a) marker survival through any future GitHub body transform —
mitigated by the `commit_id` fallback key; (b) the race where the review lands *after* our
list call — mitigated by binding to `commit_id` + bounded re-list. *Recommendation:* execute
stage MUST confirm marker round-trip against one live throwaway PR before the daemon path is
ever enabled. This is NOT "no spike needed" — it is the load-bearing mechanism, spiked to
API-shape, with full-runtime confirmation deferred to execute's E2E.

### One-sentence pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden
assumption** — that our idempotency marker reliably round-trips through GitHub's stored review
body; if GitHub ever strips or transforms it, reconciliation silently fails open to a duplicate
or fails closed to a stuck pending payload. (Mitigation already in scope: the `commit_id`
marker-independent fallback key + the execute-stage live round-trip confirmation.)

### Implementation dispatch sizing

**ONE worker session (default), TDD, ordered a→b→c.** The three behaviors — (a) pending-payload
persistence + the five event payload schemas, (b) reconcile/resume, (c) daemon gate + retention
+ rollback — share one contract (the payload/idempotency schema) and fit the 2-day appetite.
Splitting would pay repeated cold-start re-reads of the 2875-line runtime for marginal
wall-clock, and the behaviors are tightly coupled through the shared idempotency contract. Each
behavior is a complete RED→GREEN slice within the one session (never tests-in-one/code-in-next).

### Gate decisions (captain resolves at the gate)

- **D1 — retention window default.** Propose `KC_PR_FLOW_PENDING_RETENTION_SECONDS` = 7 days.
- **D2 — E2E harness for AC1.** Recorded/stub GitHub transport (recommended, no real mutation
  in CI) vs. a dedicated throwaway test PR.
- **D3 — rollback flag.** Propose `KC_PR_FLOW_ONCE_ONLY_POST`, default `off`.
- **D4 — scope vs. 2-day appetite.** Confirm the cut order (daemon preauthorization first,
  retention sweeper second) or re-appetite if the full Done Signal must ship intact.

## Stage Report: ideation

- DONE: Exactly-once posting is designed against real GitHub mutation failure modes (timeout/unknown-outcome mid-POST): idempotency key + reconcile-a-durable-marker-or-remote-receipt-before-retry, not an assumed-atomic POST.
  "Design detail — once-only posting protocol": key = sha256(review_key|commit_id|payload_sha256); durable-before-mutate (authorization.granted + post.intent + pending file), then ambiguous outcomes reconcile via GET .../reviews marker/commit_id match before any retry.
- DONE: Resume/replay compatibility and authorization invalidation are concretely specified: which state is replay-compatible, what a head/payload change invalidates, and the exact pending-payload schema + restrictive permissions.
  "Design detail — resume/replay ...": replay-compatible = complete terminal receipt + matching head + intent-without-result; head_moved/payload_changed/identity_changed each emit run.invalidated; pending-post/v1 schema fields enumerated, mode 0600 in mode-0700 dir, temp+rename.
- DONE: Default-deny daemon preauthorization, bounded-retention expiry of failed pending payloads, and a rollback path that disables the new posting path without deleting evidence needed to reconcile an uncertain remote result.
  "Design detail — daemon default-deny + retention + rollback": deny-by-absence + full-gate preauthorization, KC_PR_FLOW_PENDING_RETENTION_SECONDS expiry with a fail-safe never-GC-within-window invariant, and KC_PR_FLOW_ONCE_ONLY_POST default-off rollback that preserves pending/receipt evidence.
- DONE: Reverse-recovery audit against the merge target.
  Fetched origin/main; load-bearing files byte-identical to HEAD (empty diff); layer table classifies the 5 reserved events as STUB (review-runtime.sh:554, reference:113) and the deferred seams as MISSING (reference:204) — verdict STUB-fill + scoped-MISSING, not greenfield.
- DONE: Design determination, AC, E2E-first, doc diff, spike, pre-mortem, dispatch sizing.
  design: required with A1-A4 decisions; 7 falsifiable AC each with a Verified-by outside prose (AC1 is the E2E fault-injection end-value); before/after doc diff for review-runtime.md:204 + CLAUDE.md; spike proves marker round-trip at API-shape with commit_id fallback; hidden-assumption pre-mortem; ONE-session TDD sizing.
- SKIPPED: Opening captain scope-question round.
  Scope is captain-authored verbatim from the sharp pitch 2.3 (stated small-scope reason); genuine open decisions surfaced as gate decisions D1-D4 for resolution at the gate rather than block-waiting.

### Summary

Composed the full ideation for "Safe resume and once-only post" (increment 2.3) grounded in
primary-source runtime code and the parent/child ship-flow pitches. Central architecture
decision: keep review-runtime.sh network-free and only fill the five reserved receipt-event
payload schemas (a documented STUB per reference:113), placing all posting/reconcile/network
authority in a new source-safe helper + kc-pr-review Step 7 — so once-only posting reuses the
existing event log, safe-I/O, locks, and authorization receipt rather than a greenfield
rebuild. Four gate decisions (retention window, E2E harness, rollback flag, scope-vs-appetite
cut order) are left for the captain; the 2-day appetite is tight for the full Done Signal, so a
non-destructive cut order (daemon preauth first, retention sweeper second) is proposed.

## Stage Report: implementation

- DONE: Every AC (AC1–AC7) is proven by a real test/exercise that CAN fail — especially AC1 exactly-once-under-fault via the D2 stub-transport E2E fault injection, NOT prose and NOT a presence-grep.
  `kc-pr-flow/scripts/review-post.test.sh` (57 assertions) exercises all 7 ACs against `test/fixtures/review-post/stub-transport.sh`; AC1's ambiguous-then-landed fault (`post-plan: ambiguous`) asserts resume ends with exactly one remote review (a naive blind-retry baseline would assert 2). Also added coverage for the untested `failed` (4xx definite-failure) classification branch, which existed in shipped code with zero prior exercise.
- DONE: `review-runtime.sh` stays network-free; ALL posting/reconcile/network authority lives in the new source-safe `scripts/review-post.sh` + `kc-pr-review` Step 7.
  `grep -n 'curl\|wget\| gh ' kc-pr-flow/scripts/review-runtime.sh` → no matches; `review-runtime.sh` only gained the five closed receipt payload schemas (commit `c1f77cb`, 305/305 `review-runtime.test.sh` unaffected).
- DONE: Rollback flag OFF ⇒ legacy posting path byte-identical (AC7); durable-before-mutate and reconcile-before-retry exercised against the stub transport's ambiguous-POST fault.
  `KC_PR_FLOW_ONCE_ONLY_POST` (default off) gates `review-post.sh post` at the entry (exit 3, zero writes/network calls when off — commit `174dfb4`); `kc-pr-review` Step 7's existing `gh pr review` prose is untouched text, only relabeled "Legacy posting path (default)" and reached unconditionally when the flag is off/unset (commit `f92bb53`). Durable-before-mutate (`authorization.granted`→`post.intent`→pending file, all before the POST) and reconcile-before-retry (`GET .../reviews` marker match before any retry) are the mechanisms AC1/AC3 above exercise.
- DONE: Source-safe (public marketplace repo): no secrets, no internal org markers, no real tokens in fixtures.
  All new fixtures use synthetic placeholders (`acme/widgets`, `review-bot`, `aaaa…`/`bbbb…` hex SHAs); `shellcheck` and `bash -n` clean on `review-post.sh`, `review-post.test.sh`, and `stub-transport.sh`.
- DONE: Part C — reconcile-before-retry + resume + authorization invalidation (AC1–AC3).
  `review_post_cmd_resume` in `scripts/review-post.sh` reconciles via remote-marker scan before any retry, bounds the retry to one attempt, and re-reconciles after; head/payload/identity changes emit `run.invalidated` and drop the pending payload (commits `d250379`, `00e0ab7` fixed a sequence-numbering off-by-one that was failing all resume/gc paths — verified RED (34/45 failing) → GREEN (45/45, then 57/57 after further additions)).
- DONE: Part D — daemon default-deny preauthorization (AC5) + retention/GC (AC6) + rollback flag (AC7).
  Default-deny is satisfied by absence per the D4 cut order: `KC_PR_FLOW_ONCE_ONLY_POST` off denies every caller (daemon or interactive) with no daemon-specific gate to test separately (commit `174dfb4`). `review_post_cmd_gc` never removes a within-window unreconciled pending payload (fail-safe invariant) and expires past-window ones with `run.invalidated{expired}`.
- DONE: Part E — wire `kc-pr-review` Step 7 to the new helper; apply the before/after doc diff.
  Step 7 branches on the flag (commit `f92bb53`): on → build request/gate JSON, rediscover a resumable prior run by `review_key` before ever calling `post` fresh (crash-safety a naive re-dispatch would miss), then call `review-post.sh post`/`resume` and branch on status; off → the original `gh pr review` text, unchanged. Doc diff applied to `reference/review-runtime.md`, `docs/review-runtime.md`, `CLAUDE.md`, and `README.md` per the entity's proposed before/after.
- DONE: Part F — full-suite regression.
  All 7 kc-pr-flow test files green: `review-runtime.test.sh` 305, `review-post.test.sh` 57, `review-shadow.test.sh` 155, `review-runtime-benchmark.test.sh` 135, `cross-model.test.sh` 62, `review-architecture-diagrams.test.sh` 43, `review-architecture-diagrams-validator.test.sh` 34 — 791 passed, 0 failed. `git diff --stat origin/main...HEAD`: 11 files, +1370/-18, scoped to `kc-pr-flow/**` plus one CI workflow.
- SKIPPED: Autonomous background retention sweeper (D4 cut-second item).
  Shipped the bounded-expiry policy + an on-demand `review-post.sh gc` hook only, per the entity's explicit cut order; no cron/daemon wiring invokes it automatically. Flagged here as the surviving deferred item — not silently dropped.
- SKIPPED: Active daemon preauthorization gate (D4 cut-first item; typed decision state + coverage + fresh head/idempotency recheck before an autonomous post).
  Default-deny by absence (rollback flag off) is the entire daemon-safety mechanism today, documented explicitly in `CLAUDE.md`/`README.md`/`reference/review-runtime.md` as still-deferred rather than silently implied complete.

### Summary

Resumed from two prior checkpoints (Part A closed, Part B unverified WIP) and drove the remaining
work — reconcile/resume (C), daemon default-deny + retention + rollback (D), Step 7 wiring + doc
diff (E), full regression (F) — to a verified GREEN state: 791 tests passing across all 7
kc-pr-flow suites, `review-runtime.sh` confirmed network-free, and all 7 ACs proven by fault-
injection or gate-refusal tests rather than prose. Found and fixed one real coverage gap (the 4xx
`failed` classification branch had zero prior test exercise) and traced an apparent "hang" during
verification to a real off-by-one sequence-numbering bug that a concurrent session fixed
mid-session (commit `00e0ab7`) — confirmed by re-running the suite clean after the fix landed. The
two D4 cut-order items (autonomous retention sweeper, active daemon preauthorization) remain
deferred exactly as scoped, documented rather than silently dropped. This worktree was actively
co-edited by another session during this stage (commits `00e0ab7`, `174dfb4`, `f92bb53`, plus
docs/CI work) — all changes were verified against the actual code and test suite before being
counted as done here, not trusted on narration alone.

## Stage Report: validation

Verdict: **REJECT → route back to implementation.** A confirmed exactly-once violation defeats the entity's Done Signal ("an approved payload is posted at most once"). Run coordinator-driven with two fresh-context reviewer subagents (correctness + silent-failure) plus independent primary-source code adjudication; every cited file:line was verified against the actual file (0 fabricated citations, so no reviewer round was discarded).

### Findings (reconciled across both reviewers + code adjudication)

- **P1 — CONFIRMED (empirical repro + code):** resume's reconcile-before-retry fails OPEN when the reconcile `list` GET under-reports a landed review. `review-post.sh:555` `|| return 74` only catches a non-zero transport exit; an exit-0 but stale/incomplete body — most realistically GitHub's read-after-write consistency lag returning a well-formed `{"reviews":[]}` that does not yet include the just-created review — makes `review_post_scan_marker` (`:259-266`) return empty, indistinguishable from "marker genuinely absent" (`:557`), so the code falls through to a blind retry POST (`:567-574`) → **duplicate GitHub review**. Reviewer drove real `review-post.sh` with a `list` returning `{"reviews":null}` + a POST that lands server-side but returns `http_status:0`: post → 1 review, resume → **2 reviews / post-count=2**; the `{"reviews":[]}` lag variant is the identical code path. `--paginate` + `--argjson` in the gh adapter close the malformed/paginated sub-cases but NOT the eventual-consistency lag. Fails open, invisible to the caller (jq errors go to stderr; returned JSON status looks normal).
- **P2 (F2) — CONFIRMED:** the same reconcile scan (`:259-266`, consumed `:555-556`,`:578-579`) filters `.user == self_login`; a `--self` that differs from the identity the token actually posted under (bot vs user vs app-slug) misses the landed review → bounded retry → second review. `--self` is an unvalidated required input with no cross-check against the POST response author.
- **P2 (F1) — CONFIRMED:** the `post` path (`:308-434`) never scans the remote for an existing landed marker (only `resume` does); `review_runtime_start` (`:375`) mints a fresh `run_id` per call, so two `post` calls for the same review_key take different per-run reservation locks (`review-runtime.sh:1288`) — no mutual exclusion — and a prior run that already reached terminal `posted` (pending removed) is invisible to the SKILL step-2 rediscover-scan (which only finds runs with a surviving `pending-post.json`). Repeat or concurrent `post` at the same head → duplicate review. Partially overlaps the deferred `once-only-daemon-preauth-gate` (7j/vf backlog) for the daemon case, but the single-writer repeat-`post` case is in-scope for the "never a blind second POST" invariant.
- **P2 — CONFIRMED (silent-failure):** malformed `head` GET (exit 0, body lacking `head_sha`) → `jq -r '.head_sha'` yields literal `null` → `null != commit_id` → misclassified `head_moved` → review silently dropped (`:382-383` post, `:536-537` resume). Fails CLOSED (drop, not duplicate), less dangerous than P1.
- **nit — CONFIRMED:** `gc` does not validate `now_epoch`; a non-numeric value makes `[ "$now_epoch" -lt "$expires_epoch" ]` (`:638`) error→false, skipping the within-window keep-guard → fail-open deletion of within-window reconcile evidence. Only reachable via a garbage `--now-epoch` arg; production default (`date -u +%s`) is always numeric.
- **nit — CONFIRMED (perf, non-blocking):** each posting event append spawns multiple `python3` processes (`review-runtime.sh:928,1264`); ~0.47s python3 startup on this box makes a single `post` ~45s locally (CI python3 startup ~30ms → non-issue; append/compaction perf is already a documented deferral). This explains the local full-suite slowness observed during validation.

### Checks that PASSED (confirmed against code)
- Crash-resume exactly-once (the interrupted-then-resume case, distinct from the lag case above): reconcile hit → `posted_reconciled`, no second POST (`:555-565`); retry bounded to one (`:569-591`).
- Durable-before-mutate: `head.observed`/`authorization.granted`/`post.intent`/pending all persist (`:396-419`) before the POST (`:424`); crash between intent and pending → resume refuses (`:510-513`) → under-post, never double-post.
- Default-deny / rollback: `review_post_rollback_enabled` requires literal `on` (`:187-189`), checked before any write/network (`:319`); OFF leaves legacy `gh pr review` byte-identical.
- GC fail-safe within-window keep (`:638-641`); classify defaults unknown/parse-failed/`http_status:0` → `ambiguous` (fail-safe, `:268-296`).
- Idempotency key `sha256(review_key|commit_id|payload_sha256)` field order/quoting correct (`review-runtime.sh:714-716`, `review-post.sh:366`); pending mode 0600 in 0700 dir via temp+rename.
- Source-safe: fixtures synthetic only (`acme/widgets`, `review-bot`, `aaaa/bbbb/cccc/dddd`); no secret/token/PII/internal-marker. `bash -n` + `shellcheck` clean. Full suite 791/0 (independently re-run by coordinator).

### Test coverage gap (root cause the green suite hid P1)
`stub-transport.sh` `list` always returns a faithful, immediately-consistent array (`:40-46`); no test exercises a `list` that under-reports a landed review (lag / `--self` mismatch), so exactly-once is only proven under a perfectly-consistent read. This gap is exactly what a claim-breaking adversarial probe targets — found here by analysis instead. New RED tests for the lag + `--self`-mismatch + repeat-`post` paths are required with the fix.

### Deferred to re-validation (after the P1 fix)
- Cross-model gate: codex out of usage credits (until ~Jul 29); agy/gemini non-interactive runs were flaky this session. Not gating this REJECT (P1 already empirically confirmed). Run one clean cross-model pass on the fixed diff before any approval.
- Mechanical adversarial spot-check (claim-breaking edit → suite red): superseded for this round by the confirmed coverage gap above; run on the fixed suite.

### Correction-round budget record
- Round 1 (validation): estimate n/a (first pass) → actual 2 reviewer dispatches + coordinator adjudication. Findings disposition: 1 P1 + 3 P2 + 2 nits, ALL confirmed against code, 0 declined, 0 fabricated citations. Route-back to implementation with the file-anchored fixes below. (Not "nothing found" and not "all declined" — real defects, all actionable.)

### Fix direction (file-anchored, for the implementation round)
1. `review_post_scan_marker` / reconcile: distinguish "list unusable / not positively confirmable complete" (jq non-zero, `.reviews` not an array, or an empty list that could be consistency lag) from "list valid and marker genuinely absent"; on anything not positively confirmed, **fail closed** — emit `ambiguous`, keep pending, do NOT retry (`:555-574`, `:578-579`). Never blind-retry on a first empty reconcile given read-after-write lag.
2. Validate `--self` against the POST response's author (or the token identity) before trusting a scan miss (`:259-266`).
3. `post` path: rediscover-and-reconcile against the remote (or a durable per-`review_key` marker) before a fresh POST, covering terminal-`posted` prior runs, not just surviving-`pending` ones (`:308-434`, SKILL step 2).
4. Validate `head_response` shape before the `head_moved` decision (`:382-383`, `:536-537`); a shape-invalid head GET should fail closed as ambiguous, not as `head_moved`.
5. `gc`: validate `now_epoch` numeric before the window comparison (`:638`).
6. Add RED tests: under-reporting/lagging `list`, `--self` mismatch, repeat/concurrent `post`, malformed `head`, non-numeric `now_epoch`.

## Correction Round 1: implementation (post-validation rework)

Driven by the coordinator directly rather than a dispatched ensign: the findings were file-anchored and bounded, and three consecutive background workers had been lost to session/account interruptions.

### Budget record (round 1)
- Declared estimate: one implementation session (ideation sizing). Actual: one coordinator session, two commits (`b99e132`, `31340a8`) plus one cross-model round.
- Findings disposition: 6 routed in (1 P1, 3 P2, 2 nits) → **4 fixed as real defects, 1 downgraded to hardening on evidence, 1 already-mitigated**. Cross-model added 6 more → **1 fixed (P1), 2 hardened, 1 refuted with reason, 2 accepted as benign**. Nothing silently dropped.
- Deviation: within tolerance; no design reset required.

### Re-anchor against the source requirement
Re-read the entity's Vertical Slice / Boundary / Done Signal before touching code. The load-bearing sentence — "an approved payload is posted **at most once**" — is what the routed-back findings violated; no original constraint was dropped, and the AC set is unchanged except where the fix necessarily changes retry *timing* (recorded below).

### RED → GREEN evidence
RED was captured against the **pre-fix** helper (a scratch copy with `review-post.sh` restored from `f92bb53`, new tests applied): **15 failing / 65 passing**, including four `expected [1], got [2]` duplicate-review assertions — the P1 reproduced independently of the reviewer's own repro. GREEN after the fix: **review-post 86 passed / 0 failed**, full suite **820 passed / 0 failed** across all 7 kc-pr-flow suites (791 before this round), `shellcheck -S error` clean, CI doc-safety greps intact.

### What changed
- **P1 (lagging list)** — a retry now requires a reconcile read that positively confirms remote state. An absent marker only proves "never landed" after `KC_PR_FLOW_RECONCILE_CONFIRM_SECONDS` (default 60) has elapsed since that run's `post.intent`; inside the window resume reports `ambiguous{reconcile_unconfirmed}`. Derived from the already-durable `post.intent.occurred_at` — deliberately **no new event type and no new pending field**, since both schemas are closed and CI-frozen (2.1/2.2 fixtures).
- **P1 (unusable list)** — a `list` body that is not a reviews array fails closed as `ambiguous{reconcile_unavailable}`; it is never read as "marker absent".
- **P2 (author mismatch)** — marker matching no longer filters on review author; the key already pins the payload.
- **P2 (repeat post)** — `post` reconciles against the remote marker before its own POST, covering a prior run that reached terminal `posted` and so has no pending payload for the skill's rediscovery scan.
- **P1 from cross-model (concurrent post race)** — when the pre-POST reconcile cannot confirm a remote copy, `post` also checks local durable state for another run that authorized this exact payload and never settled, and defers with `ambiguous{prior_attempt_unsettled}`.
- **nit → real (gc clock)** — `gc` rejects a non-numeric `--now-epoch`; RED proved the old behavior actually deleted within-window reconcile evidence. Same class fixed for `KC_PR_FLOW_RECONCILE_CONFIRM_SECONDS`, which failed OPEN into the very retry its window prevents.
- Docs synced: `reference/review-runtime.md`, `docs/review-runtime.md` (operator reason table), `CLAUDE.md`, `README.md`, and `kc-pr-review` SKILL Step 7 (new `ambiguous` reasons; Step 7 already refuses to fall back to the legacy path on `ambiguous`, so no duplicate is introduced at the seam).

### Corrections to the validation findings (evidence over report)
- **Malformed `head` response was NOT a live defect.** The RED run's malformed-head assertions passed against the pre-fix helper: the runtime's `head.observed` payload validation already failed closed (exit 74) before any `head_moved` event was written. The added shape guard is defense-in-depth, not a bug fix.
- **Cross-model "marker injection suppresses our post" is refuted.** `idempotency_key` is sha256 over `review_key|commit_id|payload_sha256`, and `payload_sha256` covers the not-yet-published review body, so a third party cannot derive the marker before we post. After we post, reusing it only suppresses a duplicate — the intended behavior.
- **Cross-model "`jq -e` stream exit status" is real semantics but was unreachable** (one `post.intent` per run). Hardened anyway with a slurped `any()`.
- Cross-model `occurred_at`-corruption lock-up is unreachable (the authoritative log is integrity-validated before replay) and bounded anyway: `gc` expires the pending payload after its retention window.

### Behavior change the captain should know
The truly-lost retry is no longer immediate. A payload whose POST was genuinely lost is retried on a resume **after** the confirm window, not on the first resume. This is the unavoidable cost of the P1 fix: at the moment of an empty list, "lagged but landed" and "never landed" are indistinguishable, so the only safe discriminator is elapsed time. The existing AC1 truly-lost assertion was updated to encode this, and a new assertion proves no retry happens inside the window. Window is operator-tunable via `KC_PR_FLOW_RECONCILE_CONFIRM_SECONDS`.

### Named residual (not solved, not hidden)
Two `post` invocations that enter the pre-POST check before either records `post.intent` can still both post. Full mutual exclusion needs server-side idempotency (GitHub exposes none for reviews) or a cross-process lock, and a lock reopens the crash-safe-lock / PID-reuse scope this plugin explicitly defers. Accepted for this increment and tracked alongside the deferred active daemon preauthorization gate (`once-only-daemon-preauth-gate`), which is the realistic source of autonomous concurrency. The shipped default (`KC_PR_FLOW_ONCE_ONLY_POST` off) denies every caller, so the race is not reachable without explicit opt-in.
