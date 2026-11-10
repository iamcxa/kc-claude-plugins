violation | rule: "When the Captain chooses differently from the recommendation, FO writes" (FO steps: review findings) | evidence: "要維持 5 次先交付"／"Captain: 「這張就做到 7 次」"; "Override:" absent (4d8af48649b2)
violation | rule: "Send your completion message to `main`" (Stages) | evidence: absent；改寫為 "Your final reply is your completion message: Paseo delivers it to FO when your turn ends." (4d8af48649b2, dispatch/validation-3.md)
violation | rule: "FO runs each step as written" (Captain steps) | evidence: "Asked: open https://github.com/iamcxa/kc-claude-plugins/pull/828"；"Ran: env -i bash --noprofile --norc -c with gh pr view" (4d8af48649b2, captain-steps/1.md)
violation | rule: "`<package>/scripts/role_triggers.py` lists calls owed" (Stages) | evidence: "next: amendment-checked-when-written has 2 validations with a Material or Needs decision finding and 1 replacing amendments: before the next step, answer: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?" (4d8af48649b2；exit 0；同檔已有 "Step back (FO, 2026-11-10, before the third validation")
ok | rule: "A Captain ruling is his reply" (FO steps: review findings) | evidence: backlog「決定：第 20 批這四張」／reason「answering 「決定：第 20 批這四張」；完整比對相符 (7f9e0e1336d6)
ok | rule: "A Captain ruling is his reply" (FO steps: review findings) | evidence: ideation「決定：第 20 批四張設計」／reason「answering 「決定：第 20 批四張設計」；完整比對相符；問題另載「核准即接受上列每一項建議」 (c553d9db99b5)
ok | rule: "A Captain ruling is his reply" (FO steps: review findings) | evidence: validation「決定：合併 #828」／reason「answering 「決定：合併 #828」；完整比對相符 (a3ca50bc324d)
ok | rule: "`Asked:` is required" (Captain amendments) | evidence: "Captain: 「改成 5 次（建議）」"／"Asked: 「決定：「修改驗收條件的檢查」"; "Superseded text:"；"**AC-8** Amended by Captain, amendment 1, and by amendment 2." (4d8af48649b2)
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog/ideation) | evidence: "seed fields and FO alignment recorded"／"design surfaces presentable"；兩次 exit 0 (05b021eb4061／d265939cb127)
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: "reference:amendment-checked-when-written:validation:attempt-1:revision-1:item-2"; "2026-11-10T10:59:48Z"; "864536d1180334fa8a10c1ec7122f2ddf0feea14"；雜湊與文字皆相符 (b5145f6b1c31)
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: sufficiency "state law L4 reports a reused criterion id"; necessity "only kc-dev-flow-2/scripts/laws_check.py, design_surfaces.py, test_laws_check.py" (b5145f6b1c31)
observed | rule: "Reviewer:" (Stages) | evidence: "Reviewer: kc-dev-flow-2:chief-engineer gpt-6-astra 2026-11-10" (4d8af48649b2)
ok | rule: "FO counts rounds and records the count" (FO steps: review findings) | evidence: "External rounds: 2."; "FO declines: F2 of validation-2"; "as Deferred risk judged at d7502656c and unchanged at 864536d11" (3cd9b78be10f)
ok | rule: "merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it" (Delivery authority) | evidence: "carried: 10 of 15" (gh pr list, state refs；純讀補充比對)
observed | release PRs carry no task ask | evidence: "release: #819 #831" (gh pr list)
observed | sync PRs carry no task ask | evidence: "sync: #813 #824 #833" (gh pr list)
can't tell | rule: "merging the full head" (Delivery authority) | evidence: "error connecting to api.github.com"；原稽核未完成 (merge_audit.py)

Coverage: 67ab5711c125..4d8af48649b2。完整讀取規則、歷程、控制區差異、簡報、ledger、綁定紀錄、派工及步驟；工人報告及其大量附件僅抽樣，未判產品內容。原 merge_audit.py 未經管線，退出碼立即保存為 2；warning: state fetch failed; reading local refs; records may be stale or invisible。補充純讀比對另以 GitHub 確認全部遠端狀態參照一致。缺漏紀錄可能是聊天批准或其他儲存庫狀態。批次整體證據、未記錄的授權及派工覆蓋執行無法判定；歷史設計的 scope check 未執行。無 agent:first-officer 決策或 Precedent；狀態工作樹仍乾淨。

自動核准審查拒絕重跑原稽核，因 fetch --prune 會更新或刪除本地遠端參照，違反唯讀範圍；已改用純讀查詢完成補充比對。
