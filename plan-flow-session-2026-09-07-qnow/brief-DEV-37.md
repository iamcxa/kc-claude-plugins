# DEV-37 執行 QNow 三角色 hosted claim／readback 驗收

## 目的

完成 QNow hosted infrastructure 已通過後仍缺少的產品驗收：以三個真實 hosted Identity actors 證明 assignment、tenant isolation、exact-once claim race、遺失回應後 readback，以及完整清理。

## 前置

* DEV-35：Conductor Cloud headed Playwright preflight 通過。
* DEV-36：package-scoped ESM full runner 通過所有零 provider gates。
* fresh authorization receipt、exact site／rollback／runtime／zero remainder 綁定。

## 單次執行範圍

* 最多 1 個新 candidate、1 次 deploy；禁止 retry 或第二次 deploy。
* 六個 production/functions secrets 僅在 memory 中持有；readback 採 safe structural receipt。
* 建立 3 個 synthetic non-PII Identity users、3 assignments、2 tenants、2 branches、1 scheduled order。
* headed browser 建立 3 個 isolated contexts。
* 驗證 missing/malformed identity denial、inactive assignment 403、tenant-B denial。
* reception A/B 同步 claim，結果必須恰好一次 HTTP 200、一次 HTTP 409。
* 轉送真實 winner POST 後只丟棄 browser response；不得重送 POST。
* winner 必須由 Mine、Detail 與 reload 讀回；DB 恰好 1 owner、1 immutable audit。
* safe canary scan 不得出現 secret、PII、URL 或 raw provider error。

## 清理驗收

first failure 後只允許 cleanup：

1. 刪除／reset exact run-owned rows 與 audit，census 0。
2. 刪除 exact 3 users，census 0；stale token 回 401。
3. 刪除 exact 6 environment keys並證明 absent。
4. pointer 綁定正確時 restore admitted bootstrap-free rollback。
5. 刪除 exact new candidate，API NotFound、immutable routes unavailable。
6. link、clone、evidence、QNow containers 與 owned processes remainder 0。

## 完成條件

產出 revision-bound、secret-safe acceptance receipt，狀態可交給獨立 validation；本票不自行宣告正式產品上線。

## 不包含

OTP／invitation、客戶 SMS、LINE、credential rotation、snapshot restore、Supabase、production rollout、第二個 order 或第二輪 journey。

## Accepted outcome

One recorded run, in a Conductor cloud workspace whose environment carries the six production/functions secrets, executes the 單次執行範圍 above exactly once (one candidate, one deploy, no retry) and produces the revision-bound, secret-safe acceptance receipt named in 完成條件, then performs the 清理驗收 steps to zero remainder; the receipt and the run log are stored in the qnow batch record and handed to independent validation. This ticket does not declare production launch.

## Non-goals

- Everything listed under 不包含 above.
- A second deploy, a retry, or a second journey — a first failure ends the run and only cleanup follows.

## Acceptance criteria

* **AC-1** The run log records exactly one candidate and one deploy, the claim race outcome as one HTTP 200 and one HTTP 409, and the winner read back from Mine, Detail and reload; exit 0.
* **AC-2** The acceptance receipt file exists in the batch record and a safe canary scan of it (script named in the run) prints zero hits for secret, PII, URL or raw provider error patterns.
* **AC-3** The cleanup census script prints 0 for rows, users, environment keys and containers, and the stale token check returns 401; each logged.
* **AC-4** `gh pr view 1174 --repo iamcxa/qnow --json state --jq .state` and the same for 1175 print MERGED before the run starts (prerequisite gate).

Re-verified: `test -f /dev/null && gh api repos/iamcxa/qnow/contents/docs/evidence --jq 'map(.name)|join(" ")' | grep -qi 'acceptance-receipt'` exit 1 2026-09-07
