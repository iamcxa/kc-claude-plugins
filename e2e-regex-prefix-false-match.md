---
title: The regex-prefix branch emits bare substring greps that match the wrong element
status: backlog
source: found by the SO/EM reviewer during rd cycle-1 re-review, 2026-07-26; pre-existing, not introduced by that entity
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: ybbxkftvpk8n7mcsvks1xm4k
---

## Problem

`compiler/lib/selector-translate.js:86-91` translates `role=X[name=/Y/]` by stripping
from the first regex metacharacter and returning the **bare literal prefix** — no quotes.
`codegen.js:748` then runs it as `grep -Fq "$_pattern"` against the accessibility
snapshot, where every accessible name is quoted. So the pattern is not anchored to a
name boundary and matches anywhere in the line.

Measured over the real corpus (49 unique `role=X[name=/…/]` values, 5 affected):

```
role=button[name=/holder.*關閉/]              ->  holder
role=button[name=/Toggle (Dark|Light) Mode/]  ->  Toggle
role=button[name=/calendar.*\d{4}/]           ->  calendar
role=button[name=/切換為.*模式/]                ->  切換為
role=button[name=/登\s*入/]                    ->  登
```

Verified against a snapshot line: `grep -Fq holder` matches
`- button "placeholder text" [ref=e1]`. The assertion passes on the wrong element.

**This is the false-PASS direction** — the same failure class as issue #7, which is what
makes it more serious than [[e2e-nth-chord-widening]]. The other translation defects
found in this programme fail loud; this one succeeds quietly on something the author
never named.

## Notes for ideation

- The obvious fix is to stop prefix-extracting: return `null` for regex values and let
  them take the `_poll_visible` fallback, which is exactly the choice
  [[e2e-selector-canon-review]] made for `text=/regex/` after establishing that
  mirroring this branch would recreate the defect. Consistency argues for it; the
  counter-argument is that 44 of the 49 corpus values currently produce a pattern
  identical to their full intent and would lose a working check. Weigh both — the
  44 are working by accident of having no metacharacter before the end.
- A middle option: keep extraction but quote-and-anchor the emitted pattern so it can
  only match a whole accessible name. That preserves the 44 and kills the 5. Check
  whether the snapshot format guarantees the closing quote before relying on it.
- Falsification: a fixture with an element named `placeholder text` and a selector
  intending `holder…`. The current code passes it. Any fix must fail it.
- Beware the measurement trap that hid this for two review rounds: printing the
  pattern through `JSON.stringify` adds quotes that are not in the value, which makes
  a bare pattern look anchored. Print raw, and assert with the same `grep -F` the
  runtime uses.
