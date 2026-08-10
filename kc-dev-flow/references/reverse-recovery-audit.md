---
name: reverse-recovery-audit
description: "Brownfield shape/plan mindset: assume the abstraction already exists, classify its completeness and its observed need as separate axes, and only greenfield what is confirmed MISSING"
version: 0.2.1
---

# Reverse-Recovery Audit — Assume It Exists, Prove What's Missing

> Plugin-canonical copy. Adopting repositories vendor this file at the adopted
> workflow's `_mods/reverse-recovery-audit.md` and MAY append a
> repo-specific worked example and their own known seam-defect classes.

## Why This Exists

In a brownfield codebase, the default planning instinct — "the feature doesn't
work, so plan to build it" — is systematically wrong and expensive. It
produces duplicate implementations beside broken-but-present ones, misses
one-line wiring fixes disguised as features, and inflates a one-day seam
repair into a multi-day rebuild. Empirically (carlove v1 gap analysis,
2026-07-05): of 71 golden-path capabilities audited, only 6 were truly
MISSING; the dominant states were EXISTS_BROKEN and unproven wiring. The work
was recovery, not construction.

## The Rule

**Before planning ANY capability as new work, run the reverse-recovery audit:
assume the abstraction already exists, hunt for it, classify it with
evidence, surface evidence-backed removal candidates for the scope owner, and
only greenfield what is confirmed MISSING.**

**Completeness and need are separate axes.** The ladder below says how finished
a layer is. It cannot say whether the layer should be there — a surface nothing
consults is `WORKING`, and is thereby protected by the very evidence that
describes it. So every classified layer carries a completeness tier **and** a
need field, and neither substitutes for the other.

### 5-tier completeness classification (evidence ladder)

| Tier | Meaning | Minimum evidence |
|------|---------|------------------|
| `WORKING` | works end-to-end | behavioral E2E (API-level or browser) or a runtime walk — **unit tests alone never qualify** |
| `WORKING_UNIT_UNPROVEN` | logic tested, wiring unproven | unit tests pass, no seam proof |
| `EXISTS_BROKEN` | implemented but fails | concrete defect evidence: broken wiring, contract mismatch, swallowed error/rejection path, failing runtime probe |
| `STUB` | abstraction only | type/contract/route/page skeleton with placeholder logic |
| `MISSING` | no abstraction | exhaustive search came up empty (see below) |

### Need field (recorded beside the tier, never instead of it)

| Value | Meaning | Minimum evidence |
|---|---|---|
| `REQUIRED` | a consumer or an obligation is named | the consumer at file:line, or the rule/contract that requires it |
| `NO_OBSERVED_CONSUMER` | none found inside stated boundaries | two search strategies, **and the boundaries named** — see discipline 3 |
| `UNKNOWN` | not searched, or the boundaries cannot be closed | say which |

`NO_OBSERVED_CONSUMER` is a removal **candidate**, not a verdict. It is the
strongest claim the evidence supports: searches establish what was not found
inside a boundary, never that nothing requires a thing.

### Discipline

1. **Layer-trace before classifying**: UI entry → API contract → handler →
   domain logic → persistence/projection → UI readback. Record file:line per
   layer or the literal `MISSING`. One broken layer ≠ MISSING — it is
   EXISTS_BROKEN at that seam, and the fix is scoped to that seam.
2. **MISSING requires proof of absence, not absence of proof.** Search domain
   nouns in every language the codebase uses, across contracts, routes,
   domain types, and UI surfaces, with at least two search strategies before
   writing MISSING. "Not found after one grep" is the easiest false claim.
3. **A `NO_OBSERVED_CONSUMER` claim names its search boundaries.**
   In-repo callers are the easy half. Also state what was done about external
   repositories, dynamic or reflective references, manual and operational use,
   contractual or compatibility obligations, and dormant paths — searched, out
   of scope, or unknown. A `NO_OBSERVED_CONSUMER` claim that does not say where
   it stopped looking is `UNKNOWN`.
4. **The audit proposes; the scope owner disposes.** Removal is a scope
   decision. The audit records the candidate with its evidence and stops. An
   agent that likes deleting is as dangerous as one that likes adding, and the
   same evidence bar governs both directions.
5. **Sizing follows the decision, not the proposal.** Once a removal is
   accepted, size the increment against the tree that remains. Until then size
   against the tree as it is, or present both as conditional alternatives.
   Sizing against a removal nobody approved plans against a tree that does not
   exist.
6. **Every non-runtime classification carries a `disproof_hook`** — the one
   command or observation that would flip it. The audit stays
   self-correcting instead of authoritative.
7. **Unit tests prove logic, never wiring.** Silent-failure architectures
   (event-sourced rejection-as-event, schema-boundary stripping, CQRS
   projection lag) fail BETWEEN tested units; seam claims need runtime or
   E2E evidence.
8. **Boundary conditions.** Greenfield domains take no search tax — the rule
   is "prove MISSING before building", not "never build". The need field is
   asked of every surface the increment proposes to create, change, or remove,
   and of existing layers the increment will sit on — not of the whole tree or
   of shared foundations the increment merely passes through. And
   cheapest-literal recovery is a scope tool, not an architecture tool: when
   a recovered abstraction fights the domain model, escalate to a redesign
   decision instead of contorting the old shape.

### Where it binds

- **shape stage**: frame the entity around recovered capability + named gaps,
  citing existing abstractions by file:line, not around "build X".
- **plan stage**: every task that creates a new file/domain/route MUST carry
  a classification line justifying why recovery was impossible (MISSING with
  search evidence). Plan reviewers reject greenfield tasks without it.
- **plan stage, need**: a task that creates, changes, or removes a surface, or
  builds on an existing foundation, MUST carry the need field for those
  surfaces and layers. Plan reviewers reject it without one, on the same
  footing as a missing MISSING claim. Without a rejection predicate the field
  is prose an author can decline to write and still pass.
- **any "build/add/implement X" request**: run the audit for the touched
  capability before writing the plan.

### Why need is asked separately

In one adopting repository's session, six changes were made where the rules as
written permitted an addition and the human scope owner chose a removal: a
status file added to hold facts that expire, two pre-existing files nothing
consulted, a stale document given a warning banner rather than deleted, a new
policy file where an existing one had room, and a new token added to a list that
already had a format.

**What that shows and does not show.** Three of the six are arguably reachable
under "prefer the smallest addition" if it is read strictly, so this is not six
gaps. It also does not show that unnecessary surfaces were shipped — a human
caught every one. What it does show is direction: the correction always ran the
same way, and the two pre-existing unconsulted files were never questioned at
all, because no rule asks about a surface no new work is proposing to touch.

The observation that would settle whether this field changed behaviour, rather
than reading well: among comparable brownfield plans, does the rate at which a
scope owner turns a proposed addition into reuse or removal fall? Count first
drafts, not final artifacts. Track removals later reverted alongside it, or the
measure rewards destructive false positives.
