---
title: dispatch_records.py pointer rule round-3 follow-ups
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from the third Codex review round of iamcxa/kc-claude-plugins PR #642 (head 4b59d1ea, review:5511647035), 2026-10-14, task `followup-dispatch-records-checked`, plus the Deferred risks its validation recorded. None is P1 or Material, so none started a repair cycle there.

## Scope

- Codex P2 (`scripts/dispatch_records.py`, the pointer rule): a checklist line whose only words besides the sibling name are non-ASCII ("驗證 validation-1 的修復。") is failed as pointer-only, because the word match is ASCII-only. Decline reason: it fails closed with a message, dispatch records are repository-facing text written in English under the language rule, and no real record has hit it.
- Deferred risk (validation): the `references/sd/workflow.md` clause that a follow-up record carries its own items is not pinned by `test_sd_dispatch.py`, which tolerates it as optional; a later edit dropping the clause alone passes every check. Becomes Material if FO then writes pointer records; the script rule still fails them at the next validation.
- Deferred risk (design Limits): a paraphrased pointer ("Reuse the checklist of implementation-2.") or a pointer beside one real line passes, and the check runs at validation, one cycle after a follow-up is sent.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the findings and decline reasons above are the scope.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Closed

Closed by the Captain 2026-10-20 (「照建議關掉 19 張。」) on FO's follow-up triage against origin/main ad44f0cb: the resumed-dispatch clause is pinned in test_sd_dispatch.py; the rest fails closed or is stated in the docstring.
