---
title: The Codex reader counts a code-review round only from a code review, never from a completed security review
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: codex-reader-reads-receipt-marker ideation D3, approved by the Captain 「可以，但要注意這個安全性審查是選用功能，不是每個人都會打開，請你動手設計時要跟 codex 確認一下它的規格」 (batch-5 sitting, 2026-10-21) as its own batch-5 task, after codex-reader-reads-receipt-marker.
- Bite: that ideation found the summary-comment path of `kc-dev-flow-2/extensions/codex/codex_review.py` reads a completed Codex security review as a clean code-review round; iamcxa/kc-claude-plugins #685, #686 and #689 read exit 0 via `summary:` while their `code_review.status` was null. Those three PRs merged in kc-dev-flow-2 0.27.0 with that evidence counted as Codex clean.
- First step: establish, from Codex's own documentation or output specification (not an adopter's reading of it), what the summary comment states for code review and for security review, whether a code review ran on those three heads, and what the comment looks like when security review is not enabled.
- The Captain's constraint: security review is an optional Codex feature that many repositories do not enable, so the reader must stay correct with it off, with it on, and when only one of the two ran.
- Shape asked for: a round counts as clean only from a code-review result on the head; a security-only summary reads as no verdict for code review.
- Upstream first: `codex_review.py` and its tests; the codex extension's stated limit that an unrecognized shape never reads as clean; codex-reader-reads-receipt-marker (same file, lands first).
- Non-goals: reading or acting on security-review findings themselves.

## FO alignment

Alignment: not needed before ideation; the Captain set the constraint.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
