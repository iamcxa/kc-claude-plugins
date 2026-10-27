# 0041. Seed admission enforces the three explicit bounds for new tasks

Date: 2026-10-27

## Status

Accepted

## Context

The Relay task room-specs-follow-web-part-select lacked Budget and Stop condition
yet passed the package's seed check. The workflow also required stored id although
Spacedock's slug identity route omits it. The original design proposed five
frontmatter fields and explicit body bounds; the Captain narrowed that design.

## Decision

**Words:** 「其他全照建議」 — Captain, 2026-10-27, chat; recorded in the task's
ideation gate and Captain amendment 1, answering the batch-8 proposal to follow
the chief engineer's recommendations. This task's row proposed optional stored id,
the three required bounds, and checking new tasks only.

**Options considered:**
- require Non-goals, Budget and Stop condition for newly admitted seeds; stored
  id optional under id-style: slug; report historical replay counts without
  enforcement or migration (chosen)
- enforce the original five frontmatter fields including stored id, and Scope,
  on historical replay too — not chosen: the Captain narrowed the design
- retain the alignment-only seed check — not chosen: it misses the observed bounds

**Recommended:** the narrowed first option, as accepted by the Captain.

**Protects:**
- `kc-dev-flow-2/scripts/design_surfaces.py` — check_seed_fields and its seed-only call

The package seed check requires non-empty Non-goals, Budget and Stop condition
records as Scope labels or dedicated level-two sections, ignoring fenced examples
and unfilled placeholders. It adds no frontmatter or Scope requirement. FO applies
the check before admitting new tasks; default check remains the design check.
Historical replay diagnoses current compatibility, not past operator fault without
the event-time schema. No upstream creation hook or automatic migration is added.

## Consequences

New seeds missing bounds are refused before their backlog gate when FO runs the
existing check. Skipping that step still bypasses the refusal. A seed passes on
presence, not adequacy or Captain approval; an old seed replay can fail without
requiring any existing task to change. Reopen if a supported admission path needs
different required records or an upstream hook.
