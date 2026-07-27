---
title: An absolute claim in prose needs an enforcement point or a bound
status: backlog
source: EM validation gate on qh (#67), 2026-07-27 — third and fourth occurrence of the class in two days, across two different authoring agents
design:
id: 4nrx4be9bt2741zrwqase1nf
---

Four times in two days a document or comment asserted a guarantee its enforcement point does not
make. Each shipped: each passed CI, each was read by a reviewer, and each was caught only by a
later adversarial pass that went looking for it.

- `sv` (#63) wrote "leaves **exactly one path** to the POST" into `reference/review-runtime.md`.
  Feeding `{"reviews":[42]}` walks a second path and reaches a live POST.
- `qh` (#67) wrote "mirror the helper's calendar semantics **exactly**" into a commit message.
  `18446744073709551616` returned `1970-01-01T00:00:00Z` where the Python reference raises
  OverflowError — in both signs.
- `qh` wrote "temp_events **is** byte-for-byte the log validated above" into a code comment. It is
  an assumption about a window, not a property the code establishes.
- `qh` wrote that the batch falls back "whenever ... its record count disagrees with the file" into
  `reference/review-runtime.md`. That cross-check runs on neither caller-supplied path.

The authors were **different agents**, which is what makes this a class rather than a habit.

The repo already has the downstream half of the rule: `docs/dev/README.md`'s validation stage
requires a doc diff stating an absolute to name the input that would falsify it. That clause works
— it caught all four. But it is a *gate-side* rule, so the cost is paid every time by a reviewer
hunting for a counterexample, and it covers doc diffs only: two of the four above are a commit
message and a code comment, which no gate reads.

The missing half is authoring-side: an absolute — "exactly", "only", "always", "never",
"byte-for-byte", "cannot" — written into a reference, a comment, or a commit message must either
name the enforcement point that makes it true, or be rewritten as the bounded claim the code
actually supports. `qh`'s return round did exactly this by hand for all four sites and it cost
minutes; the differential test it added converts one of them from asserted to checked, which is
the shape to generalise.

Open question for the captain, not for the FO: whether this is a prose rule in
`docs/dev/README.md` plus `kc-pr-flow/CLAUDE.md`, or also a diff-time lint that greps added lines
in `reference/**`, `*.md`, and comment bodies for the absolute vocabulary and asks for a citation.
A lint is mechanically cheap and would be the first check in this repo that reads prose for a
claim rather than a format — that is either the point or the reason not to.

**AC-1 — An absolute claim added to a reference, comment, or commit message names its enforcement point or is bounded.**
Verified by: the rule stated in the canonical doc, plus a re-audit of the four sites above showing each now cites a test, a code path, or a stated exception. Falsified by: a new absolute landing with neither.
