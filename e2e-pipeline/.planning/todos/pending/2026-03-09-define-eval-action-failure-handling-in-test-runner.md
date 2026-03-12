---
created: 2026-03-09T17:13:15.880Z
title: Define Eval action failure handling in test-runner
area: agents
files:
  - agents/e2e-test-runner.md
---

## Problem

Flow steps using `Eval '<js>'` action have undefined behavior when the JavaScript throws an exception. The test-runner agent may silently fail or crash without proper error capture.

## Solution

Add Eval error handling to the test-runner's per-step execution: catch JS exceptions from `agent-browser eval`, mark step as FAIL with the error message, take a screenshot, and continue to next step (same as other step failures).
