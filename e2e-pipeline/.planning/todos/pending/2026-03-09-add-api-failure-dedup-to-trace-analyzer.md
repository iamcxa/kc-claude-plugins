---
created: 2026-03-09T17:13:15.880Z
title: Add API failure dedup to trace-analyzer
area: agents
files:
  - agents/e2e-trace-analyzer.md
---

## Problem

trace-analyzer counts each API failure individually — same endpoint failing 100 times = 100 entries (capped at 20 displayed). The `api_failures` count can be misleading, making one flaky endpoint look like a systemic issue.

## Solution

Group API failures by method+URL+status. Report unique failures with occurrence counts. E.g., "POST /api/items 500 (×47)" instead of 47 separate entries. Update both the report format and the `api_failures` count to reflect unique failures.
