---
title: Adoption asks which extensions to enable, and a record dispatched before an extension existed is not judged against it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: intake from the kc-paseo-plugins dev2 FO (Paseo agent 8b2c2fc, 2026-10-21), relaying the Captain's 「dev2 問題開給維護它的 FO」 and his remark there 「理論上 adopt 時應該要問要用哪些 ext」 (relayed, not a ruling in this session).
- Bite: iamcxa/kc-paseo-plugins ran release r1's first four tasks with `extensions: []` (no roborev, codex, learn, journey-map) until the Captain ruled 「啟動全部除了 copilot 之外的 ext」 (iamcxa/kc-paseo-plugins#12). Verified 2026-10-21: kc-dev-flow-2 0.27.0 `references/sd/adoption.md` § Extensions says only to check each extension's `Needs:` before listing it, and `references/sd/workflow.md` ships `extensions: []`.
- Side effect reported: after the list changed, `dispatch_records.py` flags every earlier implementation record as missing the roborev instruction, and an observer counts it as a violation although the extension was not listed when that record was dispatched (the dev2-poc observer in this workflow found the same shape on interrogation-replay-on-batch-3-poc).
- Upstream first: `spacedock:commission` / `spacedock:refit` (what adoption asks), `adoption.md`, `dispatch_records.py`, the observer.
- Non-goals: choosing extensions for any adopter.

## FO alignment

Alignment: needed at ideation; whether adoption asks or recommends a default list is the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
