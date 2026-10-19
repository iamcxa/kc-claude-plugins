---
title: A task cannot reach its delivery gate while the comment check its implementation and validation owe is missing from their reports
variant: kc-dev-flow-2
merge: pr
status: backlog
---

## Scope

- Source: issue iamcxa/kc-claude-plugins#409 (written for kc-dev-flow v1 from subspace-relay PRs 195 and 196, still open on 2026-10-19), handed to this FO under DOT#0007 (iamcxa/dot-decision-log PR #9, revision 3d601c5).
- Finding on origin/main 18dbf490 (2026-10-19): kc-dev-flow-2 states the rule but nothing at completion refuses its absence. `skills/implementation/principles.md` requires running `comment_ratio.py <base> HEAD` and reporting its output; `skills/validation/principles.md` requires reading every added comment and treats `comment_ratio.py` exit 1 as a repair finding. No completion-path script calls `comment_ratio.py`: `git grep -c -i comment` gives 0 in `laws_check.py`, `observer_check.py`, `dispatch_records.py` and `pr_watch.py`, and the 3 hits in `delivery_gate.py` are the `comment:<id>` reviewer token. So a validation report with no `comment_ratio.py` output, or with output from an earlier candidate, still reaches the delivery gate.
- Part of #409 already covered by prose only: the semantic read of changed comments (the #196 false-ownership case) is the validation principle "Read every comment the candidate adds"; `comment_ratio.py` measures ratio and citation classes, not truth.
- Bite: relay PRs 195 and 196 (the case corpus with fixed revisions in #409). No dev2 task in this workflow has yet been observed delivered without the comment output; measuring that over the archived validation reports is the first ideation step.
- Upstream first: `delivery_gate.py` (the merge ask), `laws_check.py` L1/L2, the observer; Spacedock owns the runtime transition. Whether one of these can require the `comment_ratio.py` line bound to the dispatched Candidate head, with no new FO words.
- Non-goals: to be set at ideation. Closing #409 is not this task's to do; if the gap is closed, the task proposes it to the Captain.

## FO alignment

Alignment: not needed before ideation; the Captain approved this trial run in DOT#0007 (「准用 409」, 2026-10-19), which leaves profile, gates and merge to him as usual.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Peers

- Peer: DOT#0007 conductor (kc-claude-plugins workspace) = de83e726-1fa6-4991-b12e-bd82ad8a7d79; listed as uds:/tmp/cc-socks/9226.sock (reply, 2026-10-19). Asked this FO to decide whether #409's gap remains in kc-dev-flow-2 and file one task; FO read DOT#0007 at 3d601c5 and checked the Captain's words 「可以，跑看看」 and 「准用 409」 in that session's own transcript (user messages at 2026-10-19T08:08:43Z and 08:18:11Z) before filing.
