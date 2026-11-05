---
title: The dispatch-record check sees every listed extension's scope-note instruction, the paseo one included
variant: kc-dev-flow-2
status: backlog
---

`dispatch_records.py` holds a dispatch record that lacks the scope-note instruction of any extension the workflow README lists, not only the instructions that name a package script.

Source: the Captain, chat 2026-11-05: 「開」, answering 「建議開兩張 dev2 任務，請你決定要不要開。」 whose first item read 「派工紀錄檢查器也要檢查每個已啟用擴充規定的交代句。這一類是 12 筆。」

Bite: across the 12 tasks archived in batches 12 and 13, observer reports carry 12 violations of the paseo extension's rule "Start in the assigned worktree; verify pwd and git root before edits." (scope notes of Codex worker dispatch records, ideation, implementation, validation and message records). `dispatch_records.py --names` passed every one of those records. Cause, read in kc-dev-flow-2 0.35.0 on 2026-11-05: `declared_instructions` keeps an extension only when its EXTENSION.md has the `INSTRUCTION` bullet, a `JOINS` stage and a `<package>/extensions/...py` path in that bullet, and `extension_errors` reads only `dispatch/<stage>-1.md`. Of the nine packaged extensions only roborev passes that filter; paseo writes its line as `Add to scope notes: "..."` with no join stage and no script path, so it is never checked.

Consumer: every adopter FO whose README lists paseo (Codex workers through Paseo) or another extension whose scope-note instruction names no script, and the observer, which today is the only reader that catches the missing line.
