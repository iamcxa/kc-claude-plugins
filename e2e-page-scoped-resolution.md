---
title: Make the page qualifier bind, or drop it from the grammar
status: backlog
source: sprint-1 (compiler boundary) entity 3 of 5; split out of e2e-typed-operands so the sprint stays inside the compiler
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 3tp0ym1mj0gcwssfxq9s4b0y
---

## Problem

`resolver.js:6-42` parses `"Click <element> on <page>"` and captures the page group — then
discards it. Element resolution goes against `buildSymbolTable` (`resolver.js:44-70`), which
flattens every page's elements into one mapping-wide table, so the page a step names has no
bearing on which element it resolves to. A step that says `on login-page` while naming an
element that only exists on `dashboard-page` compiles clean and drives the wrong element.
Collisions are tracked but only raised when an ambiguous name is actually referenced, so the
error surfaces on some corpora and not others for the same defect.

This is worse than an unsupported feature. The grammar advertises page scoping, authors write
it believing it constrains, and it constrains nothing — enforcement theatre. Either the
qualifier binds or it leaves the grammar; parse-and-discard is the one option that must not
survive.

## Notes for ideation

- Spike DONE, 2026-07-25 (`.context/spike-page-binding.js`, run over the 100-flow corpus). It
  answers the sizing question and surfaces a design constraint that was not anticipated:

  | | |
  |---|---|
  | page-bearing steps | 437 |
  | supply the qualifier | **307 (70%)** |
  | qualifier resolvable against the mapping | 288 |
  | steps whose element is not on the stated page | 38 |
  | — of those, element lives on `_global` | **36 (legitimate)** |
  | — **genuine mismatches** | **2** |
  | elements ambiguous across pages | 13 |

  So: **this is cheap insurance, not a bug fix.** The live defect count is 2 — both the same
  `back_button`, named on `booking-confirm` and `task-execution` while mapped only under
  `service-order-detail`. Removing the qualifier from the grammar instead is not cheap: 70% of
  qualified steps use it.

- **The load-bearing design constraint, and it is not in the original brief.** 36 of the 38
  apparent mismatches are elements stored under a shared page key (`_global`) and referenced by
  the page the user is visiting — correct authoring, not error. A binding implementation that
  compares the stated page against the element's own page key rejects all 36. That is **18×
  more damage than the 2 defects it catches.** Shared/global page keys must resolve against any
  stated page, and the set of such keys must be defined rather than pattern-matched on a leading
  underscore.
- The 13 ambiguous-across-pages elements are where binding buys something structural: today they
  are only caught when a step happens to reference them, so the same defect errors on one corpus
  and passes on another.
- Binding it means element lookup becomes page-scoped with a defined fallback for steps that
  omit the qualifier — decide whether omission means "any page" (today's behaviour, kept for
  compatibility) or is itself rejected. The second is stricter and belongs with
  [[e2e-assertion-honesty-gate]]'s migration wave if chosen.
- Expect strings have the same shape (`<element> visible on <page>`) and the same question.
  Decide both together or the grammar stays inconsistent.
- Falsification: a fixture step naming a real element under the wrong page must fail to
  compile. Reverting the binding must make it compile again.
