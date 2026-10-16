---
title: design_surfaces.py amendment check round-3 follow-ups (moved blocks outside Superseded text, marker number suffix)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from Codex review round 3 (review:5544568264) of iamcxa/kc-claude-plugins PR #650 (head 458324f8), task `amendment-form-check`. Neither is P1, so neither starts a repair cycle there; each is filed here with its decline reason, per `## FO steps: review findings` step 5.

## Scope

- P2: `declarations()` reads bold criterion lines anywhere in an amendment entry, so a verbatim `Captain:` or `Asked:` value that continues on a line starting `> **AC-9**:` is treated as a moved criterion and a valid `Supersedes: none` entry is refused. Decline reason: fails closed (a refusal, not a pass), and no corpus entry quotes a criterion line inside `Captain:` or `Asked:`; candidate fix: parse moved blocks only under `Superseded text:`.
- P2: the amendment-number boundary `(?!\d)` accepts `Amended by Captain, amendment 1a` as amendment 1. Decline reason: needs a typed malformed marker, none in the corpus; candidate fix: exclude letters and identifier characters after the number.
