---
session-date: 2026-08-20
sequence: 1
first-commit: 141d3156
last-commit: f9875565
duration: ~7h
---

# Session Debrief — 2026-08-20 #1

One theme, arrived at sideways: three separate mechanisms in this repository looked healthy
and did nothing. A README fact-check turned into an archaeology of a dead improvement loop,
which turned into building and measuring its replacement, which turned into finding that the
vendored mod governing delivery was fifteen versions behind. Three PRs landed; one built
capability was measured and deleted rather than shipped.

## Shipped

- **r9** `improvement-loop-never-ran` — [#260](https://github.com/iamcxa/kc-claude-plugins/pull/260). The adopter-to-source improvement loop had never run in either direction; retired 1035 lines and gave the retirement its own enforcement point. `done` / PASSED / archived.
- **jp** `digest-effect-unmeasured` — archived on a `local-merge:` sentinel, no delivery artifact. Its Step 0 kill switch fired: zero measurable headroom, verdict "do not ship."
- Also merged this session: [#257](https://github.com/iamcxa/kc-claude-plugins/pull/257) (README trimmed to current behavior, contract-test assertions retargeted, adopt step 9 no longer forces an adopter to vendor a test) and [#261](https://github.com/iamcxa/kc-claude-plugins/pull/261) (pr-merge sentinel port).

## Filed (backlog)

- **jp** `digest-effect-unmeasured` — measure whether the recent-failure digest changes agent behavior. Shipped and closed same session.
- **ge** `knowledge-output-cannot-terminalize` — work whose output is knowledge has no terminal path. Defect 1 retracted after refit; defect 2 confirmed on 0.27.0-pre8.
- **pp** `pr-merge-extension-rule-by-rule` — measure the vendored extension one rule at a time and cut what has no headroom.

## Non-PR commits (workflow-only)

Eighteen state-branch commits, almost all ordinary entity lifecycle. Three worth naming:

- `a42c8e02` The first recent-failure digest this mechanism has ever produced — 12 entries from four real debrief records. Measured, then not shipped.
- `8e6c0704` Retraction of defect 1 after checking the scaffolding version instead of filing upstream.
- `65ee3401` Partial port of the 0.27 sentinel path plus the extension audit that was later itself overturned.

All other session commits are rolled up in the shipped PRs above.

## Decisions

- **Retire the improvement transport rather than repair its pointers.** Four broken pointers were an afternoon's work, but every one of them presupposed keeping the mechanism. Repairing them first would have converted a keep-or-retire decision into an implementation detail, in the direction that costs more.
- **Do not ship the recent-failure digest.** The branch was built, gated, and green. It was deleted on a measurement, not an argument: 53 of 54 informative baseline runs already applied the checks it would have carried.
- **Partial port over full refit on `pr-merge.md`.** The full refit is a three-way merge that has to preserve an enforced local delivery contract; the three hunks that unblock a real refusal are separable and were sent alone.
- **The version stamp stays 0.12.3.** Stamping 0.27.0 on a partial port would make the next refit skip the remaining hunks — the same drift-by-false-claim that produced the defect.
- **Measure the extension rule by rule.** Two wholesale judgments about the same file were already wrong in opposite directions; the unit of decision is one rule.

## Issues — Workflow

- The vendored `pr-merge.md` was fifteen versions behind and **prescribed a terminalization procedure the current binary refuses**. An agent following it reaches a refusal with nowhere to go. Partially ported in #261; the rest is tracked.
- `profile-spacedock-route.test.py` is red on this machine and equally red on unmodified `main`. It is green in CI only because `spacedock` is not installed there, so the test never runs. Not filed — it belongs with the rule-by-rule task's third open question.
- The kc-dev-flow contract test pins prose, not behavior. Three separate checks passed for the wrong reason during this session (see Observations).

## Issues — Spacedock

- **`merge guard` misreports and clears an armed `mod-block` when `pr` is empty.** Observed: `mod-block: merge:pr-merge` present, guard reports "mod-block is empty," field is empty afterward, and the remediation text instructs setting exactly the field it destroyed. Each invocation destroys the state the next one demands. Reproduced on 0.27.0-pre8 with a throwaway entity. **Not filed** — awaiting captain approval.
- **`--archive` and `merge guard` disagree about the `local-merge:` sentinel.** The same value archived successfully through one path and was read as a pending PR by the other. **Not filed** — awaiting captain approval.

## Observations

1. **Three mechanisms, one disease.** The improvement transport (1033 lines, never executed), the recent-failure digest (12 real lessons, zero measured headroom), and `profile-spacedock-route.test.py` (green in CI because it never runs there) fail differently and identically: something guards the *shape* and nothing checks the *effect*. This repository is good at adding prose and then adding checks that the prose is still present.

2. **Every conclusion I reasoned to was wrong; every one I measured held.** Three retractions in one session — "knowledge work has no terminal path" (it did, documented in a mod fifteen versions newer), "238 lines are a redundant back-port" (deleting them failed 13 assertions), "a passing contract test means the rules earn their place" (it pins prose). Each was overturned by a single command. The pattern is not carelessness; it is that reading produces confident conclusions and measuring produces correct ones, and they feel the same from the inside.

3. **Absent output plus present input is the cheap fingerprint.** Four `_debriefs/` records with no `_improvements/` directory answered keep-or-retire before any repair work started. One `ls`.

4. **A hand back-port of an unreleased version becomes silent debt.** 238 lines of `0.27.0-pre3` content sat in a file stamped `0.12.2`, and nothing anywhere said so. The release landing is the moment the back-port becomes stale, and there is no event for it.

5. **Checks passing for the wrong reason happened three times.** A did-work guard grepped a word that appears in the fixture's own type declaration; two probes were reverse-polarity so a no-op scored PASS; a mutation proof fired the wrong assertion twice. Two guards per check, and assert the reason rather than the outcome token.

6. **Blind authoring works and is cheap.** Probes written by a separate model from the raw records — with the artifact under test withheld — surfaced two failure classes my own twelve-entry curation had dropped, one of them the highest-headroom candidate. Hand-curation is not what an independent reader extracts from the same source.

## Agent Testimonial

- Date: 2026-08-20
- Harness/runtime: Claude Code
- Model: Claude Opus 5 (1M context)
- Model version/build: claude-opus-5[1m]
- Session scale: 4 tasks touched; 2 workers dispatched; 3 PRs touched/merged

Spacedock earned its place here in a specific way: it refused three terminal actions I was
about to take, and each refusal named the ceremony step I had skipped. Without it I would have
marked work done on an unmerged branch at least once.

The friction was equally specific. `merge guard`'s livelock cost four rounds before I stopped
re-running it and read the binary's strings instead — the circuit breaker should have fired on
round two. The `--set` field-combination rules (a `mod-block` clear cannot ride along with a
terminal field) took two failures to parse, because the error names the constraint without
naming which of my fields triggered it. And resolving the debrief home was only reliable via
`status --boot --json`; inferring it from the README's `state:` key would have put this file on
the wrong branch.

One thing the workflow does not model: an entity whose accepted output is knowledge. That is
now tracked, and the escape (`pr=local-merge:{reason}`) exists — but it was invisible for a
whole session because the vendored prose describing it was fifteen versions old.

## What's Next

**Dispatchable:**

- **pp** `pr-merge-extension-rule-by-rule` — the method is proven and the first four numbers are in the entity.
- **ge** `knowledge-output-cannot-terminalize` — defect 2 is reproduced and narrowed; the remaining work is an upstream issue plus the `--archive` / `merge guard` sentinel disagreement.
- **bz** `delivery-topology-review-deduplication` — untouched, predates this session.

**Blocked on the captain:**

- Release PR **#258** is open and includes kc-dev-flow. The release-boundary smoke (`kc-dev-flow-published-tag-smoke.py candidate`) has not been run and is required before merge.
- Both Spacedock defects above are drafted but unfiled; filing is an outward action.
