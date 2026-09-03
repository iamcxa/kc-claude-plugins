結論：Run C通過拒絕結構，但discovery assignment只完成一半。Run A/B暴露更嚴重的錯誤：plan-flow接受了「不做runtime enforcement」的方案，卻宣稱ship-flow會enforce三項保證。

## [P0] Outcome與方案互相矛盾

- **判定：unsound**
- `run-A Station 2, Alternative A`：只寫README與pins，明載「no enforcement」。
- `run-A/B User value`：卻說「because ship-flow enforces…」。
- `run-A Station 3`：以Kent不再提問作成功指標。

Kent可能因文件而停止提問，但runtime仍未執行任何保證。這會把降低監督誤判成安全成功。

最小修正二選一：

- 選真正執行三項保證的Alternative B；或
- 把outcome限縮為「Kent能找到三項policy」，不得使用`enforces`，也不得把停止安全提問當成功。

## [P1] Run C

- **拒絕：sound**
- `run-C REFUSAL`正確列出demand、specific human、observation三個缺口。
- 明確沒有profile、Project、Issues或receipt。
- 停在Seam 1，沒有硬把材料轉成build plan。

- **Discovery assignment：needs a falsifier**
- `run-C Discovery assignment`要求「ask」後帶回「observed doing」；訪談不能產生觀察證據。
- 「是否願意付費」仍是口頭意向，不是demand behavior。

可執行版本應是：

> 本週到一間店或開一次screen-share，不提示地看一位具名店主完成一筆實際客戶追蹤；記錄工具、步驟、時間與漏失。接著提供一個single-shop人工試辦，要求本週實際付款或投入真實資料。

## [P1] Run A與Run B比較

- **「borrowed多改2–3句」：sound，僅限adapter成本**
- Borrowed templates確實需要轉成repository Brief shape。

- **「fallback成本為0且分析等價」：needs a falsifier**
- fallback本來就是依Brief欄位反向撰寫；零rewrite是定義造成的結果，不是品質證據。
- Run B重用Run A的Station 2答案，Issue bodies也直接宣稱相同。
- 同一worker已讀過borrowed skills，再寫／執行fallback；不是獨立比較。
- 一個requirement得到相同cut，不能證明兩條路普遍等價。

方向應採：

> **fallback-with-borrowed-as-checklist**

Fallback是唯一產生artifact的路徑；installed borrowed skill只能作可選檢查，指出漏掉的persona、hypothesis或split pattern，不得另產一套需要轉譯的正文。

## [P1] User value line

- **判定：unsound**
- `run-A/B User value`前半「Kent stops re-asking…」是observable outcome。
- 後半「because ship-flow enforces…」是solution mechanism，而且與「no enforcement」直接矛盾。

改為：

> `User value: Kent completes the next three ship-flow UATs without re-deriving the three declared guarantees from each PR.`

若真正要保證安全，outcome必須量測runtime拒絕錯誤候選，不能只量測Kent是否停止提問。

## [P1] dialectic.md授權

- **Station 1：sound**
- 問具體人物、現況成本及事實／假設，主要來自MIT office-hours原則，沒有明顯複製pm template。

- **Station 2：sound**
- 是office-hours Q1–Q4、Phase 3的濃縮；MIT來源已標示。

- **Station 3：unsound**
- 三題依序對應pm-skills的If/Then、Tiny Acts、Validation Measures。換字仍是明顯改編，不符合「never vendor」的自訂界線。

- **Station 4第1題：unsound**
- `step, rule, data type`直接映射pm splitting的Workflow Steps、Business Rules、Data Variations。
- 「own wording」不會使改編失去CC BY-NC-SA來源性。

最小修正：重新從kc-dev-flow自身需求獨立寫問題；或者承認CC BY-NC-SA衍生並接受其授權條件。不要在public fallback中保留pm patterns的壓縮清單。

## [P1] Refusal seam位置

- **判定：unsound**
- `dialectic.md Refusal seam`放在Station 2提交persona前。
- 但Station 1已經要求borrowed problem-statement產生persona、because與feel，Run C也先生成了這些欄位。

正確順序：

1. Station 0收集材料。
2. WHY evidence與refusal check。
3. 通過後才生成正式problem statement。
4. 再進goal與Issue cut。

Station 1可先產生hypotheses，但在refusal通過前不得稱為Brief輸出。

## 唯一 front-half blocker

plan-flow沒有拒絕一個**無法因果達成User value的chosen approach**。Input A已實際命中：`no enforcement`方案通過，卻產生`ship-flow enforces`的outcome。

在commission前，必須加入一個premise falsifier：

> 對每個chosen approach，移除其實作後重新問：accepted outcome是否仍可能成立？若方案沒有建立聲稱的mechanism，就拒絕進入Issue splitting。

```text
剩餘: 修正Input A的因果矛盾、fallback授權內容與refusal順序
下一步: 讓DEV-89以「no enforcement卻聲稱enforces」作premise refusal falsifier重跑（你）
可收線: 否
```

tokens used: 1021730
