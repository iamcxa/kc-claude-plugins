---
title: Journey fold answers an open question that holds placeholder text instead of reporting a conflict
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: intake from the kc-paseo-plugins dev2 FO (Paseo agent 8b2c2fc, 2026-10-21), relaying the Captain's 「dev2 問題開給維護它的 FO」 (relayed, not a ruling in this session). The fix lands in kc-journey-map, which kc-dev-flow-2's journey path uses.
- Bite: footprints fp:project-env-notice-missing-variable:1 and :2 (questions q3, q7) conflicted on `status: "open"` questions whose answer is "Open for ideation. Fact: …", the shape kc-journey-map's own interrogation writes; the adopter deleted the placeholder answers before the fold applied (commit 05df552 on branch docs/project-env-r1-split in iamcxa/kc-paseo-plugins).
- Verified 2026-10-21: kc-journey-map 1.7.0 `lib/journey-fold.mjs` holds `if (have.ref || (have.answer && have.answer !== fp.answer)) { result(fp, 'conflict', `${key} already holds a different ${have.ref ? 'source' : 'answer'}`)`, which treats any existing answer as a conflict, open status included.
- Shape asked for: a rule for open questions, in fold or in interrogation's output, so a ruling folds into an open question without hand edits.
- Upstream first: `journey-fold.mjs`, the interrogation command's question writer, the `journey-map-question` schema (status open|answered|deferred).

## FO alignment

Alignment: not needed before ideation.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
