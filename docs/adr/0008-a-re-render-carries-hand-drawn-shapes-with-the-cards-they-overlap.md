# 0008. A re-render carries a hand-drawn shape with the cards it overlaps

Date: 2026-10-07

## Status

Accepted

## Context

`renderToRoom` recomputed generated card positions from the journey YAML and left every
shape without `meta.journey` (hand frames, stickies) at its absolute position. On one real
team canvas (kc-journey-map 1.5.0, 2026-10-06/07) two stories added to one release moved
the cards below by +500, and another row by +2910; of 74 hand-drawn shapes, 7 were left
beside empty space and repaired by hand, each by the offset of the card it had overlapped.
Replayed on the three recorded room snapshots, the carry rule below moves 8 shapes, 7 of
them to exactly where the hand repair put them; the eighth is a frame whose corner overlaps
a card by 28px, which the hand repair left in place.

## Decision

**Words:** 「可以。標註跟著卡片移動，不能判斷的列出來，因為如果沒跟著動，那畫面會變得很奇怪，而要怎樣跟著動，做最近一次更新的 agent 才知道彼此的關係，不然很可能手寫標記會被破壞」 — Captain, ideation gate of this task, 2026-10-07.

**Options considered:**
- carry: move a hand-drawn shape with the cards it overlaps, list what cannot be placed
  (chosen)
- report only: leave every hand-drawn shape in place and list the ones that would be
  stranded — rejected by the Captain's choice: the canvas looks wrong until someone moves
  them, and only the render that moved the cards knows which shape belonged to which card
- centre-in-card instead of any positive overlap — rejected: it misses a sticky that only
  grazes two stacked cards yet was moved by hand

A shape without `meta.journey`, parented directly to a page, that overlaps with positive
area at least one story, activity, question or answer card this render redraws or removes
moves by the cards' offset when every overlapped card moves by the same (dx, dy). Cards
that disagree, or a removed card, leave it in place, listed as `cards-disagree` or
`card-removed`. A shape that overlaps no card is not moved and not listed. The relation is
computed by the render that moves the cards, from the positions they had before it, inside
the same call; nothing is stored on the shape. Every carried and stranded shape is printed
(`carried <id> (dx, dy) with <cards>`, `stranded <id>: <reason> <cards>`) and returned as
`carried` and `stranded` by `renderToRoom`. The sentence in `canvas.md` that hand-drawn
shapes are "never touched" is replaced by this rule. Later work must keep the move
derived from pre-render positions in one render, never from a stored link.

## Consequences

A re-render can now move a hand-drawn shape, so a shape that sat on a card by accident moves
with it; the render says so on every run. Not covered, and named in `canvas.md`: shapes
without width and height (text, arrows, strokes), shapes nested in another shape, rotation
(the unrotated box decides), flow, constraint and legend boxes as cards, and cards on a
page the call did not draw. Only the recorded incident (one canvas) supports the rule;
reopen if an adopter's canvas shows a shape carried wrongly, or a recorded case needs a
box kind that is not covered.
