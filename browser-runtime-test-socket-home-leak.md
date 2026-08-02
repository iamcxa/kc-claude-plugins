---
id: g2wzybys88ygg58yjvbqy972
title: "The test suite leaks a socket-home directory per fixture and never reaps them"
status: backlog
source: "spike on browser-runtime-namespace-drift-across-upgrade, 2026-08-02"
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

Full census on this machine, 2026-08-02: **5,111** directories under
`/tmp/e2e-agent-browser-502-*`. Of those, **4,983 (97.4%) are completely empty** and 128 hold
a `namespaces/` directory — mostly `e2e-run-123`, the fixture run id used by six files under
`compiler/test/`.

**The empty majority is the finding, and it relocates the fix.** An empty root means
`cleanupClosedNamespaceState` (`e2e-browser-runtime.js:1924-1961`) *succeeded*: it removed
`namespaces/<ns>/run` and then `namespaces/<ns>`, tolerating ENOTEMPTY at each step. It simply
stops two rungs short — nothing removes `<socketHome>/namespaces`, and nothing removes the
socket home itself. `socketHomeForBrowserHome` derives that root from a hash of the browser
home, so every test fixture's temporary browser home mints one.

So the repair is two more rungs on an existing ladder, at one site, in the pattern already
there — not six test-file teardowns. The 128 roots that still hold a namespace are a smaller
second population where `close` never ran at all.

**Bounded severity.** An earlier version of this seed said it "grows without bound on any
machine that runs the suite". That is false here: the age histogram is 1970 / 692 / 1992 / 457
for 07-30 through 08-02 — a hard floor at three days with a *full* oldest bucket, which is a
reaper horizon, not an origin. `/System/Library/LaunchDaemons/com.apple.tmp_cleaner.plist`
runs daily on this machine. Steady state is roughly three days of test runs, about 5K empty
directories and 524K. Linux and CI tmp policy is unverified, so "unbounded" is unknown there
rather than established.

**Shared design constraint.** This and
[[browser-runtime-namespace-drift-across-upgrade]] are two symptoms of one absent mechanism:
the runtime removes only state it can address by an exactly recomputed path. "Extend the
ladder" and "enumerate and sweep" are competing designs for that mechanism and must not be
decided twice independently.
