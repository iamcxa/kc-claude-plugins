---
created: 2026-03-09T17:13:15.880Z
title: Handle missing variables block in test-runner
area: agents
files:
  - agents/e2e-test-runner.md
---

## Problem

When a flow YAML uses `${key}` tokens in action strings but the `variables:` block is absent or missing that key, the test-runner's behavior is undefined. Unresolved tokens may be sent as literal strings to agent-browser, causing unpredictable failures.

## Solution

Add variable resolution validation: before executing steps, scan all action/expect strings for `${...}` tokens, check against `variables:` block. Unresolvable tokens → STOP with clear error listing the missing variables. This catches flow authoring errors early.
