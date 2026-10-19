---
title: "kc-decision-log P1: read the same scoped decision across clients"
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
source: https://github.com/iamcxa/kc-claude-plugins/tree/b75e10c15270c9e8bec4be1ebcf25c1e1b16ec24/docs/journey/kc-decision-log
---

Deliver the selected P1 outcome: 使用者指定自己的決策 repo 後，Claude、Codex、dot 均以已驗證身分，讀到相同精確版本與正確層級的裁示，或一致保留疑義。

## Scope

Planning source: docs/journey/kc-decision-log/journey.yaml at b75e10c15270c9e8bec4be1ebcf25c1e1b16ec24; selected release P1, stories S01, S02, S04, S10, S11. The merged map owns story requirements; the guarded Development Brief will supply the admission snapshot. No scalar journey-story is invented for this integrated outcome.

The Captain explicitly selected latest dev2 / Pilot and P1 on 2026-10-19, requested publishing and merging the map before starting, and then answered the investment-limit question with 「1-3天」. Appetite is at most 3 days, with the original 1–3 day range retained; this is not a delivery estimate or deadline. Integration and validation belong in the estimate. Estimate and guarded handoff are pending factual investigation; do not advance from backlog on that absence.

- 明確來源配置及使用者隔離
- 總指揮／工程層級與適用範圍的讀取邊界
- 真實跨客戶端身分驗證與原文／有效判定
- 含 commit 的可重現引用
- 上層獨立庫與工程 repo 分開配置、各自授權讀取及回報 commit；來源不可讀保留未知
- 沿用 dev2 原始格式／狀態；區分原狀態與服務保守有效查詢，不強制新欄位或改寫 Legacy

Product non-goals from the accepted map:
- 寫入 MCP、PR 建立或合併
- 自動 Git 更新與背景監控
- 搬移產品 code 或私人 ADR
- 把單一使用者登入成功視為跨客戶端已相容

The product's no-write-MCP/PR non-goal does not prohibit the authorized development PR workflow. Do not create credentials, broaden source access, modify the existing Sites entry/deployment, open host rooms, auto-bridge agents, or import private ADRs. Later releases remain candidates. A map or ADR does not grant external action authority.

Stop conditions: missing required existing source or access, cross-client authentication failure, unproven isolation, an estimate exceeding 3 days, or an unavoidable change to accepted value/constraints returns a concrete planning delta to the Captain. Existing host refactoring is coordinated independently; no concurrent host mutation is authorized here.

## Acceptance criteria

**AC-1**: 用兩個合成使用者各自的獨立決策庫，證明不可讀到另一人的索引、原文或 source metadata。
Verified by: Two independently authorized synthetic identities and separate sources; verify allowed reads and negative access cases without copying private data.

**AC-2**: 在 Claude、Codex、dot 實際登入查詢同一合成 ADR；回傳 repo、層級／範圍、ID、commit、digest 一致；無法登入的客戶端明列失敗。
Verified by: Real authenticated queries from Claude, Codex and dot against the same synthetic ADR; preserve exact responses and failure limits.

**AC-3**: 在分開的合成上層 repo 與工程 repo 放置同號或同 key ADR，分別經已配置且授權的來源讀取、回報各自 commit；工程記錄不能 supersede 上層，Proposed／衝突／壞鏈不被 resolved。工程或上層來源不可讀時保持未知，不把原文搬到另一庫當替代。
Verified by: Separate authorized synthetic upper-level and engineering repositories with collisions, invalid chains and unreadable-source cases; record each source commit.

**AC-4**: snapshot 固定在 D0 時，來源已到 D1 也只宣稱 D0；引用可重現 D0，不宣稱最新。
Verified by: A fixed D0 host snapshot with source D1; reproduce D0 and confirm responses never claim D1.

**AC-5**: 每個客戶端都能查核目前經驗證的使用者／授權空間與選定來源；切換空間或來源不匹配時清楚拒絕，客戶端自稱的名稱不能成為權限依據。
Verified by: Inspect verified caller/space/source from each client and test mismatched identity or source; client labels must not grant access.

**AC-6**: 合成 dev2 原生 docs/adr、Accepted 無 Decision key 及 Legacy 舊原文，來源／原狀態照實呈現；保守 effective 無法判定時另標 unresolved／能力限制，不改 Accepted 或要求新增服務欄位。Legacy 不冒充新裁示；adapter 路徑／舊格式不足需明列失敗，不以改寫原文掩蓋。
Verified by: Use synthetic native dev2, missing-key Accepted and Legacy fixtures; compare raw state with conservative query output and retain unsupported cases.

## FO alignment

Direction alignment is needed before ideation only if the evidence-based estimate, required source/access or full P1 outcome does not fit the accepted three-day upper limit. Preserve the existing D1–D4 decisions; do not restart settled design questions. Formal Development Brief / journey-handoff preparation is in progress, not passed.
Surfaces: ui
Visible change: Each authenticated MCP client can identify its caller and source, read precise decision text and state, and see unresolved or denied outcomes honestly.

The MCP client response presentation is a ui surface in this workflow. Ideation must provide its corresponding proposal and a readable preview. This classification does not approve a new custom webpage UI, frontend product or database schema; a necessary scope or persistent schema change returns for surface/profile review before dispatch.
Release review: P1 changed, signal 1 (new task preparation for the selected release); before first implementation dispatch, perform the existing fresh release review and derive the smallest batch from its output. This task has not yet been formally admitted or mapped into story-progress frontmatter.

## Route-back conditions

If the accepted outcome, non-goals, required authority, source availability or investment premise changes, stop dependent work and return the changed premise, affected acceptance evidence and recommended change. Do not silently reduce three clients to one, fabricate a usable dependency or bypass the guarded handoff.
