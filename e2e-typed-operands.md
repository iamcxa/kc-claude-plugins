---
id: g5zmajvxtfrsph13tv3x8jdz
title: Kill the parse-and-discard class in flow step operands
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

The compiler resolves flow steps by regex-matching a natural-language `action:` string,
and two of those matches are silently lossy. `compiler/resolver.js:266` downgrades any
`expect:` string that matches none of the 12 ordered patterns to `type: 'deferred'`;
`compiler/codegen.js:1674-1675` then compiles that into a bare `echo "TODO: ..."` which
never touches `_STEP_RESULTS`, so the step stays `pass` (default set at `codegen.js:985`,
only flipped by the failure path at `codegen.js:588`) and the run exits green. Separately,
the `<page>` group in `"Click <element> on <page>"` is captured by the regex at
`resolver.js:6-42` and then discarded — element lookup goes against a flat mapping-wide
symbol table (`buildSymbolTable`, `resolver.js:44-70`), so a wrong or typo'd page name
never errors. Net effect: the pipeline reports success on a compiled test that asserts
nothing and resolves elements against the wrong page. A human notices a suite that passes
suspiciously fast; an agent loop compounds on it.

The honest signal already exists and is merely unwired — `coverage.js:76` correctly
declines to count a deferred expect toward `verified_count`, but coverage is opt-in
(`--coverage`) and reported as a percentage, never as a gate. Likewise
`scripts/lint-mapping.sh` rejects 5 banned selector forms that the plugin's own docs say
are "silently mishandled at runtime (fallback eval path -> false positive risk)", but the
compiler never calls it; the ban is enforced by restating it in 13 markdown files.

**Scope cut by the captain, 2026-07-25.** This work split into two entities: making the
silence loud is [[e2e-assertion-honesty-gate]] and goes first; **this entity is the
structural half and is sequenced after it** ("先做 A，B 應該落下一個 entity，保持敏捷").

What remains here: promote operands out of the prose `action:` string into typed fields
(`element:`, `page:`), demoting `action:` to a human-readable label, so both defects above
become unrepresentable rather than merely rejected — and close the grammar permutation
holes the spike found. Flows already carry a `type:` field (`parser.js` errors with "has no
type field — run migration tool first") and a `migrate.js` already exists, so this is a
repair of a half-built abstraction, not a greenfield build. The cross-model reviewer argued
this is the real lever and that the gate alone patches symptoms; the captain's counter is
that the gate ships value sooner and this can follow, which the sequencing above records.

## Notes for ideation

- Spike DONE, 2026-07-25 — the number exists now, do not re-run it. Over 100 unique flow
  YAMLs by content hash (87 resolvable against their mapping), **368 of 794 expects resolve
  to `deferred` — 46.3%**, concentrated in 19.5% of flows; excluding one outlier feature
  whose near-duplicate copies contribute ~260 of the 368, the baseline is **~25%**. Live
  proof of the false green on a real project flow: `e2e-compile entity-inspector-drawer`
  prints `Compiled: 5 steps, 12 expects active, 11 expects deferred` then `OK` — 48% of that
  flow's assertions silently dropped, exit 0.
- Classification of the 368 — this should drive scope, not the headline rate:
  35% free-form prose ("at least one card shows NT$ prefix") — the genuine ceiling;
  16% deliberate human checkpoints ("manual Enter keeps X selected");
  14% raw selectors smuggled into `expect:` ("[data-testid='...'] is visible");
  12% unsupported predicates on known elements ("X has exactly 8 rows", "X has aria-disabled=true");
  10% text-assertion quoting variants ("text '請先選擇廠牌' is visible");
  8% visibility word-order ("email_input is visible on login");
  5% quantified assertions ("every X row is labelled '未實作'").
- The last two rows (18%) are pure permutation holes in the hand-written table at
  `resolver.js:119-151`: it accepts `X is visible` and `X visible on <page>` but not
  `X is visible on <page>`; it accepts `text "v" visible` and `text 'v' on page` — where
  `page` is a LITERAL word, not a page name, unlike every element form — but not
  `text 'v' is visible`. Authors write the obvious combination of two supported forms and
  get silence.
- The 16% manual class exists *because* `agents/e2e-flow-writer.md` Critical Rule 9 bans
  `manual: true` without offering a replacement; authors moved it into `expect:` strings,
  where it silently passes. The ban produced the hole it was meant to close.
- Consequence for scope: the ceiling is real but well below the cross-model reviewer's
  prediction, and it bounds how much *grammar* work is worth doing — it does not bear on
  whether the *honesty gate* is worth doing. Even the irreducible 35% should fail loud
  ("not automatable — mark manual or rewrite") rather than emit `echo TODO` and exit green.
- Blocks the value measurement for [[e2e-json-diagnostics]]: a repair-loop cost baseline is
  meaningless while the baseline silently passes.
