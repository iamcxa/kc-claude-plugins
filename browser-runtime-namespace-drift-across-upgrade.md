---
id: agdzctr6mabbddhp2wegbh42
title: "PR #135 changes the namespace for the same run, orphaning sessions live across the upgrade"
status: backlog
source: "cross-model review of PR #135 (Codex) plus local verification, 2026-08-02"
product: e2e-pipeline
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design:
lane:
---

## Problem

`namespaceForRun` derives the truncated namespace from a budget that now subtracts
`<session>.sock` instead of the old literal `daemon.sock`. For the same `runId` and socket
home, old and new code therefore return **different namespaces** whenever the run id is long
enough to truncate and the session name is shorter than `daemon` (6 characters).

Measured against `27bff48^` and `27bff48` with a 107-character run id:

| `--app` | old namespace | new namespace | old session could exist |
|---|---|---|---|
| `ab`, `app`, `secha` | `…-aaaaaaaaaaaa-…` | `…-aaaaaaaaaaaaaaa(a)-…` | **yes** |
| `daemon` (6 chars) | unchanged | unchanged | yes |
| `secha-app` (9 chars) | changed | changed | no — old path exceeded 103 |

A session opened by the old runtime in the first row is looked up by the new runtime under a
different namespace, so `close` and the cleanup path do not reach it: a leftover namespace
directory and possibly a live daemon nobody will close.

Reachability is narrow. `new-run-id` emits 29 characters, which does not truncate at the
default socket home, so this needs a caller-supplied long run id (the validator allows up to
128) plus a short app name plus a session live across the upgrade. It is also
transition-only: once every caller is on the new code the derivation is self-consistent.

## Why this is not the defect lane

There is an open design decision, so condition 4 fails. At least three defensible shapes:
accept it and document the transition, add a one-time sweep for namespaces that match the
old derivation, or stop deriving the namespace from the socket filename at all so the
identity does not move when the filename rule changes. Choosing among those is design work
and belongs in `ideation`.

## Shaping — audit, options, and what needs the captain

Shaped 2026-08-02 while the captain was away. **This does not choose**, for the same reason
[[e2e-runner-path-selector-enforcement]] does not: the three shapes differ in kind, and one
of them changes how a runtime identity is derived, which Gate Authority puts on the captain.

### 換句話說

**What breaks if this is wrong.** A browser session that was running when the plugin updated
becomes unreachable to the new code: `close` computes a different namespace, does not find it,
and the Chrome process and its socket directory stay behind. Nobody notices until the machine
has collected several, because nothing reports them.

**How expensive to reverse.** Accepting costs nothing now and cannot be un-decided later
except by doing one of the other two. A one-time sweep is one PR and self-deleting. Changing
how the namespace is derived is a runtime identity change: anything holding an old namespace
string stops matching, so it has the same across-upgrade problem it is meant to fix, once.

**What is actually being chosen.** Not "is this a bug" — the drift is measured. It is **how
much we owe a session that was alive during an upgrade**, and the answers range from nothing
to a schema change.

### Reverse-recovery audit (against `origin/main` `0a1079c`)

| layer | verdict | evidence |
|---|---|---|
| Namespace derivation | **WORKING (as designed)** | `namespaceForRun` truncates deterministically; #135's tests pin it |
| Same-input stability across versions | **EXISTS_BROKEN** | old and new return different namespaces when the run id truncates and the session name is shorter than `daemon` — measured against `27bff48^` vs `27bff48` |
| Reaching a session by namespace | **WORKING** | `close` recomputes the namespace from `(runId, socketHome, app)` |
| Sweeping namespaces not currently computed | **MISSING** | every access is scoped to one computed namespace (`cleanupClosedNamespaceState` at `:1924`, called at `:2880`, `:3028`, `:3075`); and no `readdirSync` in the runtime enumerates `<socketHome>/namespaces` — a structural check, not a vocabulary grep. An orphaned namespace is removed only by the platform's own tmp reaper — on macOS `/usr/libexec/tmp_cleaner`, daily, with a three-day horizon measured here. Unbounded only where no such reaper exists; Linux and CI are unverified |

### Fastest path and smallest cut

**Fastest:** accept it, document the transition in the changelog, and let the next `close`
after a restart leak one directory. Zero code.
**Smallest cut that changes behavior:** a sweep that removes namespace directories whose
socket has no live listener, run at open. Bounded, self-limiting, and it also collects
orphans from crashes, which is a pre-existing source this entity did not create.

### Options

**A — accept and document.** Zero code.
**Risk:** a Chrome process can survive with nothing pointing at it, and by this entity's own
restatement nothing reports it — so "the user closes it by hand" assumes a user who knows it
is there. On macOS the directory is reaped in three days; the process is not. Accepting also
means the next filename-rule change moves the identity again.
**Cost:** a changelog line.

**B — sweep dead namespaces at open.** Remove namespace directories whose socket has no
listener. Catches this drift and crash orphans alike. Needs a liveness test that cannot
mistake a slow daemon for a dead one, which is the whole risk: a wrong answer kills a live
session belonging to a concurrent run.
**Cost:** one function plus its tests, and a liveness predicate that has to be right.

**C — stop deriving the namespace from the socket filename.** The drift exists because the
budget subtracts `<session>.sock`, so changing the filename rule moves the identity. Deriving
the namespace from `(runId, socketHome)` alone and enforcing the length budget separately
makes the identity stable across any future filename change — the only option that prevents
recurrence rather than cleaning up after it.
**Risk:** it has the same across-upgrade discontinuity it is meant to fix, once, on the way in.
**Cost:** `namespaceForRun` plus its call site and the tests #135 added to pin the current
derivation — one seam, but the pinned tests all encode the filename-derived budget, so they
change with it.

**D — extend the existing cleanup ladder two rungs.** `cleanupClosedNamespaceState:1924-1961`
already removes `namespaces/<ns>/run` and then `namespaces/<ns>`, tolerating ENOTEMPTY at each
step. Nobody then removes `<socketHome>/namespaces` or the socket home itself, which is why
97.4% of the 5,111 roots are empty shells. Adding two more rungs in the same pattern at the
same site collects them.
**Risk:** low — the same ENOTEMPTY-tolerant pattern, and a non-empty directory is left alone.
**Cost:** smallest in the field; one function, no new call site, no liveness predicate.
**It does not fix the drift** — an orphan whose namespace moved is never passed to this
ladder. It is listed because the census says the population that actually exists is the empty
shells, not drift orphans.

### Design determination

`design: required`. B and C both decide something about a runtime contract — B about when the
runtime may delete state it did not create, C about what a namespace identity is derived from.
A decides nothing and would be `trivial-pass` on its own, which is exactly why the three
cannot share one determination and the choice comes first.

### What depends on the choice

Appetite, ACs, dispatch sizing and the E2E determination are all functions of which option is
taken, so they are deliberately not written. Recording them now would author scope.

### Design constraint shared with the sibling

[[browser-runtime-test-socket-home-leak]] and this entity's MISSING row are two symptoms of
one absent mechanism: the runtime removes only state it can address by an exactly recomputed
path. "Extend the ladder" (D) and "enumerate and sweep" (B) are competing designs for that
one mechanism. **They must not be decided twice independently** — whichever entity is worked
first settles the shape for the other.

### Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden
assumption**: that the orphan is worth reaching at all. The reachability bound is narrow — a
caller-supplied run id long enough to truncate, an app name under six characters, and a
session live across the upgrade — and no observed instance exists. Option B would then be a
liveness predicate carrying real risk, built for a population of zero. The check that would falsify
this before building was named here and then run — see below.

### Spike: the check was run, and it could not have failed — retracted

Swept this machine on 2026-08-02 and reported "drift-attributable orphans: zero", then
wrote "it argues for A". **Both are withdrawn.**

The zero is not evidence about the drift population. `namespaceForRun` is arity 2 in both
local installs — `~/.claude/plugins/cache/kc-claude-plugins/e2e-pipeline/3.1.1` and
`~/.claude/plugins/local/e2e-pipeline` — so the post-#135 code has never run here and **the
transition that produces a drift orphan has never occurred on this machine**. A check that
cannot produce the thing it is looking for reports absence either way. Proof Policy 8: the
silence carries information only after the check has been seen to speak, and this one was
never made to speak.

"It argues for A" was also a choice, in a section that opens by saying it does not choose.
Withdrawn on both counts.

**What the sweep does establish**, because it was a full census rather than a sample: there
are 5,111 socket-home roots under `/tmp/e2e-agent-browser-502-*`, of which **4,983 (97.4%)
are completely empty** and 128 hold a `namespaces/` directory. An earlier version of this
section and of the sibling seed said "almost every one holds `namespaces/e2e-run-123/`" —
that is inverted, and the correction moves the fix site (see the sibling).

The age histogram is 1970 / 692 / 1992 / 457 for 07-30 through 08-02: a hard floor at three
days with a **full** oldest bucket. That is a reaper horizon, not an origin —
`/System/Library/LaunchDaemons/com.apple.tmp_cleaner.plist` runs daily on this machine. So
the observation window is three days wide, which is a second reason the drift zero means
nothing, and it also falsifies "stays indefinitely" below.
