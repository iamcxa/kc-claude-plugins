---
title: Nothing checks that a test's stub matches the collaborator it replaces
status: backlog
source: maintainer feedback from a live kc-pr-review run on DataRecce/recce-cloud-infra #1596, received 2026-07-27 (kc-pr-flow 1.9.1)
design:
id: x0r4sgxg66w21egfngz2sq1e
---

A reviewer running this kit on a backend bugfix found seven real defects. The most important one
was found by **an agent reading two layers**, not by any pre-scan — and it is mechanically
detectable, which is what makes it a gap rather than a limitation.

The PR added a five-arm HTTP status mapping to two endpoints. It was **dead code in production**:
the client methods those endpoints call raised the error object without ever setting the
`status_code` field the mapping branches on. Every failure arrived unclassified, and a genuinely
missing resource regressed from a correct 404 to a 502 — the change made the common case worse
while appearing to fix the rare one.

The endpoint tests could not catch it *by construction*, because the test patched the whole
collaborator and then asserted the stub's own behaviour:

```python
@patch("api_server.apis.gitlab_api.GitLabClient")
mock_client.list_merge_requests.side_effect = GitLabAPIError("...", status_code=404)
self.assertEqual(response.status_code, 404)   # passes
```

The stub asserts the collaborator's contract and nothing verifies that assertion. The real
`list_merge_requests` contained no `status_code=` anywhere. What did not catch it: a green
5600-test suite, `mypy`, `ruff`, and a passing mutation-test round.

This is the fourth cell of a matrix the §4.5 family already covers three quarters of — verified
against `skills/kc-pr-review/SKILL.md` at 1.9.1:

| Check | Verifies | Exists |
|---|---|---|
| §4.5i (`:622`) | code helper rollout is complete across the repo | yes |
| §4.5j (`:651`) | doc claims are grounded in the code they describe | yes |
| §4.5k | doc rules are consistent with doc examples | yes |
| **§4.5x (proposed)** | **test stubs are consistent with the real collaborator** | **missing** |

Like the others it is pure grep, zero LLM tokens.

## Sequencing

Cut this **after `2t` (prescan-coverage-honesty)**. `2t` decides how a pre-scan reports coverage
and how its evidence payload is shaped; adding a twelfth pre-scan before that representation
exists means designing against a shape that is about to change, and `1c` already has to fill the
same payload. This entity is also the strongest argument for `2t`: a check that is a prose
instruction to grep is indistinguishable from one nobody ran, and this defect class is exactly
what a skipped grep looks like.

## Proposed detection, from the reporter (not yet independently validated here)

Activate when the diff adds or modifies a test that patches a class or module-level symbol
(`@patch("mod.ClassName")`, `patch.object`, `vi.mock`, `jest.mock`) **and** stubs a return value
or raised exception constructed with keyword fields.

1. From `git diff --unified=0`, find added patch decorators in test files; extract the target.
2. In the same test body find `<mock>.<attr>.side_effect =` / `.return_value =` assignments.
3. Extract keyword arguments from the constructed value. Skip stubs with none.
4. Resolve the patched target to its real module and `git grep -n "<keyword>"` there.
5. Zero occurrences in the real module → MEDIUM, source `PRESCAN`. Occurrences outside `<attr>`'s
   body → LOW (a shared helper may set it).

False-positive filters the reporter names: skip unresolvable third-party symbols, skip `**kwargs`
forwarding, skip test-only fixture factories. Whole-module grep is an acceptable
over-approximation — it yields false negatives, never false positives.

Companion for cases grep cannot reach, proposed for the `pr-test-analyzer` dispatch prompt (§4f):
"For every collaborator the tests patch wholesale, state explicitly whether the real collaborator
can produce the stubbed shape. If it cannot, that is a finding regardless of test results."

## What still needs deciding at ideation

The reporter's spec is Python-shaped (`@patch`, keyword arguments). This kit reviews TypeScript and
shell repos too, and `vi.mock`/`jest.mock` stubs are usually object literals rather than keyword
constructions. Whether §4.5x ships Python-only with an explicit scope note, or generalises, is the
open design question — a check that silently does nothing on a TS repo is precisely the failure
`2t` exists to make visible.

**AC-1 — A test that stubs a collaborator with a keyword field the real collaborator never sets produces a finding before the confirmation gate.**
Verified by: a fixture pair (test stubbing `status_code=`, real module without it) driven through the pre-scan, asserting a MEDIUM `PRESCAN` finding naming both sites. Falsified by: the fixture producing no finding, or the check reporting clean on a repo whose language it cannot parse.
