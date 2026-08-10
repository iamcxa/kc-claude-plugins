---
title: Review the published-tag Science Officer runtime smoke
status: backlog
source: Captain-approved issue #183 follow-up, 2026-08-10
product: kc-dev-flow
sprint:
design:
id: jj5jbzp2tpyc7a6x78wnfqky
---

## Problem

The published-tag cross-harness smoke is intentionally speculative until the first kc-dev-flow release containing its packaged schema and prompt can exercise the clean-installed Claude and Codex surfaces. Without a durable review point, the harness could remain permanently after its claimed value fails to materialize.

## Review contract

After the first GitHub Release containing the smoke assets, run the authenticated exact-tag release smoke and preserve its receipt. Keep the harness only if it produces installed-runtime evidence unavailable from the existing post-install and marketplace helpers; otherwise remove it.

This seed captures the review obligation only. Its blank sprint grants no scheduling or execution authority.
