---
title: An FO publishing a gate briefing to Spacedock Review reads Review's format list first and repeats in chat every URL the Captain must open
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the subspace-web dev2 FO (Paseo 295b873d) relayed the Captain's words of 2026-10-28 from its session: 「這個應該要記錄到哪裡？ spacdock review or dev2？不要只是記錄記憶，因為這是其他人也會犯的錯」. Relayed words are not a ruling until the Captain confirms them in this session.
- Bite: 2026-10-28, the web FO published a gate briefing to Spacedock Review with tailnet preview URLs and the Captain could not tap them. Review's served list https://review.spacedock.md/web/formats.md says a `[text](url)` link "degrades: the text shows, not clickable" and a bare URL shows "as typed: not a link"; the subspace remote-review skill tells publishers to read that list first, but dev2 FOs publish with `subspace-relay-client publish` directly and skip the skill.
- Upstream first: kc-dev-flow-2 at origin/main says nothing about publishing to Spacedock Review (git grep for relay-client, Spacedock Review and subspace in kc-dev-flow-2/, 2026-10-28, matched only test fixtures); Spacedock's present-gate skill names chat or Subspace as presentation channels; the subspace `rr` skill already carries the rule. Where the sentence belongs (Spacedock present-gate, the subspace skill, or dev2's gate content) is the first design question.
- Related: batch-reaches-each-gate-together (Review deck carrying previews), paseo-human-surfaces-visible-and-reachable (links reachable from the Captain's phone).

## Non-goals

- Changing Spacedock Review's rendering; publishing for FOs.

## Budget

- One sentence or one check in one place, chosen at ideation; no new script.

## Stop condition

- The web FO's 2026-10-28 briefing replays with every URL the Captain must open also in the chat reply; return to the Captain if the right home is upstream Spacedock (not his repository) rather than dev2.

## FO alignment

Alignment: needed before ideation; where the rule lives is the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
