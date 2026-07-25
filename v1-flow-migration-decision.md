---
id: vkf1bkx1cns4x6z0kf6dk8fe
title: Decide whether the un-migrated v1 flows should be migrated, and whether the existing tool is safe to point at them
status: backlog
source: FO finding while gating gz, 2026-07-25 — 90% of the corpus's compile-error mass, and the only thing in sight that could move the clean-compile count
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

`compiler/migrate.js` exists and its header describes exactly the defect that dominates the
corpus: it adds `type:` fields to flow YAML steps. `grep -rn migrate bin/ skills/` returns
zero hits — no CLI subcommand and no skill step reaches it. The tool is unreachable.

Measured on the 100-flow corpus: **565 of 630 resolve errors are `no_type_field`** (90%), and
only 20 flows compile clean. Nothing else currently in the backlog could plausibly move that
20; this could.

This entity is an INVESTIGATION, not a migration run. Three risks make "just run it" wrong:

1. **The tool has an LLM classification step.** Its documented fallback when regex
   classification fails is `claude -p`, skipping on low confidence. A misclassified action
   type produces a flow that compiles and does the wrong thing — the exact silent-failure
   class sprint-1 exists to close. Using a silently-fallible tool to repair silent failures
   needs an argument, not an assumption.
2. **565 errors is not 565 flows.** The per-flow distribution was never measured; the real
   unlock could be a handful of flows with many steps each. Measure before valuing.
3. **The corpus flows live in `carlove`, not this repo.** Migrating them means editing another
   project's files, which is a scope and ownership question before it is a technical one.

Open question to answer first: is the honest deliverable "migrate the corpus", "make the tool
reachable and let owners run it", or "decide the v1 format is dead and say so"? Those are
different tasks with different blast radii.
