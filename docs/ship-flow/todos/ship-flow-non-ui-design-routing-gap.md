---
tid: ship-flow-non-ui-design-routing-gap
captured_at: 2026-05-04T10:50:00Z
status: pending
source_pitch: "001"
addressed_to: ship-flow-maintainer
priority: medium
---

# ship-flow design stage doesn't route non-UI contract design

## Maintainer-eval prompt (drop into a fresh-context ship-flow specialist agent)

```
ship-flow design stage 的 trigger 條件目前偏 UI（affects_ui / *.tsx|*.css|*.html
glob / domain registry classify），對 plugin-internal contract design 有覆蓋盲點。

具體 case：kc-claude-plugins/docs/ship-flow/001-selector-grammar-alignment

這個 pitch 是純非 UI 修復（agents/*.md prompt + compiler/*.js + fixtures），但
spec 內含一個未拍板的 contract 決策——選哪一種「mapper → agent-browser native
selector vocabulary」當 canonical：
  (1) find role <r> --name "<v>"  agent-browser 子命令字串
  (2) [role="<r>"][aria-label="<v>"]  純 CSS attr
  (3) {role, name}  結構化欄位

shape 階段只拍了 high-level「走 issue option 1+3 hybrid」，沒拍 selector grammar
具體形式。Plan worker 在 T1.2 自己選了 (1)，沒走 design gate。如果走了 design：
captain 應該看到 trade-off table 後拍板，這是真實的 design intent decision。

當下系統的 routing 結果：
- affects_ui: false                                   ← 觸發 1 不亮
- domain: 未設（registry-resolve.sh 不存在於此 repo）  ← 觸發 2 跳過
- architecture-impact: 無 *.tsx/*.css                  ← 觸發 3 不亮
- --design flag: 未下                                  ← 觸發 4 不亮
→ design-skipped: true（per skip-when: "!affects_ui && !domain"）

Gap 本質：design stage 預設「design = visual / render / token」。對「agent ↔
agent contract」「schema / grammar / vocabulary」這類 non-visual design intent
沒有 routing 路徑。Domain registry 理論上可承擔，但需要新增 domain 類別
（如 agent-contract / api-vocabulary / cross-component-schema）+ trigger config。

請你評估改進方向，至少回答：

1. 這是不是 ship-flow 該長出的能力？或本來就應該由 captain `--design` 補位？
2. 改 trigger 邏輯（加 contract-domain 自動分類）vs 改 design stage 範圍（明確擴
   到 non-UI contract）vs 兩者都要——優先序怎麼排？
3. 有沒有更輕量的中間態：例如在 shape 階段就強制把「未拍板的 contract 決策」明
   列在 spec，plan worker 看到該欄位非空時 BLOCK 等 captain 補拍板，不一定要進
   完整 design stage。
4. 命名：non-UI design 應該還叫 design 還是另闢一個 stage（如 contract / API-
   shape / interface-design）？跟現有 design stage 共用 ship-design skill 還是分
   家？
5. 既有 plugin-internal pitch 的 case 多嗎？這 gap 在 spacedock-ui dogfood 裡是
   否也曾命中但被忽略？

同時請評估 001-selector-grammar-alignment 這個 case 的最小修補路徑——「事後追認
design intent」vs「退回重跑 design」哪個 ROI 高。
```

## Evidence artifacts

- `docs/ship-flow/001-selector-grammar-alignment/spec.md` — pitch with the contract decision in scope but no design hand-off
- `docs/ship-flow/001-selector-grammar-alignment/design.md` — retrofit design.md authored AFTER plan landed, with Retrofit notice header naming this gap
- `docs/ship-flow/001-selector-grammar-alignment/plan.md` — T1.2 originally locked the selector vocabulary unilaterally (pre-retrofit); plan was amended to reference design.md once captain confirmed Candidate 1
- This todo — captures the maintainer-eval prompt and outcome trail

## Captain action chosen for THIS pitch

Option A (full retrofit) — over Option B (lock decision silently in plan T1.2). Reason: maximize "expose gap" evidence value over single-pitch time savings. Decision date: 2026-05-04.
