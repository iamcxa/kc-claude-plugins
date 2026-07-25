---
title: Make the mechanically decidable pre-scans produce evidence no agent authored
status: backlog
source: deferred tier 2 of prescan-coverage-honesty, 2026-07-26 sprint planning
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 1cwdnyhqp91g3yndjfhtrpbx
---

`prescan-coverage-honesty` makes a skipped Step 4.5 pre-scan a visible gap, but the terminal
state is still authored by the agent that ran or skipped the scan, so a fabricated `clean` is
indistinguishable from a real one. Three of the eleven are mechanically decidable and need no
model at all: `4.5f` lint gate, `4.5h` dead export detection, `4.5b` stale reference detection.

Scope: have those three produce their terminal from a script's exit status and output rather
than from the agent's report, so the workflow's proof policy is satisfied — a check counts as
independent evidence only when what it inspects was not authored by the agent under review.

Depends on `prescan-coverage-honesty`, which is expected to fix the evidence payload shape so
this slice fills it rather than bumping the closed schema a second time.

**AC-1 — The terminal for a script-backed pre-scan is derived from the script, and an agent report that contradicts it loses.**
Verified by: a run where the agent reports `clean` while the script finds a violation; the
recorded terminal is `findings`. Falsified by: the agent's claim surviving, or the two being
reconciled by prose.
