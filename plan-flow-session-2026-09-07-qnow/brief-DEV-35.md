# DEV-35 驗證 Conductor Cloud headed Playwright 執行環境

## 目的

確認 Conductor Cloud Linux sandbox 能執行 QNow hosted acceptance 所需的 Playwright 1.56.1 headed Chromium；這是正式三角色 journey 的環境前置，不是產品驗收本身。

依賴未預裝屬於環境佈建工作，不視為平台能力 blocker。先在 Conductor Cloud 預先提供或安裝所需相依，再執行本 ticket 的 preflight 驗證。

Conductor Cloud 的環境設定或 image 負責提供系統 Chrome 與 Xvfb；repository 的可重複 setup script 負責鎖定 Playwright 版本、安裝 workspace 依賴與執行 preflight self-check。

## 範圍

* 固定 `spacedock-ensign/qnow-next-hosted-staging-qualification@36a8bef4a3a6e5e8acbe3bf552e06d2e7765bab3`。
* 區分 base image 預裝與 workspace 內後續安裝。
* 驗證 QNow 獨立 `npm ci`、Playwright-managed Chromium、Xvfb 與 `headless: false`。
* 建立三個 isolated browser contexts，只開 `data:` 頁面，不連 provider。
* 執行 committed self-check，要求 `providerCalls: 0`。
* 驗證 browser／Xvfb owned process remainder 為零。

## 驗收

* 回報 `CLOUD_HEADED_PLAYWRIGHT_READY` 或 `CLOUD_HEADED_PLAYWRIGHT_INSTALLABLE`。
* 若 blocked，留下安全 failing phase 與缺少能力。
* 不讀取／輸出 credential value，不部署，不建立 users／rows／env vars。
* Supabase 不是 QNow gate；generic setup 若曾自動啟動，僅記錄 side effect，不使用它。

## 不包含

Netlify deploy、hosted journey、Supabase 診斷、產品資料 mutation。

## Accepted outcome

The Conductor Cloud headed-Playwright preflight in PR iamcxa/qnow#1175 is merged with a review disposition and an e2e result recorded; its preflight script is runnable from main and is the environment gate DEV-37 cites.

## Non-goals

- Running the three-actor journey (DEV-37).
- Installing dependencies into the cloud image beyond what the PR already does.

## Acceptance criteria

* **AC-1** `gh pr view 1175 --repo iamcxa/qnow --json state --jq .state` prints MERGED and `review/disposition-1175.json` exists in the batch record.
* **AC-2** The preflight command the PR body names runs at the merge head in a Conductor cloud workspace and its log with exit 0 is recorded.
* **AC-3** `git log --oneline origin/main | grep -c '#1175'` prints 1.

Re-verified: `gh pr view 1175 --repo iamcxa/qnow --json state --jq .state | grep -q OPEN` exit 0 2026-09-07
