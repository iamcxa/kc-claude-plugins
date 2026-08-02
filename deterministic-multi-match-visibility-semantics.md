---
title: Define deterministic visibility semantics for hidden-first multi-match selectors
status: backlog
source: GitHub issue #91; committed e2e-pipeline/S1 work item
product: e2e-pipeline
sprint: S1
started:
completed:
verdict:
worktree:
issue: "91"
pr:
design:
lane:
id: d3mmhwzpdye4mtg6yc0jvmdz
---

`agent-browser is visible <selector>` can return false when the first matching element is
hidden or zero-sized even though a later match is visibly rendered. The e2e-pipeline paths
currently inherit that ambiguous first-match behavior, so S1 needs one deterministic contract
that keeps parser and invalid-selector errors fail-loud and gives every consumer enough evidence
to distinguish no match, all hidden, one visible, and strict multi-match failure.
