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

- Spike before choosing: the page group is optional in the pattern
  (`(?:\s+on\s+([\w-]+))?`), so count how many corpus steps supply it and how many of those
  currently resolve to an element on a different page. The first number sizes the migration;
  the second is the live defect count. If the second is zero the change is cheap insurance; if
  it is not, it is a bug fix with a blast radius.
- Binding it means element lookup becomes page-scoped with a defined fallback for steps that
  omit the qualifier — decide whether omission means "any page" (today's behaviour, kept for
  compatibility) or is itself rejected. The second is stricter and belongs with
  [[e2e-assertion-honesty-gate]]'s migration wave if chosen.
- Expect strings have the same shape (`<element> visible on <page>`) and the same question.
  Decide both together or the grammar stays inconsistent.
- Falsification: a fixture step naming a real element under the wrong page must fail to
  compile. Reverting the binding must make it compile again.
