---
created: 2026-03-09T17:13:15.880Z
title: Add trace analysis to e2e-test skill
area: skills
files:
  - skills/e2e-test/SKILL.md
  - agents/e2e-trace-analyzer.md
---

## Problem

e2e-test skill dispatches test-runner which produces trace.zip, but never dispatches e2e-trace-analyzer to analyze it. walkthrough does dispatch it in Phase 4 step 3. This means test runs collect trace data that sits unanalyzed — API failures and console errors from traces are invisible unless user manually runs `--analyze`.

## Solution

Add a Phase 1.75 or integrate into Phase 2: after test-runner returns and before presenting results, dispatch e2e-trace-analyzer with the trace.zip. Include API failures/console errors from trace analysis in the results presentation. This aligns e2e-test behavior with e2e-walkthrough.
