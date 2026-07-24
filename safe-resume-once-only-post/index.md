---
title: "Safe resume and once-only post"
source: superseded ship-flow pitch 2.3-safe-resume-once-only-post (agent-native PR review kit PR3); builds on ship-flow 2.1 (PR #48) + 2.2 (PR #50)
id: 50n4g9vyzdd12h03r6wskfkq
status: implementation
started: 2026-07-24T10:20:35Z
worktree: .worktrees/spacedock-ensign-safe-resume-once-only-post
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
