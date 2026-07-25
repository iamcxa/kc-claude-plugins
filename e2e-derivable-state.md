---
id: t6d92zakbky0gsvpwpfjcd5q
title: Make pipeline state derivable instead of asked
status: backlog
source: captain note — e2e-pipeline agent-native audit, 2026-07-25 (session analysis + agy cross-model review)
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

The pipeline cannot answer "what is stale and what should happen next" without a human.
`skills/e2e-map/SKILL.md` carries 11 ask-the-user points and `skills/e2e-flow/SKILL.md`
6 more; the load-bearing one is the Update Scope Decision, where an existing mapping forces
the skill to ask "re-scan all pages / update one page / start fresh" and explicitly forbids
defaulting. It has to ask because it has no way to compute the answer: mappings carry no
provenance — no source commit, no route-file hashes — so freshness lives only in the
operator's memory. Pre-flight has the same shape: whether agent-browser is installed,
whether `base_url` answers, whether the auth profile exists is re-implemented as inline
bash in four separate skills, and there is no `status` or `doctor` command to ask once.

Shape to decide at ideation: a provenance block on the mapping (source commit plus per-
route-file hashes recorded at map time) and a single `status --json` reporting mappings
with per-page staleness, flows with compiled-artifact staleness, environment pre-flight,
and the last report. `/e2e-map` then proposes an update scope computed from staleness and
asks for confirmation once, instead of asking the operator to choose blind.

## Notes for ideation

- Cheapest of the batch to cut if appetite runs short — it is additive, depends on nothing,
  and its value is ergonomic rather than correctness. Sequence it last for that reason.
- The cross-model reviewer independently proposed the same `doctor --json` surface, arguing
  it from deduplicating the four prose pre-flight snippets rather than from staleness.
  Both motivations point at the same artifact.
- Watch the scope boundary: staleness detection is a mapping-freshness signal, not a
  general-purpose cache-invalidation framework.
