---
title: "close.py closes only the tasks the batch dispatched, and its validator exempts Captain-stopped tasks from the merged_sha rule"
status: backlog
source: "measured on the first close after #448 merged, ship-cloud-wrapper-r3, 2026-09-15 (questions log on spacedock-state/ship)"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r4
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 8ekqymrkgz5f9y0h8qaf6vp2
gates:
    version: 1
    records:
        - id: gate:8ekqymrkgz5f9y0h8qaf6vp2:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:8ekqymrkgz5f9y0h8qaf6vp2-backlog-1
              briefing:
                id: briefing:8ekqymrkgz5f9y0h8qaf6vp2:backlog:attempt-1:revision-1
                digest: sha256:a4abe55b7f086322b4f438e04bcced96ed7fed0cd2fabbb3fdfb4994c786de58
                room-ref: ./close-roster-is-the-fence-and-captain-stopped-validates/review/backlog/briefing-1
---

bite: 2026-09-15, `python3 kc-ship-flow/scripts/close.py ship-cloud-wrapper-r3 --dev-state … --ship-state …` at main 625c6b50. (1) It exited 3 `not all tasks merged` because three entities carrying `sprint: ship-cloud-wrapper-r3` with `sprint-readiness: defer` — never dispatched, absent from the fence — were counted as batch tasks; the ship FO had to move them to another sprint to close. (2) After that, `close.py --validate` refused the receipt it had just written: the two `captain_stopped` tasks (PRs #446 and #450, closed unmerged by the Captain) carry `merged_sha: null`, and #448's 40-hex rule has no exemption for them, so the first receipt the new validator ever saw failed on its own rule. The receipt was committed with the refusal disclosed.

consumer: the ship first officer's close step (`kc-ship-flow:run-batch`, stage closed), every batch that has a deferred sibling in the sprint or a Captain-closed PR — both happened in the first three batches.

## Accepted outcome

`close.py` treats the fence as the batch roster, and a Captain-stopped task closes with a receipt entry that says so instead of failing validation.

## Acceptance criteria

* **AC-1** `close.py` builds its task set from the fence's slugs (what `dispatch.sh` claimed), not from every entity whose `sprint` matches; an entity in the sprint but absent from the fence is listed once on stderr as `not dispatched` and ignored. Verified by: the r3 state replayed with the three deferred entities present closes without moving them. Falsified by: exit 3 on that replay.
* **AC-2** A task in `captain_stopped` is written with `merged_sha: null` and `closed: captain_stopped`, and `--validate` accepts it; a merged task with a null or non-40-hex `merged_sha` is still refused. Verified by: the r3 receipt validates as committed; the existing bad-merged-sha fixture still fails. Falsified by: either outcome flipping.
* **AC-3** No new fixture copies real repository SHAs or duplicates an existing file.

## Non-goals

- No change to the receipt schema version; add the `closed` field as optional.
- No change to debrief matching (#448).

## Route-back conditions

- Back to backlog if the fence shape written by `dispatch.sh --resume` (#445 `history`) changes the slug roster semantics.

Profile recommendation: pilot.
