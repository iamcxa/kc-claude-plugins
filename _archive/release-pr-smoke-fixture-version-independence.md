---
title: Keep the release smoke fixture version-independent
status: done
source: Release PR #202 required-check failure after #203 merged; captain authorized continuing through release
product: kc-dev-flow
sprint: S1
design: trivial-pass
lane: defect
started: 2026-08-11T07:39:56Z
worktree:
pr: pr-merge:204:artifact-v1:e178998d6345ee40412412698ce0b3d5596f3d97a83a4e14df449db19f71db9e
id: 0bk09wbq8j7y6fec41ptg9kk
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiWzBiXSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvMDk2OTk1YWZhZGZkZDEyY2MyNjQ2OTFiZWFjMTY4MzQ5OGZkOTcwNS9yZWxlYXNlLXByLXNtb2tlLWZpeHR1cmUtdmVyc2lvbi1pbmRlcGVuZGVuY2UubWQpIiwiYmFzZSI6Im1haW4iLCJiYXNlX29pZCI6IjUzZTMyMzJkNjFkNjg5ZDM0YTZjNDkzNDk1Yzc5MWZlMGQwZjg1YjQiLCJib2R5IjoiS2VlcCBSZWxlYXNlIFBSIHZhbGlkYXRpb24gaW5kZXBlbmRlbnQgb2YgdGhlIHByZXZpb3VzbHkgcHVibGlzaGVkIGtjLWRldi1mbG93IHZlcnNpb24uXG5cbiMjIFdoYXQgY2hhbmdlZFxuXG4tIERlcml2ZSB0aGUgZmFrZSBwdWJsaXNoZWQgdGFnIGZyb20gbWFuaWZlc3RzIHVuZGVyIHRlc3QuXG4tIFByZXNlcnZlIGFsbCBmaXZlIHB1Ymxpc2hlZCBpZGVudGl0eSBmYWxzaWZpZXJzLlxuXG4jIyBFdmlkZW5jZVxuXG4tIDIvMiB2ZXJzaW9uIGNvbnRleHRzIHBhc3NlZCBjb250cmFjdCB0ZXN0cy5cbi0gNS81IGlkZW50aXR5IGZhbHNpZmllcnMgcmVqZWN0ZWQ7IE9wdXMgSGlnaCBmb3VuZCAwIE1hdGVyaWFsIGlzc3Vlcy5cblxuLS0tXG5bMGJdKC9pYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMvYmxvYi8wOTY5OTVhZmFkZmRkMTJjYzI2NDY5MWJlYWMxNjgzNDk4ZmQ5NzA1L3JlbGVhc2UtcHItc21va2UtZml4dHVyZS12ZXJzaW9uLWluZGVwZW5kZW5jZS5tZClcbiIsImJvZHlfc2hhMjU2IjoiMzI1MDdjM2MwM2M1OTAwZTVhNmQyMmFjZTMxZmMzNTJlZWE1MWZhZWM0ZTQyZDY5NjBiN2Y1MmNjMjk4MDQyZSIsImRpZmZfc2hhMjU2IjoiZjRhMjRhNmU4NWVlZjQxMzQ1OWIwYzM1YzVhMWJjOWNjYmUzZGE3MzdkNDMwNWI4YzQ2MGE5N2JiNzY0ZDNmYyIsImhlYWQiOiJzcGFjZWRvY2stZW5zaWduL3JlbGVhc2UtcHItc21va2UtZml4dHVyZS1maXgiLCJoZWFkX29pZCI6IjVlNWM1ZjY0NmEyY2E0MDExMjFiMzllZWFjMjYyOGRlNjg1ZWI1MWYiLCJsaXZlX3BhdGgiOiJyZWxlYXNlLXByLXNtb2tlLWZpeHR1cmUtdmVyc2lvbi1pbmRlcGVuZGVuY2UubWQiLCJyZXBvIjoiaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zIiwidGl0bGUiOiJmaXgoa2MtZGV2LWZsb3cpOiBrZWVwIHJlbGVhc2Ugc21va2UgZml4dHVyZSB2ZXJzaW9uLWluZGVwZW5kZW50In0
mod-block:
completed: 2026-08-11T07:56:30Z
verdict: PASSED
archived: 2026-08-11T09:17:41Z
---

The published-mode contract fixture hard-codes `kc-dev-flow-v2.2.0`, so a correctly version-bumped Release PR fails before exercising its identity falsifiers. Derive fixture identity from the manifests under test while leaving the production smoke and its strict published-tag checks unchanged.

## Bounded known-defect route

- Root cause: `scripts/kc-dev-flow-contract-test.py:107,220,432-474` injects the `2.2.0` literal into an otherwise version-derived candidate receipt.
- Mechanical AC: the contract test fails in a parity-clean simulated `2.3.0` Release PR tree before the change and passes afterward.
- Seam: one deterministic fake-runtime fixture in one existing file; no production, schema, host, or release configuration change.
- Design: no choice remains after the failure is reproduced; the tested manifests are the single compatible source of fixture version identity.
- Appetite: one dispatch, 20 minutes with 10 minutes tolerance; stop on a second file or any production-smoke change.

## Stage Report: implementation

- DONE: Reproduce the release-version mismatch before changing the fixture
  RED: a parity-clean simulated `2.3.0` tree exited 1 with `published tag version differs from manifests: 2.2.0 != 2.3.0` before source and installed-tree falsifiers could run.
- DONE: Make the fixture version-independent at the bounded seam
  `scripts/kc-dev-flow-contract-test.py` maps to the Mechanical AC and one-file seam: commit `5e5c5f646a2ca401121b39eeac2628de685eb51f`, `+10/-9`, derives the tag from tested manifests, and preserves tag, version, source, Claude-tree, and Codex-tree falsifiers; production smoke is unchanged.
- DONE: Verify the exact implementation head and prepare fresh validation
  Current-tree and simulated-`2.3.0` contracts, marketplace L0/L1/L2, version parity, 40-file frontmatter lint, and diff check passed; the product worktree was clean at the exact head.

### Summary

The smallest sufficient change touched one existing fixture file and left production release identity enforcement intact. Without it, every future version-bumped Release PR would fail on the stale fixture tag before exercising the five intended falsifiers.

## Stage Report: validation

**DECISION: PROCEED** at exact product revision
`5e5c5f646a2ca401121b39eeac2628de685eb51f`.

- DONE: Re-run the mechanical acceptance boundary
  `scripts/kc-dev-flow-contract-test.py` passed on the parity-clean current
  `2.2.0` tree and on an independently prepared parity-clean simulated `2.3.0`
  tree; the latter derived `kc-dev-flow-v2.3.0` from the manifests under test.
- DONE: Challenge the five published-identity falsifiers and the review flip condition
  Tag, version, source tree, Claude installed tree, and Codex installed tree each
  returned `rejected`. The requested `smoke_tag` matches `TAG_PATTERN`; fake
  observed `smoke_tag-other` does not, and production lines 580-584 compare that
  observed value directly, so the tag case fails for the intended `resolved`
  mismatch rather than argument parsing.
- DONE: Close exact-head repository, review, and scope gates
  Marketplace L0/L1/L2, version parity, 40-file skill-frontmatter lint,
  `git diff --check`, clean-worktree, one-file scope, and 100% executable
  changed-line coverage (10/10 under `trace`) passed. Fresh Opus High session
  `2c1831fc-7cde-4a43-b241-224bd30db2f1` returned `PROCEED` with no Material
  finding at the same head.

Lenses: correctness PASS (0 findings) and silent-failure PASS (0 findings) — read exact head `5e5c5f646a2ca401121b39eeac2628de685eb51f`, `scripts/kc-dev-flow-contract-test.py`; either a non-manifest-derived requested tag or any accepted identity falsifier would fail this round. Security, type-design, concurrency, resource-lifecycle, and manifest/back-compat did not fire because the diff changes one deterministic test fixture and no production, type, async, resource, manifest, or installed contract.

Diff coverage: PASS — exact head `5e5c5f646a2ca401121b39eeac2628de685eb51f`, `scripts/kc-dev-flow-contract-test.py`, 10/10 changed executable lines observed by Python `trace` (100%); any changed executable line not reached, or a result below 85%, would fail this round.

Adversarial: PASS — exact head `5e5c5f646a2ca401121b39eeac2628de685eb51f`, `scripts/kc-dev-flow-contract-test.py`; tag, version, source, Claude-tree, and Codex-tree mutations all reddened independently, and acceptance or model invocation in any case would fail this round.

Cross-model: PASS — fresh Opus High session `2c1831fc-7cde-4a43-b241-224bd30db2f1` read the exact one-file diff at `5e5c5f646a2ca401121b39eeac2628de685eb51f` and returned `PROCEED` / no Material findings; a valid requested tag being rejected before the fake observed tag reached lines 580-584 would flip that judgment.

E2E: N/A — ideation bounded acceptance to the deterministic fake-runtime contract and declared no user-facing or external-runtime journey; the Release PR boundary is re-observed below.

Origin re-observation: PASS — Reported scenario: a correctly version-bumped Release PR fails on the stale fixture tag | Originating runtime kind: required CI contract check | Re-observation artifact/revision: parity-clean simulated `2.3.0` tree at `5e5c5f646a2ca401121b39eeac2628de685eb51f` | Equivalent-runtime rationale: the same contract script, manifests, release parity, fake runtime, and identity assertions ran with only the release-owned version fields advanced | Falsifier kind: mutation | Result: the contract passed and all five identity mutations still rejected.

### Risk, change shape, and recommendation

Residual risk is limited to future changes in production smoke identity semantics;
the unchanged production file and the contract's five mutations keep that visible.
The shape is irreducible at this seam: one existing fixture file, `+10/-9`, replaces
nine stale literals with one manifest-derived identity. Removing that binding
reintroduces a version literal, duplicates derivation, or couples later cases to
an unrelated parser result. Proceed to the existing delivery gate; this advisory
record grants no push, PR, merge, release, or task-transition authority.

```yaml
engineering_judgment:
  question: "Does the exact-head fixture fix close Release PR version drift without weakening published identity checks?"
  revision: "5e5c5f646a2ca401121b39eeac2628de685eb51f"
  evidence_synthesis: "Current 2.2.0 and simulated 2.3.0 contracts pass; five identity mutations reject; required repository checks and 10/10 changed-line execution pass; production smoke is unchanged."
  adjudications:
    - finding: "Opus flip condition could be satisfied by tag parsing rather than the intended observed-tag mismatch"
      disposition: unsupported
      basis: "The requested derived tag matches TAG_PATTERN, fake observed tag does not enter argument validation, and run_published_smoke compares it directly at lines 580-584."
  risk_tradeoff: "One manifest-derived fixture identity removes perpetual release-version failures while preserving all production checks; the alternative is a stale literal or broader coupling."
  recommendation: "Proceed to the existing delivery gate."
  route: proceed
  confidence: high
  dissent: ""
  disproof_condition: "Any parity-clean future version fails before the five falsifiers, any falsifier accepts, or production smoke differs from the reviewed base."
  authority_boundary: "The validation gate and captain retain transition, PR, merge, release, and scope authority."
```
