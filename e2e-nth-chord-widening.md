---
title: The nth chord translates by dropping its index, silently widening 339 assertions
status: backlog
source: found while validating e2e-selector-canon-review, 2026-07-25 — same disease as the deferred expects, different mechanism
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: z1yh40ten5zgb342xfmzzq7d
---

## Problem

`compiler/lib/selector-translate.js:93-95` translates the Playwright nth chord by
discarding the index:

```js
// role=X >> nth=N → X (role name only)
var nthMatch = selector.match(/^role=(\w+)\s*>>/);
if (nthMatch) return nthMatch[1];
```

So `role=tab >> nth=1` becomes the a11y pattern `tab`, and the compiled probe greps
for *any* tab in the snapshot. An assertion written to check the second tab passes if
the first one is present. The corpus carries **339 lines** using this form.

This is [[e2e-assertion-honesty-gate]]'s defect wearing a different costume. There the
assertion did not run at all; here it runs and reports success on a weaker claim than
its author wrote. Both are checks that cannot fail for the reason they exist.

`scripts/lint-mapping.sh` still bans the chord (CLASS 2 was deliberately kept when
CLASS 1 was removed), so nothing new is being authored in this form — but the 339
existing lines are live, and the ban does not repair them.

## Notes for ideation

- Two candidate shapes, and the choice is not obvious. Either translate the index
  faithfully — which the a11y-grep mechanism may not support, since `grep -Fq` over a
  flat snapshot has no notion of "the second match" and would need an occurrence
  count rather than a substring test — or refuse the form at compile time so the 339
  become loud failures instead of quiet passes. The second is honest but converts
  working-looking flows into red ones; sequence it behind
  [[e2e-assertion-honesty-gate]] so both landings share one migration wave.
- Establish first whether any of the 339 actually depend on the index. A chord on an
  element that happens to be unique is harmless; one on a repeated element is a live
  wrong-element assertion. That count decides whether this is a cleanup or a defect.
- Falsification for either fix: a fixture with two same-role elements where only the
  second satisfies the assertion. The current translation passes it. Any correct
  implementation must fail it.
- Do not treat the lint ban as coverage. CLASS 2 stops new instances; it does not make
  the existing ones mean what they say. That distinction is the whole entity.

## Scope extended, 2026-07-26 — `text=` chords now widen too

The correction round on [[e2e-selector-canon-review]] made `text=V >> nth=N` translate to
`"V"`, mirroring the `role=` precedent at `selector-translate.js:93-95`. That was the right
call for that entity — the alternative (mirroring the regex branch) would have produced
patterns that can never match — but it means **this defect's blast radius now includes the
18 corpus `text=` chords** on top of the 339 `role=` ones.

The implementing worker argued the widening is sound because the accessibility snapshot does
not carry the DOM duplicate the chord exists to disambiguate. **That argument is untested and
this entity owns testing it.** React Native Web is the documented reason those chords exist
(text renders twice, `nth=0` hidden), and an RNW app is available on `localhost:8081` — take
a snapshot of a duplicated element there and see whether the a11y tree collapses the pair or
carries both. A snapshot captured during this session showed the same string appearing on two
separate node types (`button "AlphaBtn"` and `StaticText "AlphaBtn"`), which is suggestive that
it does NOT collapse — but that was a plain HTML fixture, not RNW, so it does not settle it.

If the snapshot does carry both, the widening is a live wrong-element risk and not merely a
loosened assertion.
