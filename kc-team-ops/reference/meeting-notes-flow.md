# Meeting Notes Flow (Step M)

## Linear Customer Request Concept

Linear has a customer need tracking system independent of Issues:

```
Customer (company/person)
  └── Customer Need (a request/requirement)
        ├── Can link to Issue (existing work item)
        └── Can link to Project (belongs to a project scope)
```

**Available MCP tools:**
- `list_customers` — list customers; `includeNeeds: true` fetches needs in one call
- `save_customer` — create/update customer (requires `name`)
- `save_customer_need` — create/update need (requires `body`; can link `customer`, `issue`, `project`; `priority`: 0=normal, 1=important)
  - **API limitation**: `projectId` and `issueId` are mutually exclusive — only one can be provided. Providing both causes an error. If a need relates to both an issue and a project, link the issue (issue already implies project membership).

**Role in em-triage:**
- **Input**: meeting notes can be extracted into Customer Needs and saved to Linear
- **Triage**: how many customer needs reference an issue = customer demand signal, influences priority
- **Overview**: table should show customer need count so EM can see demand intensity

---

## Step M: Meeting Notes → Customer Needs

**Trigger**: User provides meeting notes (Notion page, transcript, screenshot, or pasted text).

**Process**:

1. **Read source** — based on format:
   - Notion page → MCP read
   - Fireflies transcript → `fireflies` MCP tools
   - Screenshot → Read tool (multimodal)
   - Pasted text → use directly

2. **Extract customer needs** — identify from meeting content:
   - **Customer**: which customer/company raised the need (may be multiple)
   - **Needs**: specific request items (each need is a separate entry)
   - **Priority**: did the customer emphasize importance (maps to `priority: 1`)
   - **Association**: does it correspond to a known issue or project

3. **GATE — confirm extraction results**:

   ```
   從 [會議名稱/日期] 萃取出以下 Customer Needs：

   Customer: Acme Corp（已存在 / 需新建）
   1. 「批次匯出報表」 — priority: important — 可能對應 SC-XXX
   2. 「API 查詢客戶資料」 — priority: normal — 無對應 issue
   3. 「SSO 整合」 — priority: important — 無對應 issue

   要寫入 Linear 嗎？
   ```

4. **Write to Linear** — after user confirms:
   - `save_customer` — create customer if it doesn't exist
   - `save_customer_need` — create each need independently, link to customer; link to issue if one exists

5. **Connect to triage** — after needs are saved, assess next steps for each need:

   **Before creating issues: infer team estimate scale** — if issues need to be created, first infer the target team's estimate settings. See `${CLAUDE_PLUGIN_ROOT}/reference/estimate-inference.md`. Provide estimate suggestions based on need complexity.

   **Evaluate each need:**
   - **Has existing issue** → "Want to triage these issues?" → enter issues flow
   - **Needs research before work** (vague requirements, UX flow undefined, technical feasibility unclear) → create issue + research sub-issue via `linear-manager`:
     ```
     Issue: 「[功能描述]」— est: M (3)
       └── Sub-issue: 「[Research] [功能描述] — UX/技術研究」— est: S (2)
           assignee + labels → ask user (or follow team conventions)
     ```
   - **Requirements clear, ready to start** → create issue via `linear-manager`, link need, include estimate
   - **User chooses not to continue** → done

   Always **GATE** before creating issues — present the planned structure (with estimates) for user confirmation. `linear-manager` handles the actual issue creation and structure.
