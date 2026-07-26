---
title: A shape-valid but content-invalid reviews list reads as "marker absent"
status: backlog
source: named residual from reconcile-degraded-mode-symmetry (sv) EM gate, 2026-07-26
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 11785c6he7dv034qb970tqm0
---

`review_post_reviews_usable` checks only that the response is an object whose `.reviews` is an
array (`scripts/review-post.sh:328-330`). A body like `{"reviews":[42]}` passes. The marker
scan that follows then evaluates `.reviews[] | select((.body // "") | contains($marker))`
against a number, which is a jq runtime error, and the empty result reads as **"marker
absent"** — the precise misreading the usability check exists to prevent.

Both commands share it byte-identically: `resume` passes at `:746` and errors at `:751`; `post`
does the same at `:569`/`:570`. `sv` made the two commands agree on an unusable *shape*; this is
the case where the shape is fine and the contents are not.

Not reachable through the shipped `gh` adapter, which cannot produce it — the exposure is a
custom `KC_PR_FLOW_POST_TRANSPORT`, a proxy that rewrites the body, or a future adapter. It was
deliberately not folded into `sv` because the fix (tightening `review_post_reviews_usable`,
e.g. `all(.reviews[]; type == "object")`) changes the behaviour of **both** commands and
belongs with its own tests rather than riding along on a scoped change.

**AC-1 — A list whose elements are not review objects is treated as unusable, not as "marker absent".**
Verified by: driving `{"reviews":[42]}` through both `post` and `resume` and asserting each
refuses with `reconcile_unavailable` and writes no review. Falsified by: either command
proceeding to POST, or the malformed element surfacing as a jq error rather than a verdict.
