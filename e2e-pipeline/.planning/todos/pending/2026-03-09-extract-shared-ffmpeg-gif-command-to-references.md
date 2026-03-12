---
created: 2026-03-09T17:13:15.880Z
title: Extract shared ffmpeg GIF command to references
area: references
files:
  - skills/e2e-test/SKILL.md:138
  - skills/e2e-walkthrough/SKILL.md:184
  - references/commands.md
---

## Problem

Identical ffmpeg GIF generation command duplicated in e2e-test Phase 1.5 and e2e-walkthrough Phase 4. If the command changes (e.g., framerate, resolution), both files must be updated — risk of drift.

## Solution

Add a "GIF Generation" section to `references/commands.md` with the canonical ffmpeg command. Both skills reference it instead of inlining. Keep a short inline summary (purpose + reference pointer) in each skill.
