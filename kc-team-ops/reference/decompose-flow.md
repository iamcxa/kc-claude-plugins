# Decompose Flow Reference

Two entry points, same output: sub-issues in Linear → return to overview mode.

**Core principle: `linear-manager` owns the split, em-triage provides technical context.**

em-triage gathers codebase intelligence (explorer findings, brainstorming output). The actual issue decomposition — how to slice, what granularity, naming, acceptance criteria — is delegated to `linear-manager` in consultation mode. Every sub-issue follows Linear Method:

- **E2E feature** — not split by layer (backend/frontend), but by user-visible capability
- **Right-sized** — ≤3 days, estimate ≤8 (16 = must split further)
- **Independently valuable** — user can actually use the feature when done
- **Title format** — `[action] + [feature] + [user value]` (e.g., 「顧客預約完成後收到確認通知」)

---

## Step DC: Decompose from Issue

Triggered from deliberation gate when scope is too large.

1. **Gather technical context** — Summarize explorer findings: files involved, domains touched, independent workstreams identified, dependencies between them.

2. **Infer team estimate scale** — Before proposing estimates, fetch the target team's estimation settings. See `${CLAUDE_PLUGIN_ROOT}/reference/estimate-inference.md` for procedure. Provide the inferred scale + allowed values to `linear-manager` in the next step.

3. **Dispatch `linear-manager` (consultation mode)** — Provide:
   - Original issue content
   - Explorer findings summary (files, domains, workstreams)
   - **Team estimate scale** (e.g., "T-shirt: XS=1, S=2, M=3, L=5, XL=8") + scope-based estimate suggestions per workstream
   - Ask: "Based on Linear Method principles, how should this be split into E2E sub-issues? Use the team's estimate scale for sizing."
   - `linear-manager` returns: proposed issues with titles, descriptions, acceptance criteria, estimates, dependency order

4. **Present to user** — Show `linear-manager`'s proposed breakdown. Add technical notes from explorer (key files per issue, risks spotted). Estimates show both value and scale name.
   ```
   Team estimate scale: T-shirt (XS/S/M/L/XL)

   linear-manager proposes splitting SC-500 "Add notification system":

   1. 「顧客預約完成後收到確認通知」— est: XL (8)
      — booking saga + notification domain + email delivery, E2E
   2. 「顧客可在 app 設定通知偏好」— est: M (3)
      — profile extension + app endpoint + Expo screen, E2E
   3. 「管理者可查看通知發送狀態」— est: M (3)
      — notification view + admin UI page, E2E

   Dependencies: 1 → 2, 3 (1 first, 2/3 can parallel)
   Proceed with this split? (estimates adjustable)
   ```

5. **GATE** — User approves, adjusts, or rejects (including estimates).

6. **Create sub-issues** — Dispatch `linear-manager` to create:
   - Sub-issues of original (or standalone, user decides)
   - With acceptance criteria, estimates, labels, dependencies
   - Copy relevant technical context from explorer findings into description

7. **Return to overview** — Show new sub-issues in overview table. User picks which to deep-dive.

---

## Step DD: Decompose from Document

Triggered when user provides a document as input.

1. **Read document** — Fetch content via appropriate method:
   - Notion page → MCP read
   - Linear project → `linear-manager` agent
   - Markdown file → Read tool
   - Pasted text → use directly

2. **Brainstorming** — Invoke `Skill: "superpowers:brainstorming"` with document as context:
   - Understand overall scope and goals
   - Identify distinct work blocks (features, infrastructure, migrations, etc.)
   - Surface ambiguities or missing requirements → ask user

3. **Code-explorer per block** — For each identified work block, dispatch `feature-dev:code-explorer` to assess:
   - Which files/domains are involved
   - Technical feasibility and complexity
   - Dependencies on other blocks

4. **Infer team estimate scale** — Same as Step DC-2. See `${CLAUDE_PLUGIN_ROOT}/reference/estimate-inference.md`.

5. **Dispatch `linear-manager` (consultation mode)** — Provide:
   - Document content summary
   - Brainstorming output (work blocks, ambiguities)
   - Explorer findings per block (files, feasibility, dependencies)
   - **Team estimate scale** + scope-based estimate suggestions per block
   - Ask: "Based on Linear Method principles, propose E2E issues for this scope. Use the team's estimate scale for sizing."
   - `linear-manager` returns: proposed issues with titles, descriptions, acceptance criteria, estimates, dependency order

6. **Present to user** — Show `linear-manager`'s proposed breakdown with technical context from explorer. Estimates show both value and scale name. Flag ambiguities that need product decisions before issues can be finalized.

7. **GATE** — User approves breakdown before creating anything (including estimates).

8. **Create issues** — Dispatch `linear-manager` to create:
   - Issues with descriptions from brainstorming + explorer + Linear Method formatting
   - Estimates (using team's scale values), priority, labels, dependencies
   - Link to source document in description
   - Optionally assign

9. **Return to overview** — Show all new issues in overview table. User picks which to deep-dive for implementation guidance.
