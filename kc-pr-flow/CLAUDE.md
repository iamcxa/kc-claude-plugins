# kc-pr-flow

PR lifecycle workflow: create, review, resolve reviews, commit reorg, automated daemon.

## Prerequisites

External runtime dependencies — marketplace plugins whose agents/skills are dispatched at runtime. The plugin works without them but degrades gracefully.

| Dependency | Used by | Purpose |
|-----------|---------|---------|
| `pr-review-toolkit` (code-reviewer, comment-analyzer, silent-failure-hunter, security-reviewer) | pr-create (ship mode), pr-review, pr-review-resolve | Code review analysis |
| `feature-dev` (code-reviewer) | pr-review-resolve | Complex thread validation |
| `superpowers` (receiving-code-review) | pr-review-resolve | Evaluation mindset |

If unavailable, the skill warns the user and continues without agent dispatch (manual review fallback).

## Internal Agents

Built-in subagents dispatched by kc-pr-review for security analysis. Based on Trail of Bits methodologies.

| Agent | Dispatched by | Condition | Purpose |
|-------|--------------|-----------|---------|
| `tob-security-reviewer` | kc-pr-review (Step 4-ToB-a) | Always | Differential security review: risk triage, blast radius, adversarial modeling |
| `tob-supply-chain-checker` | kc-pr-review (Step 4-ToB-b) | Dependency files changed | Supply chain risk audit + insecure defaults detection |
| `tob-actions-auditor` | kc-pr-review (Step 4-ToB-c) | Workflow files changed | AI agent CI/CD security: 9 attack vectors |

## Skill Trigger Conditions

| Skill | Triggers |
|-------|----------|
| `kc-pr-create` | "create pr", "open pr", "建立 PR", "開 PR", "發 PR", "送審", implementation complete. Default: full ship chain (draft → review → fix → ready → announce). `--draft-only` for PR-only. `--ci` for CI + AI reviewer gate. |
| `kc-pr-review` | "review pr", "review this PR", PR number/URL, "review current branch" |
| `kc-pr-review-resolve` | "resolve reviews", "address feedback", "fix review comments", PR has unresolved threads |
| `kc-pr-reorg` | "squash commits", "clean up history", "reorganize commits", "reorder commits", 5+ messy commits |
| `kc-pr-announce` | "announce", "post to product", "draft product message", "公告", after PR + demo completion |
| `kc-pr-daemon` | "start daemon", "stop daemon", "daemon status", "pr daemon", "daemon config", "啟動 daemon", "停止 daemon" |
| `break-point-probe` | "pressure-test this fix", "break-point check", "verify the break-point", bugfix / cross-stack PR review |

## Reference Index

| Reference | Skills that Read it | Content |
|-----------|-------------------|---------|
| `gh-api-patterns.md` | pr-create, pr-review, pr-review-resolve | PR detection, API payloads, GraphQL, AI reviewer timeline |
| `linear-integration.md` | pr-create | Linear comment format, 3-tier fallback |
| `review-triage.md` | pr-review | Noise filters, agent tiers, security patterns |
| `compliance-audit.md` | pr-review | Domain mapping, baseline validation, CODE/DOC/NEW classification |
| `knowledge-capture.md` | pr-review, pr-review-resolve | Two-dimension learning: skill patterns (D1) + project knowledge (D2) with write threshold |
| `learned-patterns.md` | pr-review, pr-review-resolve | Accumulated cross-project review patterns (D1 auto-append target) |
| `e2e-verification.md` | pr-create | Layer classification patterns for E2E integration detection |
| `pr-review-loop.md` | pr-daemon (iteration prompt) | Classification logic, risk tiers, safety rules for daemon |

### External Config (shared across plugins)

| Config | Skills that Read it | Content |
|--------|-------------------|---------|
| `~/.claude/kc-plugins-config/channels.yaml` | pr-announce | Slack workspace registry + channel → ID + defaults + project path → default channel mapping |
| `~/.claude/kc-plugins-config/language.yaml` | all skills | Output language per directory (longest prefix match) |
| `~/.claude/kc-plugins-config/identity.yaml` | pr-create | GitHub username, default assignee |
| `~/.claude/kc-plugins-config/pr-flow/daemon.yaml` | pr-daemon | Poll interval, model, ci-gate, notifications |

## Language Preference

Query flow (evaluated in order):

```
1. Read → ~/.claude/kc-plugins-config/language.yaml
2. pwd → longest prefix match against overrides
3. Match found → use that language
4. No match → use default
5. Config file not found → ask user:
   "PR workflow 的文字輸出要用什麼語言？預設是？特定目錄有不同偏好嗎？"
   → save to ~/.claude/kc-plugins-config/language.yaml
```

**Affected** (language preference applied):

| Scope | Examples |
|-------|---------|
| PR title description | "feat: add login flow" description text |
| PR body | Summary, test plan, impact sections |
| Self-review inline comments | Comments posted during kc-pr-review |
| Review inline comments | Comments from agent-dispatched code review |
| Thread replies | Responses to existing review threads |
| Re-review summary | Summary after resolving reviews |
| Linear comments | Comments posted to linked Linear issues |
| Commit descriptions | Commit message body (not the prefix line) |

**Not affected** (always English):

| Scope | Reason |
|-------|--------|
| Conventional commit prefix | `feat:`, `fix:`, `chore:` etc. — tooling depends on exact format |
| Code identifiers | Variable names, function names, file paths |
| gh CLI commands/flags | Shell commands are not natural language |

## Rules

- All text output follows unified language preference (see Language Preference above)
- Reference files are loaded via `Read → ${CLAUDE_PLUGIN_ROOT}/reference/xxx.md`
- Shared config is loaded via `Read → ~/.claude/kc-plugins-config/xxx.yaml`
- External agent dispatch degrades gracefully if marketplace plugin is unavailable
- PRs are always assigned to the user (`--assignee @me` from identity config)
- **Documentation sync**: When adding or modifying plugin components (skills, hooks, scripts, reference files), update ALL of: CLAUDE.md (trigger conditions + reference index), README.md (skills table + docs table + references), and relevant `docs/*.md`. Include mermaid diagrams for non-trivial flows.
