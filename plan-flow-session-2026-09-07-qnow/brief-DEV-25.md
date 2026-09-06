# DEV-25 驗證 Netlify DB、Auth 與 RLS 租戶隔離

以最小端到端驗證正式基礎：Netlify Auth 身分與 claims、Hono API 的 tenant／門市／subject context、Netlify DB migration、RLS、連線池 context 清理與稽核。

驗證車主手機 OTP 的相容性：手機作為主識別、發送與驗證 OTP、伺服器可驗證的電話證據、session 建立／refresh／revoke、Expo Web 與 tenant／role claims。不可假設 Netlify Auth 與既有 Supabase OTP 行為等價；若不相容，記錄可行 provider seam 與需人工決策的過渡方案。

驗收：跨租戶資料無法讀取或寫入；角色與門市範圍在 API 與資料庫層皆被拒絕；context 不因連線重用洩漏；migration、測試與部署流程可在 preview 或 staging 執行。

## Accepted outcome

The Netlify DB / Netlify Auth / Hono tenant-context / RLS / phone-OTP verification that PR iamcxa/qnow#1177 carries is merged to main with a review disposition and an e2e result recorded in the qnow batch record; the existing tests in that PR are the evidence.

## Non-goals

- Re-implementing or extending the verification (the PR is taken as built).
- Supabase OTP parity beyond what the PR already asserts.

## Acceptance criteria

* **AC-1** `gh pr view 1177 --repo iamcxa/qnow --json state --jq .state` prints MERGED and the batch record's `review/disposition-1177.json` exists with a disposition.
* **AC-2** The PR's own test command (named in its body) is run by the e2e station at the merge head and its exit code is recorded in the batch record.
* **AC-3** `git log --oneline origin/main | grep -c '#1177'` prints 1.

Re-verified: `gh pr view 1177 --repo iamcxa/qnow --json state --jq .state | grep -q OPEN` exit 0 2026-09-07
