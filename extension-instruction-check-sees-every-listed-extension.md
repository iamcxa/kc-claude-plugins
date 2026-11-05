---
title: The dispatch-record check sees every listed extension's scope-note instruction, the paseo one included
variant: kc-dev-flow-2
status: backlog
profile: pilot
merge: pr
gates:
    version: 1
    records:
        - id: gate:extension-instruction-check-sees-every-listed-extension:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:extension-instruction-check-sees-every-listed-extension-backlog-1
              briefing:
                id: briefing:extension-instruction-check-sees-every-listed-extension:backlog:attempt-1:revision-1
                digest: sha256:d7c07cbecae6d0a7fd945d14cc7d29634b7c6093531e1679611e8a4f547a4ef7
                room-ref: ./extension-instruction-check-sees-every-listed-extension/review/backlog/briefing-1
---

`dispatch_records.py` holds a dispatch record that lacks the scope-note instruction of any extension the workflow README lists, not only the instructions that name a package script.

Source: the Captain, chat 2026-11-05: 「開」, answering 「建議開兩張 dev2 任務，請你決定要不要開。」 whose first item read 「派工紀錄檢查器也要檢查每個已啟用擴充規定的交代句。這一類是 12 筆。」

Bite: observer reports across every archived task carry 12 violations (6 of them in the 12 tasks of batches 12 and 13; counted with grep over `_archive/*/observer.md` on 2026-11-05) of the paseo extension's rule "Start in the assigned worktree; verify pwd and git root before edits." (scope notes of Codex worker dispatch records, ideation, implementation, validation and message records). `dispatch_records.py --names` passed every one of those records. Cause, read in kc-dev-flow-2 0.35.0 on 2026-11-05: `declared_instructions` keeps an extension only when its EXTENSION.md has the `INSTRUCTION` bullet, a `JOINS` stage and a `<package>/extensions/...py` path in that bullet, and `extension_errors` reads only `dispatch/<stage>-1.md`. Of the nine packaged extensions only roborev passes that filter; paseo writes its line as `Add to scope notes: "..."` with no join stage and no script path, so it is never checked.

Consumer: every adopter FO whose README lists paseo (Codex workers through Paseo) or another extension whose scope-note instruction names no script, and the observer, which today is the only reader that catches the missing line.

## Scope

- Upstream first: `dispatch_records.py` (`declared_instructions`, `extension_errors`) already checks the roborev instruction; this task widens that check rather than adding one. The paseo, codex, copilot and other EXTENSION.md files state their own scope-note lines.
- Non-goals: the items already parked in extension-instruction-followups (YAML block lists, the README read at run time).
- Batch 14: the Captain 「可以」 (chat, 2026-11-05), answering 「這 5 張當下一批，可以嗎？」, which named this task.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- Every listed extension whose EXTENSION.md tells FO to add a scope-note line is checked in each dispatch record it applies to, not only `<stage>-1.md`; replays of the batch 12 and 13 records that lack the paseo line are held, and a record carrying the line or `<name> not run: <reason>` passes.

## FO alignment

Alignment: not needed: the line and where it applies are already written in each EXTENSION.md; the check only reads them.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
