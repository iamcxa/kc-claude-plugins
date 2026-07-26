---
title: The once-only path cannot work on a PR with more than one page of reviews
status: backlog
source: found outside the blast radius during sv's fresh-context validation, 2026-07-26
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: n9xjhpeza7q0hk3sepc6rxhc
---

`review_post_gh_transport`'s `list` op (`scripts/review-post.sh:127-129`) runs

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
