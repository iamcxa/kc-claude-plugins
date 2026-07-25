---
title: Re-decide the canonical selector grammar — it has been declared for three months and adopted zero times
status: backlog
source: captain approval 2026-07-25, escalated out of e2e-selector-lint-gate when the codemod spike showed the canonical form is unsupported by the target apps
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: rd55vfpddtyvsbfqxqecj6cx
---

## Problem

Release 2.7.0 (2026-05-04, "Selector Grammar Alignment") established
`[role="<r>"][aria-label="<v>"]` as the canonical selector form, banned the Playwright
`role=X[name="Y"]` alternative in `scripts/lint-mapping.sh`, instructed `agents/e2e-mapper.md`
to emit the canonical form, and restated the rule across 13 markdown files.

Measured over 32 unique real mapping files, the newest written **today, 2026-07-25** — almost
three months after the canon shipped:

| Form | Occurrences |
|---|---|
| canonical `[role="…"][aria-label="…"]` | **0** |
| banned `role=X[name="…"]` | **2,183** |
| `data-testid` | 167 |
| `find role` subcommand | 1 |

This is not a corpus that predates the rule. Mappings generated today still emit the banned
form exclusively and the canonical form not once. **The canon has been in force for three
months and has changed nothing.**

The reason is structural, not disciplinary. In the primary target app, `aria-label` appears in
21 of 741 component files (2.8%) and an explicit `role=` in 10 (1.3%). CSS
`[role="button"][aria-label="Save"]` matches two *literal attributes*; for a plain
`<button>Save</button>` it matches nothing. The mapper cannot emit the canonical form for
elements that do not carry the attributes, so it emits what the accessibility tree gives it —
which is shaped like the banned form. Meanwhile Playwright's `role=X[name=Y]` matches the
*computed accessible name* and the *implicit* role, which is why it reads correctly off an a11y
snapshot even though agent-browser (CDP, not Playwright) then mishandles it at runtime.

So the pipeline is in the worst of both states: the form that describes what the mapper can see
does not execute, and the form that executes cannot describe what the mapper can see.

## Why this is the thesis of the whole programme in one artefact

An invariant was declared in prose — in a linter nothing calls, in an agent body, and in 13
restatements — and never placed at a boundary that could refuse. Three months later it is
provably not true, and nobody noticed, because nothing was ever in a position to notice.

## Notes for ideation

- Blocks [[e2e-selector-lint-gate]], which was pulled from sprint 1 on this finding. That entity
  as written would reject 26 of 32 mappings in favour of a form the apps structurally cannot
  support — it would break the pipeline rather than repair it. Do not restart it until this
  entity concludes.
- The candidate answers are visibly different in cost: `data-testid` already has 167 real uses
  but requires editing application source; the `find role|text` subcommand path matches what the
  mapper can observe but is a *subcommand*, not a `selector:` value, so adopting it is a mapping
  schema change (this is the same wall the codemod spike hit — 83 of its 198 refusals were bare
  `text=` for exactly this reason).
- Whatever is decided, the decision must land somewhere that can refuse it, or this recurs.
  Prefer the outcome that [[e2e-schema-contract]] can enforce over the one that reads best in
  CLAUDE.md.
- Before deciding, settle the empirical question the codemod spike could not: does the CSS form
  resolve against the real app at all? That needs a browser and a running target — a static
  read of selector text cannot answer it, and the spike said so explicitly rather than guessing.
- Check whether the mapper verifies that the selector it writes resolves. Exploration clicks via
  ephemeral `@ref` handles and then writes a separately derived selector string; nothing in
  `agents/e2e-mapper.md` requires confirming the written string matches anything. If so, that is
  the seam that let this run for three months.
