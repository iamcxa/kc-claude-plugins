---
title: The journey-map interrogation strangers run with only the tools and context they are meant to have
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the dev2-poc task interrogation-replay-on-batch-3-poc (closed 2026-10-20 on the Captain's 「好，照結果結案」), whose report.md § Isolation audit and arm notes record the finding; FO listed it for filing in that session.
- Bite, recorded there: kc-journey-map's interrogation command runs its Claude stranger with `--tools Read,Grep,Glob` but no `--strict-mcp-config`; a probe with the reference flags still exposed about 200 MCP tools (Notion, Drive, Slack and others) and a 197k-token context to the model, so isolation by `--tools` alone is not real. With `--strict-mcp-config --disable-slash-commands` the tool list was exactly Glob, Grep, Read. Both CLIs also load the user's global instruction files, which the reference invocation does too and the POC did not control.
- Also recorded: the POC pinned Codex with `-m gpt-6.1-sol -c model_reasoning_effort="high"` because the user default is a different model, and the recommendation was Codex with the engineering-reviewer lens by default, plain Codex added where a decision is hard to reverse, and a rank-and-cap step.
- Shape asked for: the interrogation command's stranger invocations carry the isolation flags, and their model and effort are stated rather than inherited.
- Upstream first: kc-journey-map interrogation mode and its CLI wrappers; Claude Code and Codex CLI `--help` for the flags.
- Non-goals: changing the stranger prompts beyond isolation and model choice unless ideation finds the POC's lens recommendation belongs here.

## FO alignment

Alignment: needed at ideation; whether the POC's lens and rank-and-cap recommendation joins this task is the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
