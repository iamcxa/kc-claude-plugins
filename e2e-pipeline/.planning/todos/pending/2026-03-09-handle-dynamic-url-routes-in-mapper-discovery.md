---
created: 2026-03-09T17:13:15.880Z
title: Handle dynamic URL routes in mapper discovery
area: agents
files:
  - agents/e2e-mapper.md
---

## Problem

Mapper discovery mode encounters dynamic routes like `/items/:id` or `/users/${userId}` from nav links but has no strategy for constructing valid URLs. These routes are either skipped silently or cause navigation failures.

## Solution

Add a "Dynamic Route Handling" section to the mapper agent: detect parameterized URL patterns, skip them in discovery mode, and report them as "unexplored_dynamic_routes" in the summary so the orchestrator can inform the user to provide specific routes.
