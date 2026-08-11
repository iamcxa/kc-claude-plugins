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
pr: pr-merge:pending:artifact-v1:74a088c7cd05d846b9b26a275e7699af93c3fb5d09cb5bc498649ffc09627a9d
id: azg90gnqthr9tky03z84rxgm
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiW2F6XSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvMTE5MDY4MzY5ZjQ5MTM1N2U1YmI3NDNhNTE3YmNhMjQxZjRlNzA1OC9yZWxlYXNlLXNtb2tlLXN0cnVjdHVyZWQtb3V0cHV0LWVuZm9yY2VtZW50Lm1kKSIsImJhc2UiOiJtYWluIiwiYmFzZV9vaWQiOiIyMTVjNWQ0OGIxMTAzYmJjOWUwOWZjN2ZiNmNlZWM0MDgwMjhlNzY1IiwiYm9keSI6Ik1ha2UgcmVsZWFzZSB2YWxpZGF0aW9uIGRldGVybWluaXN0aWMgYnkgZW5mb3JjaW5nIHRoZSBzYW1lIGNsb3NlZCBFTSByZXBvcnQgc2hhcGUgYXQgYm90aCBDbGF1ZGUgYW5kIENvZGV4IHByb2R1Y2VyIGJvdW5kYXJpZXMuXG5cbiMjIFdoYXQgY2hhbmdlZFxuXG4tIEVuZm9yY2Ugb25lIGNsb3NlZCByZXBvcnQgc2NoZW1hIGZvciBib3RoIGNhbmRpZGF0ZS1yZXZpZXcgaG9zdHMuXG4tIENvbnN1bWUgQ2xhdWRlJ3Mgc2NoZW1hLXZhbGlkYXRlZCBgc3RydWN0dXJlZF9vdXRwdXRgIGV2ZW50LlxuLSBQcmVzZXJ2ZSB0aGUgc3RyaWN0IGZpbmFsIHZhbGlkYXRvciBhbmQgcHVibGlzaGVkLW1vZGUgYmVoYXZpb3IuXG5cbiMjIEV2aWRlbmNlXG5cbi0gMS8xIGNvbnRyYWN0IHN1aXRlIHBhc3NlZDsgNjIvNjIgY2hhbmdlZCBwcm9kdWN0aW9uIGxpbmVzIGV4ZWN1dGVkLlxuLSAyLzIgcmVhbCBpbnN0YWxsZWQgaG9zdHMgcGFzc2VkIHRoZSBleGFjdC1oZWFkIGNhbmRpZGF0ZSBzbW9rZS5cblxuIyMgUmV2aWV3IGd1aWRhbmNlXG5cbkZvY3VzIG9uIGBSRVBPUlRfU0NIRU1BYCBzaGFyaW5nIGFuZCBDbGF1ZGUncyBmYWlsLWNsb3NlZCBlbnZlbG9wZSBleHRyYWN0aW9uLlxuXG4tLS1cblthel0oL2lhbWN4YS9rYy1jbGF1ZGUtcGx1Z2lucy9ibG9iLzExOTA2ODM2OWY0OTEzNTdlNWJiNzQzYTUxN2JjYTI0MWY0ZTcwNTgvcmVsZWFzZS1zbW9rZS1zdHJ1Y3R1cmVkLW91dHB1dC1lbmZvcmNlbWVudC5tZClcbiIsImJvZHlfc2hhMjU2IjoiMzI1Mzg4Nzc4YjljYzE1OTJlZmNkNTg5MTBjMjM5NjQ4NzYyODg0MmRmZmM5YmZmYWEwYjgzNmUxNTIyNmQ1ZCIsImRpZmZfc2hhMjU2IjoiMTdlYzgxNWNiNzIwM2I1NjFlODI3Y2JkYWRlMmVmNTAyYzQ4YzU2Y2U4NTIwMTBhMGU5ZDU0NmU2MzQwYThkNCIsImhlYWQiOiJzcGFjZWRvY2stZW5zaWduL3N0cnVjdHVyZWQtb3V0cHV0LXNjaGVtYS1lbmZvcmNlbWVudCIsImhlYWRfb2lkIjoiNGM4ODkzYmE3NmMwNmQwOWY2NDRjOWQ5YjIxNDBmMjFlMGMzM2Q3ZCIsImxpdmVfcGF0aCI6InJlbGVhc2Utc21va2Utc3RydWN0dXJlZC1vdXRwdXQtZW5mb3JjZW1lbnQubWQiLCJyZXBvIjoiaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zIiwidGl0bGUiOiJmaXgoa2MtZGV2LWZsb3cpOiBlbmZvcmNlIHN0cnVjdHVyZWQgc21va2Ugb3V0cHV0In0
mod-block: pr-merge:product-pr:v1:74a088c7cd05d846b9b26a275e7699af93c3fb5d09cb5bc498649ffc09627a9d
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

Changed-file-to-AC mapping: `scripts/kc-dev-flow-published-tag-smoke.py` is the host enforcement and envelope-consumption seam; `scripts/kc-dev-flow-contract-test.py` supplies the RED/GREEN refusal and shared-schema checks. Raw shape against `215c5d48b1103bbc9e09fc7fb6ceec408028e765` is `+103/-34` and `+72/-0` respectively. The largest added responsibility is the shared closed schema; removing it makes the contract observe missing host schemas and restores nondeterministic free-form production, so the mechanical AC fails. Counts informed the subtraction pass but did not set scope or acceptance; no number-management incident occurred.

## Stage Report: validation

**DECISION: PROCEED** at exact product revision
`4c8893ba76c06d09f644c9d9b2140f21e0c33d7d`.

- DONE: Re-run the mechanical and repository boundary
  Fresh orchestration reran the contract, Python compile, marketplace L0-L2, version parity, 40-file frontmatter lint, and diff check at the clean exact head. The `/tmp/kc-dev-flow-candidate-4c8893b.json` receipt revision, version, and tree were independently compared with the checkout's recomputed package identity; both host results are `PASS`.
- DONE: Challenge fail-closed behavior and scope
  The contract rejects missing host schema flags, a Claude text-only result, the original extra `verdict_note`, malformed reports, and failed host reports without writing a receipt. The diff remains the two AC-mapped files; published mode, report acceptance, retry behavior, and skill content are unchanged.
- DONE: Obtain the one fresh EM verdict
  Fresh safe-mode Claude Opus High session `d4eb4cbf-0228-4ac8-aa79-8a870d87db06` compared base and head with read-only tools and returned `proceed`, `high`, `multi_model: not_needed`, with no Material code finding. It found one non-blocking state-record error: the two per-file numstats were swapped; this report corrects them above without changing product head.

Lenses: behavior PASS (0 Material findings), contract/schema PASS (0), runtime/platform PASS (0), docs/policy PASS after the state-only numstat correction, delivery PASS (0) — read base `215c5d48b1103bbc9e09fc7fb6ceec408028e765`, head `4c8893ba76c06d09f644c9d9b2140f21e0c33d7d`, both changed scripts, the task, selected mods, and validation runbook; removing either host schema flag, restoring Claude text fallback, weakening exact-object rejection, or adding unmapped scope would fail this round.

Diff coverage: PASS — `62/62` coverable changed production lines (100%) were mapped from `git diff --unified=0` and observed by Python `trace --count` while running the full contract; any changed behavior line not executed or a result below the repository threshold would fail this round.

Adversarial: PASS — at exact head, missing Claude/Codex schema flags, Claude text-only output, extra `verdict_note`, and an invalid Codex report each redden the contract; any accepted mutation or written failure receipt would fail this round.

Cross-model: not_needed — the one fresh Opus High EM bound to exact head found no contested, irreversible, low-confidence, or unresolved call; no optional panel was launched.

E2E: PASS — isolated real Claude 2.1.226 and Codex 0.145.0 installs both produced schema-conforming reports through their actual CLI envelopes at exact head; either host failure or missing receipt would fail this round.

Origin re-observation: PASS — Reported scenario: Claude free-form output added forbidden `adjudications[0].verdict_note` | Originating runtime kind: isolated installed-host candidate smoke | Re-observation artifact/revision: `/tmp/kc-dev-flow-candidate-4c8893b.json` at `4c8893ba76c06d09f644c9d9b2140f21e0c33d7d` | Equivalent-runtime rationale: the same installer, Claude/Codex CLI kinds, strict parser, authentication path, prompt, and receipt writer ran with only the producer boundary repaired | Falsifier kind: mutation | Result: both hosts passed the closed schema and final strict validator, and the bound receipt was written.

```yaml
engineering_judgment:
  question: "Does exact head 4c8893ba safely and minimally enforce the existing closed Science Officer report shape at both release-smoke host boundaries without weakening final validation?"
  revision: "4c8893ba76c06d09f644c9d9b2140f21e0c33d7d"
  evidence_synthesis: "Base/head comparison, fail-closed contract mutations, 62/62 changed-line execution, and the real Claude/Codex receipt support the accepted AC; one swapped state-only numstat was corrected."
  adjudications:
    - finding: "One shared closed in-code schema is the smallest sufficient producer shape."
      disposition: supported
      basis: "Both hosts receive one serialization derived from the same field tuples used by the strict parser; separate or tracked schemas add drift without a new guarantee."
    - finding: "The validate_report acceptance set was weakened by its tuple refactor."
      disposition: unsupported
      basis: "Base/head comparison found the same exact keys, errors, ordering, cross-field equality, revision check, and accepted values."
    - finding: "The implementation report swapped per-file numstats."
      disposition: supported
      basis: "Exact numstat is smoke +103/-34 and contract +72/-0; the state record is corrected without changing product head."
    - finding: "Published mode or failed-report receipt behavior regressed."
      disposition: unsupported
      basis: "Published logic is unchanged and the contract still proves zero model invocation and no receipt on failed validation."
  risk_tradeoff: "Deterministic host output adds a dependency on two CLI flags and Claude structured_output; host drift fails closed, while committed or per-host schemas would add a larger maintenance surface."
  recommendation: "Proceed at this exact revision after the state-only numstat correction."
  route: proceed
  confidence: high
  dissent: ""
  disproof_condition: "Either real host rejects its schema form, a successful Claude run lacks structured_output, removing either schema flag leaves the contract green, strict report acceptance changes, or a third tracked file appears."
  authority_boundary: "The captain retains scope and irreversibility; gate and work-item owners retain stage state; delivery owns push, PR, merge, tag, release, and archive."
```
