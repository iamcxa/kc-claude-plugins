結論：狹義保證成立——每個完全相同的 claim，正常 production entry 最多呼叫一次 `conductor workspace create`。它仍不保證 provider 只產生一個 workspace。ship-flow 尚有三個 commission blocker。

## 七項 blocker

| 前次 blocker | 狀態 | 證據 |
|---|---|---|
| 1. state sync fail-open | **Closed** | `holder.sh:11-15`、`intent.sh:13`；fetch、dirty、non-FF、malformed均exit 6 |
| 2. production bypass flags | **Closed** | `fenced-dispatch.sh:4-8`；只剩不削弱保證的pause/delay |
| 3. `CREATE_FAILED`被adopt | **Closed** | `fenced-dispatch.sh:18-23`；失敗或非法ID保持unresolved |
| 4. token read-back | **Closed** | `fenced-dispatch.sh:21-24`；按workspace ID讀回並精確核對含token的名稱 |
| 5. unfenced／覆寫adopt | **Closed** | `intent.sh:24-28`；重新sync、fence、拒絕不同既有ID |
| 6. POC硬編碼路由 | **Open** | `fenced-dispatch.sh:7,11,18`；已改為參數，但未證明它們來自approved receipt，也未寫入intent供reconcile核對 |
| 7. AC-5 contract mutation | **Open** | `kc-dev-flow-contract-test.py:1886-1891`；mutation仍pending |

另有一個直接錯誤：diff刪除了README舊段，卻沒有加入測試要求的新句子。`docs/dev/README.md:496`目前是空白；正常contract test應失敗。若測試通過，提供的diff或執行結果不一致。

## 新 [P1]

1. **平行dispatch會競爭同一Git checkout**

   - `intent.sh:13-23`
   - `commit_push`使用`git add _intents`，沒有程序鎖。兩個不同claims並行時，一個commit可意外包含兩者；另一個no-op失敗，留下「已有intent但從未create」。
   - 修正：對整個state checkout的`sync → write → commit → push`加單一程序鎖。不能只做per-claim lock，因為Git index與branch是共享的。

2. **intent沒有綁定實際dispatch內容**

   - `intent.sh:20-23`
   - intent只保存claim、token、holder、writer；沒有project、base branch、message hash。
   - 後果：reconcile可adopt名稱正確但project或task錯誤的workspace。
   - 修正：intent加入project ID、base、message SHA-256及approved receipt hash；create與reconcile都核對。

3. **read-back宣稱核對project，實際只核對name**

   - `fenced-dispatch.sh:21-23`
   - comment寫「name, project, token」，Python只檢查`name`。
   - 修正：核對workspace project ID；若API回傳branch或首則訊息hash，也一併核對。

4. **message-file仍有讀取競爭**

   - `fenced-dispatch.sh:7,18`
   - intent提交後、CLI讀取前，caller或另一程序可修改檔案。
   - 修正：先複製到0700臨時目錄，計算hash，將hash寫入intent，再把該不可變副本交給CLI。

## Commission 判定

仍阻擋：

1. README contract文字缺失，AC-5未完成。
2. state checkout沒有全域程序鎖，與計畫中的平行dispatch直接衝突。
3. intent與read-back未綁定project、base、message及receipt hash。

修完後可 commission，但承諾必須保持狹義：

> 每個canonical claim，production entry最多發出一次workspace-create呼叫；模糊結果阻塞並等待人工reconcile。

```text
剩餘: README/AC-5、state checkout鎖、dispatch內容綁定
下一步: 修正三項後重跑兩個平行claim與message突變falsifier（你）
可收線: 否
```

tokens used: 746774
