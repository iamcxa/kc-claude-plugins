---
title: Evidence is declared public before it reaches the public state branch
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「放行，另開任務（建議）」 (host question dialog, 2026-11-13), answering 「#854（派工結束時封存證據、刪暫存）的本機審查報了一個高嚴重度問題：封存時沒有機械檢查證據是不是公開的，私有內容若被 worker 放進證據資料夾就會留在公開分支。要不要先放行這一項、另開任務處理，讓 #854 進第三次驗證？我建議放行。獨立審查者判定：這不是實作缺陷，是你當初核准的做法（私有證據靠派工文字要求 worker 不封存）本來就沒有機械檢查；這次改動沒有新增任何自動上傳的路徑，也沒有發現實際外漏。放行等於接受：這個缺口暫時留著，我開一張任務「證據進公開分支前要先聲明是公開的」。」
- Bite: RoboRev jobs 1814 and 1815 on PR 854 candidate c429ab181 (High): the close-out step keeps every file under a task's evidence folder with no check that it is public. An engineering-reviewer probe the same day confirmed an unclassified file is compressed and kept, found no automatic publication path and no actual exposure, and classed it as a gap in the approved design (private evidence is excluded by dispatch instruction only), not a build defect.
- Related: the Captain's ruling that the repository is split into a private development repository and a public distribution repository in a second phase; the design says whether this task is still needed after that split.
- Open for the design: a per-file declaration bound to a content digest, checked before publication; what happens to evidence already archived; the reviewer's note that a declaration cannot detect a false one.
- Non-goals: scanning file contents for secrets; rewriting state history.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- An evidence file with no public declaration is refused before it is kept, and a declared one is kept as today. Return to the Captain if the split into two repositories removes the need.

## FO alignment

Alignment: needed at ideation; whether this is built before or after the repository split is the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
