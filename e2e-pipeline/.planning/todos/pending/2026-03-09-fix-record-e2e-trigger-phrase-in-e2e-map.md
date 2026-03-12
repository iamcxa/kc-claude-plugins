---
created: 2026-03-09T17:13:15.880Z
title: Fix record-e2e trigger phrase in e2e-map
area: skills
files:
  - skills/e2e-map/SKILL.md:3
---

## Problem

"record e2e" trigger phrase only exists in e2e-map's description. Users saying "record e2e" more commonly mean video recording (e2e-test with --video), not UI mapping. This could cause wrong skill activation.

## Solution

Remove "record e2e" from e2e-map description. The mapping action is better described by "map", "create mapping", "update mapping" — "record" is ambiguous with video recording.
