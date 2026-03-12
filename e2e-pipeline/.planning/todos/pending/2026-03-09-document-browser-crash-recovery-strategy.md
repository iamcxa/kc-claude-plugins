---
created: 2026-03-09T17:13:15.880Z
title: Document browser crash recovery strategy
area: agents
files:
  - agents/e2e-mapper.md
  - agents/e2e-test-runner.md
  - references/common-patterns.md
---

## Problem

No documented recovery strategy when agent-browser process hangs or crashes mid-execution. Agents have no guidance on detecting this state or recovering gracefully.

## Solution

Add a "Browser Crash Recovery" section to common-patterns.md: detect unresponsive agent-browser (timeout on commands), attempt `agent-browser close` + re-open, save partial results. Reference from both mapper and test-runner agents.
