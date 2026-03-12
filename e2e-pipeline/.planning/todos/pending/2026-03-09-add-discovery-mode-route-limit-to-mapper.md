---
created: 2026-03-09T17:13:15.880Z
title: Add discovery mode route limit to mapper
area: agents
files:
  - agents/e2e-mapper.md
---

## Problem

When mapper agent enters discovery mode (empty routes list), it follows nav links one level deep with no limit on how many routes to explore. A large app with hundreds of nav links could cause the agent to explore indefinitely, consuming excessive time and context.

## Solution

Add a `max_routes` optional field (default 20) to the mapper agent input contract. In discovery mode, stop exploring after reaching the limit and report remaining unexplored routes in the summary. The orchestrating skill (e2e-map) can pass this through from user args.
