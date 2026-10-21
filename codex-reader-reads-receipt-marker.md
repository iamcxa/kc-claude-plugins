---
title: The Codex review reader recognizes the clean receipt that now opens with a receipt marker
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: intake from the kc-paseo-plugins dev2 FO (Paseo agent 8b2c2fc, 2026-10-21), relaying the Captain's 「dev2 問題開給維護它的 FO」 (relayed, not a ruling in this session).
- Bite: on iamcxa/kc-paseo-plugins#8 (comment 6296013066) `extensions/codex/codex_review.py` returned exit 4 "not reviewed" for a head Codex had reviewed clean, and `pr_watch.py wait` timed out. Verified 2026-10-21: that comment's body opens with `<!-- codex-review-receipt:v1 -->` before "Codex Review: Didn't find any major issues…", and kc-dev-flow-2 0.27.0 `codex_review.py` matches a clean comment only when `c["body"].startswith("Codex Review:")`. The summary-comment path still reads clean (the adopter's #10 and #11; this repository's #685, #686, #689 in batch 4).
- Shape asked for: the reader accepts the receipt-marked clean comment, still never reading an unrecognized shape as clean (the extension's stated limit).
- Upstream first: `extensions/codex/codex_review.py` and its tests.

## FO alignment

Alignment: not needed before ideation; the fix is named.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
