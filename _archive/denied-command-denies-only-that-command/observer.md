violation | rule: "FO names the amendment in the next dispatch's checklist." (Captain amendments) | evidence: "absent" (04b1a9133，implementation-1-message-4 未點名修正案 2；該修正案至 82aa6626a 才加入)

violation | rule: "`<package>/scripts/role_triggers.py` lists calls owed." (Stages) | evidence: "next: denied-command-denies-only-that-command has 0 validations with a Material or Needs decision finding and 2 replacing amendments: before the next step, answer: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?" (f99630408，腳本輸出；見 Coverage 限定)

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: question "決定：第 21 批這五張要不要進設計階段。"；reason "answering 「決定：第 21 批這五張要不要進設計階段。" (13ab8217e，完整比對吻合)

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: question "決定：要不要核准"；reason "answering 「決定：要不要核准" (76e89c237，完整比對吻合)

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: question "決定：合併 #842（Paseo 擴充加一句"；reason "answering 「決定：合併 #842（Paseo 擴充加一句" (ab879a146，完整比對吻合)

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: question "決定：合併 #842（Paseo 擴充的那句話"；reason "answering 「決定：合併 #842（Paseo 擴充的那句話" (f99630408，完整比對吻合)

ok | rule: "When the Captain chooses differently from the recommendation, FO writes" (FO steps: review findings) | evidence: "Override: recommended merging the head as written; Captain chose sending it back to reword the rule so it does not name Codex alone; area: worker permission denials." (ab879a146)

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog／ideation) | evidence: "seed fields and FO alignment recorded"; "design surfaces presentable" (3c79dd97、b86cee46、fc9bb708；三次重放均退出 0)

ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: "reference:denied-command-denies-only-that-command:validation:attempt-1:revision-1:item-2"; "2026-11-11T06:55:50Z"; "cdb99da0e52e8b5cad3a7be04658dc282432b644" (6977fa45c，雜湊、版本與兩項理由吻合)

ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: "reference:denied-command-denies-only-that-command:validation:attempt-2:revision-1:item-2"; "2026-11-11T07:58:18Z"; "d22a01d5e8d334f6f4e8a2c5853f8f6abeddc89a" (897cd4016，同上)

ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: sufficiency "in four of four valid candidate replay runs"／"the one changed sentence makes sending the denial reason the default"；necessity "kc-dev-flow-2/extensions/paseo/EXTENSION.md changes against origin/main, one sentence" (6977fa45c／897cd4016)

ok | rule: "never mark a peer claim direct" (Extensions／peers) | evidence: "「要」, relayed, not a ruling here" (f99630408)

ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish" (FO steps: review findings) | evidence: "FO declines F1 Polish: extra explanation under amendment 2's Design line" (5f7a2da39，摘要綁定候選版本並記錄理由)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "error connecting to api.github.com" (merge_audit；外部合併紀錄不可讀)

Coverage: 固定窗口 707c1431a..f99630408。完整讀取規則、任務歷史、裁決帳本、五份簡報及派工紀錄；抽讀變更處的工人報告與驗收紀錄，不評產品。role_triggers 退出 0，但仍輸出上述提醒；簡報 2 已有「Step back, FO's answers after two replacing amendments」，不能據此宣稱未回答。merge_audit 未經管線執行，立即保存退出碼 2；state fetch failed，僅讀本地參照，可能過時或缺漏。缺失紀錄可能是聊天核准或其他儲存庫的狀態。無法核實外部審查輪數、合併、聊天授權及提交命令；設計匯出重放未執行 Git scope check。
