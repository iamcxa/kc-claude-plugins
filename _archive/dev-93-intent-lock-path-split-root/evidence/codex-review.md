沒有 [P1]/[P2] findings。

- 相對 `--git-dir` 會加上 `state`，解析基準正確；雖未字面正規化為絕對路徑，但 shell 不改 cwd，因此不影響 trap。
- 普通 clone 鎖在 `.git/ship-lock.d`；linked worktree 鎖在其專屬 `.git/worktrees/<name>/ship-lock.d`，仍是每個 checkout 一把鎖。
- release trap 的 ownership 與清理語意未變。
- 測試確實建立 `.git` 為檔案的 linked worktree；舊版會持續 `mkdir` 失敗並約 30 秒後以 exit 6 redden。
- 兩個新 blob 均通過靜態語法解析；唯讀環境下未執行完整 contract test。

```text
剩餘: 無
下一步: 無（你）
可收線: 未確認
```


