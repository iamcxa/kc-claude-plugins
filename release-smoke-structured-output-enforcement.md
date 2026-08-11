---
title: Enforce structured reviewer reports in the release smoke
status: implementation
source: Release PR #202 candidate smoke at ddcd98c884b67513cefe78c704d031fea6472297; captain approved durable schema enforcement
product: kc-dev-flow
sprint: S1
design: trivial-pass
lane: defect
started: 2026-08-11T08:10:00Z
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/structured-output-schema-enforcement
pr: ""
id: azg90gnqthr9tky03z84rxgm
---

The candidate smoke asks both reviewer hosts for a closed report object but relies on prose alone. Claude returned a report with the forbidden `verdict_note` field, so the strict parser correctly rejected an otherwise usable run. Enforce the already-declared report schema at each host CLI boundary while keeping the strict parser and report shape unchanged.

## Bounded known-defect route

- Root cause: `scripts/kc-dev-flow-published-tag-smoke.py:307-365,465-535` extracts free-form host output after a natural-language schema request; the candidate run at `ddcd98c884b67513cefe78c704d031fea6472297` reproducibly reached `validate_report` with an extra `adjudications[0].verdict_note` field.
- Mechanical AC: the existing contract test first rejects a host path without enforced structured output, then passes only when Claude is invoked with `--json-schema`, Codex with `--output-schema`, and both exact CLI envelopes are parsed into the unchanged strict report validator.
- Seam: the existing candidate-smoke producer boundary and its existing contract test; no report fields, validator acceptance, retry policy, release manifest, or published-mode behavior changes.
- Design: `trivial-pass` because the captain selected CLI schema enforcement after the free-form producer failed; stripping fields, retrying, or weakening validation remain explicit non-goals.
- Appetite: one dispatch, 75 minutes with 15 minutes tolerance; stop if the fix requires a third tracked file, a new persisted schema artifact, or any parser relaxation.
