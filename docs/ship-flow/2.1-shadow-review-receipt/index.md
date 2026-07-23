---
id: "2.1"
title: "Shadow review receipt"
pattern: shaped-child
parent_pitch: "2"
harvest_required: true
layout: folder
appetite: "3 working days"
affects_ui: false
design_required: true
contract_decision_required: false
domain: schema
depends_on: []
status: verify
stage_outputs:
    shape: shape.md
    design: design.md
    plan: plan.md
    execute: execute.md
started: 2026-07-23T01:31:40Z
---

### Vertical Slice

One unchanged interactive review emits a validatable, inspectable exact-head receipt and benchmark baseline.

### Boundary

Observe the existing interactive flow after collator classification. Do not dispatch a second review, change the verdict, alter confirmation, or modify GitHub event/body/comments.

### Done Signal

The receipt binds full repository identity, PR number, base/head SHA, schema/config hashes, lane terminal states, coverage, normalized findings, evidence pointers, and typed usage provenance. Deterministic fixtures and a paired-run corpus establish a trustworthy baseline without claiming token improvement.

### Next

Blocks `2.2-typed-interactive-lifecycle` until exact-head rehydration, recall preservation, complete lane accounting, and external-behavior parity pass.
