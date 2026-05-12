# Project Creation Flow (Step P)

## Trigger

During triage (Step M or issues flow), when customer needs **cluster around a theme** that has no existing project — or when user explicitly requests a new project.

**Signs a project is needed:**
- 3+ customer needs in the same functional area
- Needs span multiple issues but share a common goal
- User says "這些應該歸在一起" or "這需要一個 project"

---

## Process

### 1. Draft — GATE before creation

**Never create a project without user confirmation.** Present a draft table:

```
📋 Project Draft

| Field          | Value                                      |
|----------------|---------------------------------------------|
| Name           | [descriptive name]                          |
| Lead           | [ask user]                                  |
| Members        | [ask user — API 不支援，需手動加]            |
| Priority       | [suggest based on customer urgency]          |
| Target         | [default: 2 cycles from now, ask user]       |
| Initiative     | [suggest based on existing initiatives]      |
| Customer       | [from triggering customer needs]             |

要建立嗎？Target date 是否需要調整？
```

**Rules:**
- **Target date**: Default suggest = 2 cycles. Always ask user to confirm.
- **Lead**: Must ask — never assume.
- **Members**: Note that API doesn't support this; remind user to add manually.
- **Customer**: Auto-linked via customer need → project (since save_project has no customer field).

### 1.5. Resource Discovery — find existing assets

Before writing description, search for existing resources related to the project scope. Present findings in the draft.

**Search locations (in order):**

| Source | How to Search | What to Find |
|--------|--------------|-------------|
| **E2E mappings** | `Glob: .claude/e2e/mappings/*.yaml` | Page element maps covering project scope |
| **E2E flows** | `Glob: .claude/e2e/flows/*.yaml` | Existing test flows for related features |
| **E2E reports** | `Glob: e2e-reports/*/report.md` | Walkthrough screenshots, verification reports |
| **Notion** | Notion MCP (if available) | PRD, meeting notes, design specs, flow diagrams |
| **Linear documents** | `list_documents(projectId)` on related projects | Specs, research docs from sibling projects |
| **Figma** | Figma MCP (if available) | Design files for relevant pages |

**Present as part of draft GATE:**

```
📎 Related Resources Found

Repo:
- .claude/e2e/mappings/secha-office.yaml — 42 elements mapped
- .claude/e2e/flows/catalog-browse.yaml — existing catalog flow
- e2e-reports/20260314-pr396-walkthrough/ — 6 screenshots of service pages

Notion:
- [PRD 3.3 服務管理] — service management spec

要關聯到 project 嗎？（可建 Linear Document 彙整連結）
```

**Rules:**
- Always search — even if user didn't ask. Resources inform scope and avoid duplicate work.
- Don't dump raw file contents — summarize what's available and how many.
- If repo has `.claude/e2e/mappings/`, it's an E2E-capable project — note which pages are already mapped vs missing.
- Notion/Figma are optional — only search if MCP is available.

### 2. Write description — structured format

```markdown
## Why
一句話：為什麼現在要做這個 project？（業務驅動力，不是技術原因）

## What
核心目標（2-3 條，動詞開頭）

## Scope

### In
- 包含什麼（具體功能 / 流程）

### Out
- 明確不做什麼（避免 scope creep）

## Success Criteria
- [ ] 可驗證的完成條件（給 project lead 判斷 done 用）

## Deliverables
- 具體產出物（檔案、頁面、報告）

## Dependencies
- 依賴的 project / issue / 外部條件（如：等 Mike 提供欄位清單）

## Customer
- 客戶名 + 角色 + 使用場景（補 API 不支援的欄位）

## Existing Issues
- SC-XXX — 應搬入此 project 的既有 issues

## Resources
- 已存在的 E2E mappings / flows / reports（從 Step 1.5 發現）
- Notion 文件連結（PRD、設計稿、會議紀錄）
- Figma 設計稿連結
```

**Format rules:**
- **Why** = 業務驅動力，不是技術描述
- **Scope Out** = 必須有，即使只寫一條
- **Success Criteria** = checkbox 格式，可驗證
- **不寫「方法」** — 那是 milestone / plan 層級的東西
- **Existing Issues** = 搜尋 Linear 找相關 issue 建議搬入

### 3. Create project

After user confirms draft:

1. `save_project` with confirmed fields
2. `save_customer_need` linking customer to project (workaround for no customer field on project)
3. Remind user to manually add members (API limitation)
4. Optionally move existing issues into the project

### 4. Connect back to triage

After project created:
- New issues from this triage session can be assigned to the project
- Customer needs can be linked to the project
- Return to issues flow or overview

---

### 5. Attach Resources to Project

After project is created, attach relevant resources to the project's **Resources** section in Linear.

**Automated (via API):**
- `create_document(project: projectId)` — creates a Linear Document that appears in project Resources
- Use for: meeting notes, flow maps, specs, triage summaries

**Manual (remind user):**
- External links (Notion pages, Figma designs, Google Docs) — API has no "add link to project resources" tool
- Present links in GATE output so user can copy-paste into Linear UI

**Standard documents to create per project:**

| Document | When | Content |
|----------|------|---------|
| 會議紀錄 | After Step M (meeting notes) | Action items, customer needs, 時程承諾 |
| 流程地圖 | After resource discovery | 操作路徑、頁面關係、E2E flow 對應 |

---

## API Limitations

| Field | API Support | Workaround |
|-------|------------|------------|
| customer | ❌ | Create customer need linked to project |
| members | ❌ | Remind user to add manually |
| milestones | ❌ create | Created separately or manually |
| resource links | ❌ (external) | `create_document` works; external links need manual add |

## Anti-Patterns

- ❌ Creating project without GATE
- ❌ Guessing target date without asking
- ❌ Writing "方法" or execution plans in project description
- ❌ Forgetting Scope Out section
- ❌ Using project description as a plan (that's what milestones/issues are for)
