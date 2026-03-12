---
created: 2026-03-09T17:13:15.880Z
title: Remove hardcoded plugin install paths from agents
area: agents
files:
  - agents/e2e-mapper.md
  - agents/e2e-test-runner.md
  - agents/e2e-trace-analyzer.md
  - skills/e2e-skill-ops/SKILL.md
---

## Problem

Agents reference `~/.claude/plugins/local/e2e-pipeline/references/commands.md` as hardcoded paths. If plugin is installed via remote marketplace or different directory, these paths break.

## Solution

Use relative paths from the plugin root (e.g., `references/commands.md`) or instruct agents to discover the plugin path dynamically. The plugin framework should resolve paths relative to the plugin installation directory.
