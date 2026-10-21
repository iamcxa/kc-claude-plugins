Recorded late by FO on 2026-10-21: this record was not saved at dispatch time; its contents are the files and message the dispatch actually used.  Package script names are written with their absolute path in this record; the dispatch as sent used bare names (`adr_lint.py`, `design_surfaces.py`).
Dispatched: from c27e76590c1d2dc910e7fa2d332242a7534df0b0
Model: sonnet

## Checklist

Four arms on the same ~10 hand-written scenarios, each on Claude (sonnet) and Codex (gpt-6.1-sol, reasoning high): no help; skill teaching plain `git show` + `shasum` + reading the Status line; skill + the preview CLI; skill + CLI + a session-start hook listing ruling titles. Expected answers committed before the first run. About 80 runs declared; stop if the count would pass +20%.
A results table per arm and host: consulted the governing ruling before deciding; handoff version and digest matched; new information placed in the home the routing table names. Each cell traces to recorded tool calls and outputs, and the harness re-runs from its README.
The Amendment 1 decision rule applied in the report: does the CLI arm clearly beat the plain-git arm on those measures? Also state what the result does not prove, and which routing rows agents got wrong most.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc (shared; touch only this task's file and folder).
Read the task's `## Captain amendments` first: Amendment 1 sets the start now, four arms, about 80 runs, and the decision rule.
CLI under test: the ideation preview at /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/kc-decision-log-cli/preview/ (cli.mjs, fixture.mjs, README.md; read only — copy it into your harness, do not edit it). Its design and command surface are in the same state checkout's kc-decision-log-cli.md "## Design".
Routing rule under test: docs/journey/kc-decision-log/boundary-contract.md on branch origin/docs/kc-decision-log-boundary (PR #691), section 「什麼寫進哪裡」.
Fictional data only. Do not read or copy the Captain's private decision repository's real records.
Run agents headless: `claude -p --model sonnet ...` and `codex exec -m gpt-6.1-sol -c model_reasoning_effort="high" ...`. Check flags with `--help` first and record the exact argv per run. Tell the FO before exceeding the declared run count.
The skills and the hook are disposable POC harness pieces, not the shipped `read-adr` skill, S30, or dev2's `agent-reads-governing-adr` hook. Keep the harness and results in this task's state folder unless the implementation principles require otherwise.
roborev not run: FO omitted the roborev instruction at this dispatch; the candidate worktree has no diff (the harness lives in the state folder), so there was nothing to review.
