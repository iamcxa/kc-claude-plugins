---
title: Enforce structured reviewer reports in the release smoke
status: validation
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

## Stage Report: implementation

**READY FOR VALIDATION** at exact product revision
`4c8893ba76c06d09f644c9d9b2140f21e0c33d7d`.

- DONE: Reproduce the ungoverned producer boundary before changing it
  RED: the contract failed when neither host received a schema and when Claude extraction selected the free-form `result` carrying forbidden `adjudications[0].verdict_note` instead of a schema-validated object.
- DONE: Enforce one existing report shape at both host boundaries
  `scripts/kc-dev-flow-published-tag-smoke.py` defines one closed in-code schema, passes it through Claude `--json-schema` and Codex `--output-schema`, consumes Claude `structured_output`, and leaves `validate_report` as the final strict authority. There is no retry, field stripping, validator relaxation, persisted schema file, or skill change.
- DONE: Prove the exact implementation head through the real boundary
  Contract, Python compile, marketplace L0-L2, version parity, 40-file frontmatter lint, and `git diff --check` passed on the clean exact head. A real candidate smoke invoked isolated Claude 2.1.226 and Codex 0.145.0 and wrote `/tmp/kc-dev-flow-candidate-4c8893b.json`; both reports passed. The receipt binds revision `4c8893ba76c06d09f644c9d9b2140f21e0c33d7d`, version `2.2.0`, and independently recomputed tree `d2d103cdcf62b514e35883fea9db51b823ca809e8a363d849c2470acf7f32323`.

Changed-file-to-AC mapping: `scripts/kc-dev-flow-published-tag-smoke.py` is the host enforcement and envelope-consumption seam; `scripts/kc-dev-flow-contract-test.py` supplies the RED/GREEN refusal and shared-schema checks. Raw shape against `215c5d48b1103bbc9e09fc7fb6ceec408028e765` is `+72/-0` and `+103/-34` respectively. The largest added responsibility is the shared closed schema; removing it makes the contract observe missing host schemas and restores nondeterministic free-form production, so the mechanical AC fails. Counts informed the subtraction pass but did not set scope or acceptance; no number-management incident occurred.
