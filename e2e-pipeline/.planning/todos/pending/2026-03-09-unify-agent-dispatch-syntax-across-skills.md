---
created: 2026-03-09T17:13:15.880Z
title: Unify agent dispatch syntax across skills
area: skills
files:
  - skills/e2e-map/SKILL.md:115
  - skills/e2e-test/SKILL.md:117
  - skills/e2e-dispatch/SKILL.md:96
---

## Problem

e2e-map uses `Agent(e2e-mapper):` while e2e-test and e2e-dispatch use `Agent(subagent_type="e2e-test-runner")`. Inconsistent syntax could confuse agents about the canonical dispatch format.

## Solution

Standardize all dispatch sites to `Agent(subagent_type="<name>")` format, matching the Claude Code Agent tool's actual parameter name.
