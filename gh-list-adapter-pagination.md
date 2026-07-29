---
title: The once-only path cannot work on a PR with more than one page of reviews
status: implementation
source: found outside the blast radius during sv's fresh-context validation, 2026-07-26
started: 2026-07-29T07:44:33Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-gh-list-adapter-pagination
issue:
pr:
design: trivial-pass
id: n9xjhpeza7q0hk3sepc6rxhc
lane: defect
---

`review_post_gh_transport`'s `list` op (`scripts/review-post.sh:233-237` on
`origin/main` at `097685af`) runs

```
gh api "repos/$repo/pulls/$pr/reviews" --paginate --jq '[.[] | {id, user: .user.login, body, commit_id}]'
```

then feeds the result to `jq -cn --argjson reviews "$reviews"`. With `--paginate`, `gh` applies
the `--jq` filter **per page** and concatenates the outputs, so a two-page PR yields two
back-to-back JSON arrays. `--argjson` accepts exactly one JSON value, so it fails, the transport
returns non-zero, and both `post` and `resume` abort with rc 74.

The direction is safe — it fails closed, and it is incidentally why the `gh` adapter cannot
produce the exit-0-non-array body that `reconcile-list-element-shape` is about. But the
consequence is that **the entire once-only posting path is unusable on any PR whose reviews list
paginates**, which for a busy PR is not an exotic case. Nobody has hit it yet because
`KC_PR_FLOW_ONCE_ONLY_POST` defaults off.

CI cannot catch this: every suite drives the injected stub transport, and the `gh` adapter is
explicitly never exercised there (`scripts/review-post.sh:99-100`). So the fix needs a test that
exercises the adapter's own composition against a recorded multi-page response, not another stub
scenario.

**AC-1 — A reviews list spanning more than one page produces one usable array.**
Verified by: driving the `gh` list adapter against a recorded two-page response and asserting a
single `{reviews: [...]}` object containing every review from both pages. Falsified by: the
transport returning non-zero, or dropping the reviews from any page.

## Defect-lane classification

All four bounded-defect conditions hold:

1. Root cause is identified at `scripts/review-post.sh:233-237`: `gh --paginate`
   applies `--jq` per page, producing adjacent arrays that `jq --argjson` cannot
   consume as one value.
2. Acceptance is mechanical: the recorded two-page adapter test above must fail
   before the fix and pass after it.
3. This is one seam: the production `gh` transport's `list` composition and its
   adapter-level test. No schema, UI, or cross-layer contract changes.
4. No design choice is open: preserve the existing `{reviews: [...]}` transport
   result and combine every page before constructing it.

Design: `trivial-pass` — the fix restores the already-defined transport shape
without deciding a new interface.

Appetite: one implementation dispatch, estimated 45 minutes. Tolerance: up to
75 minutes or one correction commit; if the repair requires a new transport
schema, changes the once-only reconciliation contract, or spills into `11`
(`reconcile-list-element-shape`), return to ideation instead.

Implementation dispatch sizing: one fresh worker in one isolated worktree.
Validation remains a fresh-context gate.
