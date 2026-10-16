---
title: The dispatch_records.py --names check runs only if FO remembers to run it before dispatch build
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:names-check-before-dispatch:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:names-check-before-dispatch-backlog-1
              briefing:
                id: briefing:names-check-before-dispatch:backlog:attempt-1:revision-1
                digest: sha256:f5c4f4725e70e4780f45771d090a39a1e631de67a884c2f3be3a591dcae294b2
                room-ref: ./names-check-before-dispatch/review/backlog/briefing-1
---

Filed from a learn package-issue candidate the Captain approved on 2026-10-14 (「1,3」), after the observer report on task `followup-dispatch-records-checked` (PR #642) found bare package-script names in FO's own dispatch records `implementation-1.md` and `-2.md`, because FO ran `dispatch_records.py --names` after `dispatch build` instead of before. The same happened on that task's first implementation dispatch and on the fo-lifecycle-mod implementation dispatch the same day (caught before launch the second time).

## Scope

- The gap is enforcement: the README Stages rule says "before `dispatch build`, FO runs `python3 <package>/scripts/dispatch_records.py --names <record>` on the saved record", but nothing runs it; `spacedock dispatch build` neither calls it nor refuses a checklist naming a bare script, and the folder-mode check at validation does not include `--names`.
- Learn's no-change reason for job 49a91123 said the task's own Package root check enforces this practice; it does not (the Package root rule checks a different line and runs at validation).
- Candidate routes: a pre-send single-record mode (declined as D2 of `followup-dispatch-records-checked`, to be filed "if the late catch bites again"; it has bitten twice since), or folding `--names` into the validation-time folder run. Which is for ideation.
- Related: `extension-instruction-reaches-dispatch` (another dispatch-time check).
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
