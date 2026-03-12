---
created: 2026-03-09T17:13:15.880Z
title: Resolve dispatch vs leaf skill trigger overlap
area: skills
files:
  - skills/e2e-dispatch/SKILL.md
  - skills/e2e-test/SKILL.md
  - skills/e2e-map/SKILL.md
  - skills/e2e-walkthrough/SKILL.md
  - skills/e2e-skill-ops/SKILL.md
---

## Problem

e2e-dispatch description contains ALL trigger keywords from every leaf skill (e2e-test, e2e-map, e2e-walkthrough, e2e-skill-ops). When user says "e2e test login", both dispatch and e2e-test match equally. LLM skill router has no way to disambiguate, may load the wrong one or load both (wasting context).

## Solution

Options:
A) Remove overlapping triggers from leaf skills, make dispatch the sole entry point
B) Remove overlapping triggers from dispatch, keep leaf skills as primary and dispatch as explicit `/e2e-dispatch` only
C) Add "primary router" marker or priority hint in dispatch description

Option B is likely best — leaf skills are already registered and work directly. Dispatch is a convenience wrapper.
