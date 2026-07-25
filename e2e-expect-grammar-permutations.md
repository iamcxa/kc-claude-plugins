---
title: Close the expect-grammar permutation holes
status: ideation
source: sprint-1 (compiler boundary) entity 1 of 5; measured this session, corroborated by the cross-model reviewer as the highest-ROI lowest-risk item in the codebase
started: 2026-07-25T12:41:25Z
completed:
verdict:
worktree:
issue:
pr:
design:
id: xnj27a2qnjtb61mqegdasm00
---

## Problem

`resolver.js:119-151` holds 12 ordered regexes; an `expect:` string matching none of them is
silently dropped (see [[e2e-assertion-honesty-gate]]). Several of the misses are not
expressiveness limits — they are permutations the table simply forgot. The asymmetry is
visible in the table itself: the negated form has `^(\w+) is not visible on [\w-]+$`, but the
positive form has only `^(\w+) is visible$` and `^(\w+) visible on [\w-]+$` — **there is no
`^(\w+) is visible on [\w-]+$`**. A negation that supports a form its positive does not is an
oversight, not a design. Similarly the table accepts `text "v" visible` and `text 'v' on page`
— where `page` is a literal word, unlike every element form, which takes a page name — but not
`text 'v' is visible`.

Measured over the corpus: the visibility-word-order class is 8% of all deferred expects and the
text-quoting class 10%, so roughly **66 assertions across 100 flows are dropped purely because
of missing permutations**. Authors are writing the obvious combination of two supported forms.

This entity is a pure widening: it converts dropped assertions into running ones and can reject
nothing that compiles today. Sequenced first in the sprint because it shrinks the blast radius
every later narrowing has to absorb.

## Notes for ideation

- Enumerate from the corpus, not from imagination — the deferred strings are reproducible via
  the scripts named in [[e2e-typed-operands]]. Add the permutations the data shows authors
  actually write; resist completing the cross-product for its own sake.
- The `text '<v>' on page` literal-word inconsistency is the likely root of the text class.
  Decide whether the fix is a new permutation or making that form take a page name like every
  other; the second is a wider change and may belong with [[e2e-typed-operands]].
- Every added pattern needs a corpus assertion that was previously deferred and now resolves —
  a regex added without a real string it recovers is speculation.
- Falsification is direct: revert one added pattern and the specific corpus assertion it
  recovers must return to deferred.
