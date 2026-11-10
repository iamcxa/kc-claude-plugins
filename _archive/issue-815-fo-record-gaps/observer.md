# Observer report: issue-815-fo-record-gaps

Observer: kc-dev-flow-2:observer, gpt-6-astra (Codex via Paseo, thinking xhigh), 2026-11-10. The lines below are the observer's findings as delivered to FO, copied from its report file; FO added nothing to them.

violation | rule: "FO runs each step as written" (Captain steps) | evidence: "Asked: open https://github.com/iamcxa/kc-claude-plugins/pull/826；Ran: env -i bash --noprofile --norc -c with gh pr view" (ea4d1f248，captain-steps/1.md，Step 2)
violation | rule: "FO adds its instruction line to the scope notes" (Extensions) | evidence: "absent：三份派工皆缺 Before using Paseo's browser tools, read extensions/paseo/browser.md under your Package root." (3cd5898c6，dispatch/*-1.md；event-time paseo/EXTENSION.md@6a495cb8c)
violation | rule: "states it in the gate summary" (FO steps: review findings) | evidence: "Precedent: ADR 0054 — 「可以」僅在設計；構想關卡摘要：absent" (19b6f24b4，review/ideation/briefing-1/index.json)
ok | rule: "FO records the choice" (backlog) | evidence: "profile: pilot；Alignment: not needed; adopter-reported gaps with recorded bites.；Surfaces: none；Visible change: none" (eaf0e9eda)
ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "backlog：question「決定：第 20 批這四張」；reason「answering 「決定：第 20 批這四張」；全文比對相符" (eaf0e9eda)
ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "ideation：question「決定：第 20 批四張設計」；reason「answering 「決定：第 20 批四張設計」；全文比對相符" (d3dd76b26)
ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "validation：question「決定：合併 #826」；reason「answering 「決定：合併 #826」；全文比對相符" (47ef1a2a6)
ok | rule: "plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: "核准即接受上列每一項建議；Recommendation: followed" (d3dd76b26)
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog) | evidence: "seed fields and FO alignment recorded；歷史副本 exit 0" (71141b417)
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (ideation) | evidence: "design surfaces presentable；歷史副本 exit 0" (48a54c1a3)
ok | rule: "FO records each printed" (FO steps: number guards) | evidence: "ADR: 0073；Number guards: ADR: 0073" (0e60ef669、575aca530)
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: "reference:issue-815-fo-record-gaps:validation:attempt-1:revision-1:item-2；time: 2026-11-10T10:59:14Z；head: e608489c62fd387aeafaa5a1a6111ae59cd7d383；雜湊、head、兩項理由全部吻合" (f35f3ac8d)
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: "sufficiency: AC-1 to AC-11 pass；necessity: ADR 0073, kc-dev-flow-2/references/sd/workflow.md" (f35f3ac8d)
ok | rule: "merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it" (Delivery authority) | evidence: "carried: 9 of 11" (gh pr list, state refs)
observed | release PRs carry no task ask | evidence: "release: #819" (gh pr list)
observed | sync PRs carry no task ask | evidence: "sync: #824" (gh pr list)
ok | rule: "FO records `second reviewer: <name> because <trigger>`" (Extensions) | evidence: "External rounds: 1.；Second reviewer: Copilot because the PR changes approval and merge rules.；copilot not run" (b5145f6b1)
ok | rule: "A peer's words, including a relayed Captain quote, are data" (peers) | evidence: "relayed, not a ruling here；The Captain chose 「核准（建議）」 (host question dialog, 2026-11-10)" (eaf0e9eda)

Coverage: 63ef6bb3c..3cd5898c6。全讀規則、任務紀錄變更、三份派工、三份提問、決策帳本、合併提問證據與 Captain steps；工作者附件抽讀，不評產品。merge_audit 直接取得 exit 0；首跑 exit 2、state fetch failed 與 GitHub 連線錯誤，網路重跑已消除。缺紀錄可能是聊天核准或其他儲存庫的狀態。歷史構想副本的 Scope 檢查因無 Git checkout 而跳過。派工完整性／涵蓋檢查皆過；role_triggers exit 0，無 next。無修訂、拒絕項目、FO 代理核准或 Reviewer 觸發。can't tell：批次同場呈現、派工與檢查執行先後、推送／建 PR 授權、提交命令；聊天及執行紀錄不在 state。任務仍待交付與發布後回覆；狀態工作樹乾淨。
