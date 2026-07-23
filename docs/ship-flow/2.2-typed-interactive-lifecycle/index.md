---
id: "2.2"
title: "Typed interactive lifecycle"
pattern: shaped-child
parent_pitch: "2"
harvest_required: true
layout: folder
appetite: "3 working days"
affects_ui: false
design_required: true
contract_decision_required: false
domain: schema
depends_on:
  - "2.1"
started: 2026-07-23T02:33:13Z
status: plan
stage_outputs:
  shape: shape.md
  design: design.md
---

### Vertical Slice

Interactive review derives coverage, verdict, and confirmation from typed state with safe legacy fallback.

### Boundary

Limit the default change to interactive `kc-pr-review`. Requiredness is capability-based; a required failure retries once and then produces an explicit incomplete-coverage COMMENT ceiling. Optional failures remain evidence. Human confirmation remains mandatory.

### Done Signal

Typed envelopes are the collator source of truth, exact-head rehydration is enforced, and a kill switch restores legacy behavior. Recall must be non-inferior before stability or efficiency claims; only comparable within-provider reported usage can satisfy the token gate.

### Next

Blocks `2.3-safe-resume-once-only-post` until the typed interactive default passes its empirical evidence gate.
