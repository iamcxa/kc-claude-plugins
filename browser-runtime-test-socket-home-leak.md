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

Measured on this machine 2026-08-02: **5,111** directories under
`/tmp/e2e-agent-browser-502-*`, oldest dated 2026-07-30, 524K in total. Almost every one
holds a single `namespaces/e2e-run-123/` with no socket.

`socketHomeForBrowserHome` derives the root from a hash of the browser home, so each test
fixture's temporary browser home produces its own root. `run-123` is the fixture run id used
by six files under `compiler/test/` (`browser-runtime.test.js`,
`browser-runtime-ownership.test.js`, `flow-managed-auth-runtime.test.js`,
`local-service-runtime.test.js`, `codegen-status-safety.test.js`,
`trace-finalization.test.js`). The tests remove their fixture browser homes; nothing removes
the socket home the runtime created from them.

Three days of test runs produced 5,111 directories. The byte cost is trivial; the directory
count is not, and it grows without bound on any machine that runs the suite.

Not the same defect as [[browser-runtime-namespace-drift-across-upgrade]] — that one is about
namespaces moving across an upgrade, and its own spike found zero instances. This is the
population that actually exists.
