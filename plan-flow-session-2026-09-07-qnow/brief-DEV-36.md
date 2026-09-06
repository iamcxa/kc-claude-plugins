# DEV-36 建立 QNow package-scoped ESM hosted journey runner

## 目的

把 Cycle 84 的 `/tmp/*.ts` runner 失敗收斂成 repository 內正式、可測試、可重複呼叫的 ESM entrypoint，避免 tsx 將 out-of-package TypeScript 判為 CommonJS。

## 範圍

* 在 `qnow-next` package 內新增 `.mts` 或 `.mjs` full-runner entrypoint 與 npm script。
* 只組裝既有 secret-safe environment、Netlify session、fixture controller 與 headed journey adapters。
* 使用 package-scoped ESM semantics；禁止依賴 `/tmp/*.ts` top-level await。
* 加入零 provider contract test：module 可 instantiate、Playwright CommonJS-compatible load 可用、provider clients／browser／deploy 都未執行。
* 保留 exact revision、one-deploy、first-failure cleanup 與 safe receipt contract。

## 驗收

* 從任意 cwd 呼叫正式 npm command 皆可完成 self-check。
* `providerCalls: 0`，沒有 credential／URL／PII／raw error 輸出。
* package、type-check、Node 24 artifact、fresh-clone parity 與 relevant gates 通過。

## 不包含

本票不執行 Netlify deploy 或正式三角色 hosted journey。

## Accepted outcome

The package-scoped ESM hosted journey runner in PR iamcxa/qnow#1174 is merged with a review disposition and an e2e result recorded; its npm script runs from main with zero provider gates, as the PR's 驗收 states.

## Non-goals

- Adding journeys or actors beyond the runner entrypoint.
- Any change to secrets handling.

## Acceptance criteria

* **AC-1** `gh pr view 1174 --repo iamcxa/qnow --json state --jq .state` prints MERGED and `review/disposition-1174.json` exists in the batch record.
* **AC-2** The runner's npm script named in the PR body runs at the merge head and exits 0 with its log recorded.
* **AC-3** `git log --oneline origin/main | grep -c '#1174'` prints 1.

Re-verified: `gh pr view 1174 --repo iamcxa/qnow --json state --jq .state | grep -q OPEN` exit 0 2026-09-07
