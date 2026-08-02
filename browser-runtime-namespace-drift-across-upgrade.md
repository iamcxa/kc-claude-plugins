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
| Sweeping namespaces not currently computed | **MISSING** | every access is scoped to one computed namespace (`cleanupClosedNamespaceState:1921`, `:2698`, `:2976`); `grep -Ei 'orphan|stale|prune|sweep'` over the runtime finds no reaper for the namespaces directory. An orphaned namespace stays indefinitely |

### Fastest path and smallest cut

**Fastest:** accept it, document the transition in the changelog, and let the next `close`
after a restart leak one directory. Zero code.
**Smallest cut that changes behavior:** a sweep that removes namespace directories whose
socket has no live listener, run at open. Bounded, self-limiting, and it also collects
orphans from crashes, which is a pre-existing source this entity did not create.

### Options

**A — accept and document.** Zero code. The leak is bounded by how many upgrades happen
while a session is live, and it is invisible rather than harmful: a stale directory under
`/tmp`, and at worst a Chrome process the user closes by hand.
**Cost:** a changelog line.

**B — sweep dead namespaces at open.** Remove namespace directories whose socket has no
listener. Catches this drift and crash orphans alike. Needs a liveness test that cannot
mistake a slow daemon for a dead one, which is the whole risk: a wrong answer kills a live
session belonging to a concurrent run.
**Cost:** one function plus its tests, and a liveness predicate that has to be right.

**C — stop deriving the namespace from the socket filename.** The drift exists because the
budget subtracts `<session>.sock`, so changing the filename rule moves the identity. Deriving
the namespace from `(runId, socketHome)` alone and enforcing the length budget separately
makes the identity stable across any future filename change.
**Cost:** larger, and it has the same across-upgrade discontinuity once, on the way in.

### Design determination

`design: required`. B and C both decide something about a runtime contract — B about when the
runtime may delete state it did not create, C about what a namespace identity is derived from.
A decides nothing and would be `trivial-pass` on its own, which is exactly why the three
cannot share one determination and the choice comes first.

### What depends on the choice

Appetite, ACs, dispatch sizing and the E2E determination are all functions of which option is
taken, so they are deliberately not written. Recording them now would author scope.

### Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden
assumption**: that the orphan is worth reaching at all. The reachability bound is narrow — a
caller-supplied run id long enough to truncate, an app name under six characters, and a
session live across the upgrade — and no observed instance exists. Option B would then be a
liveness predicate carrying real risk, built for a population of zero. The check that would falsify
this before building was named here and then run — see below.

### Spike: the falsification check was run, and it answers the pre-mortem

Swept this machine, which has run the pipeline across the #135 upgrade, on 2026-08-02.

**Drift-attributable orphans: zero.** The real socket home
(`/tmp/e2e-agent-browser-502-5943dac8f232`) holds five namespaces with no live socket, and
none of them is in the truncated `e2e-<prefix>-<12hex>` form the drift produces — three are
probe ids (`e2e-i107*`) and two are full readable run ids. Drift only moves *truncated*
namespaces, so none of these is an instance.

That is a measured zero for the population option B would be built to reap, and it argues
for A. Bounded: one machine, one user, and only orphans that survived to be observed.

**But the sweep found a different, larger leak.** There are **5,111** socket-home roots under
`/tmp/e2e-agent-browser-502-*`, oldest 2026-07-30, 524K total. Almost every one contains a
single `namespaces/e2e-run-123/` with no socket — `run-123` is the fixture run id used by six
files under `compiler/test/`, so the test suite creates a socket home per fixture browser home
and never removes it. Three days of test runs produced 5,111 directories.

That is a separate defect from this entity and is filed as
[[browser-runtime-test-socket-home-leak]]. It is recorded here because it is what the
falsification check actually turned up, and because it changes what option B would be for: a
reaper built for the drift would find nothing, while a reaper built for the real orphan
population is aimed at the test suite's own leavings, which is better fixed at the source.
