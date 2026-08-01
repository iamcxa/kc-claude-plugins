---
id: h9qs5r789jp098jwp3ywyq3e
title: "--app accepts 64 characters but only ~24 can open a browser on macOS"
status: backlog
source: "EM residual on PR #135, 2026-08-01"
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

`assertRunAndApp` in `bin/e2e-browser-runtime.js` accepts an `--app` value up to 64
characters. With the default socket-home shape on macOS, the first session length that
cannot produce a socket-safe namespace is **25** — measured, not derived — so
`namespaceForRun` throws for anything longer.

PR #135 converted that from an opaque agent-browser refusal into a loud runtime error naming
the session, which is the right failure. It did not reconcile the two limits. A caller
reading the validator still believes 64 is allowed.

Open question for ideation: tighten the validator to the reachable range, or lift the
reachable range (a shorter socket home would buy characters back). Not decided here.
