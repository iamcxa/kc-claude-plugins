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
