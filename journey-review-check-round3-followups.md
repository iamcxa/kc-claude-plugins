---
title: journey-review check and the map lint refuse the three inputs Codex round 3 named on PR #704
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: Codex round 3 on iamcxa/kc-claude-plugins#704 head f0d3f442 (review:5612786931), declined in new-work-starts-from-a-story-map's merge ask under workflow.md findings step 5 (from round 3 a finding that is neither Material nor P1 is declined and filed as a new backlog task), on chief-engineer advice 2026-10-22 recorded in that task.
- Findings: comment:4347244844 an `Interrogation:` date such as 2026-13-45 passes kc-journey-map/lib/journey-review.mjs check (reuse its isoDay helper); comment:4347244848 a release-sourced ruling without `status: answered` passes; comment:4347244851 two questions with one id in a story make the Carries lookup resolve the first.
- Also (Codex round 3 on iamcxa/kc-claude-plugins#705, review:5623291232, comment:4355580158): the kc-dev-flow-2/scripts/pr_watch.py sitting next: line tells FO to list each open decision and ask one at a time but names no cap, while ADR 0029 caps a release-preparation sitting at 10 questions.
- Shape noted by the chief-engineer, not ruled: the status and duplicate-id rules are map rules and belong in kc-journey-map/lib/lint.mjs (beside lintQuestionStatus), which every mode reads; model.mjs treats a question as answered by answer:/doc:, not by status.
- Bite: none observed; each needs a hand-written malformed record or map.
- Non-goals: a schema-based record parse; the Tasks-table completeness rule (a Captain change to AC-13).

## FO alignment

Alignment: not needed before ideation; the findings and their home are stated above.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
