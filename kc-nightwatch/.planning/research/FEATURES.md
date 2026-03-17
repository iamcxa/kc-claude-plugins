# Feature Research

**Domain:** Autonomous agent monitoring + improvement cockpit (CI/CD dashboard meets AI agent observability)
**Researched:** 2026-03-18
**Confidence:** HIGH (design spec is authoritative source; external research confirms and fills gaps)

---

## Context

This is a single-user personal tool wrapping the kc-nightwatch plugin. The closest analogues are:
- **Observability dashboards** (Grafana, Datadog): established patterns for run history, metrics, logs
- **CI/CD platforms** (GitHub Actions, CircleCI): trigger/run/log/status lifecycle patterns
- **AI agent monitoring** (LangSmith, Langfuse, AgentOps): trace visibility, scoring, human feedback
- **Autonomous coding agent cockpits** (Google Antigravity Agent Manager, GitHub Copilot Workspace, Conductor): proposal review, agent direction

The Nightwatch dashboard is unusual because it is both *monitoring* (observability) and *directing* (accept/reject proposals, trigger runs, inject instructions). Most analogues do one or the other.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = tool feels broken or incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Target list with latest status | Every monitoring/CI tool shows current state of monitored objects | LOW | Cards showing name, last run result, schedule status |
| Run history with filtering | Grafana, GitHub Actions, CircleCI — history is fundamental | LOW | List of runs, filter by target/status/mode |
| Real-time log streaming during execution | GitHub Actions, CircleCI both stream logs live; users expect this | MEDIUM | SSE from worker via IPC; monospace auto-scroll |
| Run status indicators (queued/running/done/failed) | CI/CD conventions; users have muscle memory | LOW | Status badges on cards and list; color coding |
| Manual run trigger | Every CI/CD tool has "run now" button | LOW | Trigger dialog with mode selection |
| Dry-run mode toggle | Standard in automation tools; prevents accidental production runs | LOW | Part of trigger dialog; all CI tools have staging/dry-run |
| Cancel running job | GitHub Actions, CircleCI — users expect to be able to stop a run | LOW | Available during execution; SIGTERM to worker |
| Readable run detail with phase breakdown | LangSmith traces, CircleCI step view — users expect to see what happened | MEDIUM | Phase progress bar + per-action summary |
| Config view (read-only by default) | Tools like Grafana show config; users need to understand what's configured | LOW | Show targets.yaml rendered nicely |
| Basic schedule status (next run, last run) | Every cron/scheduler shows this | LOW | Status bar component |
| Persistent server (not CLI-only) | Users expect a URL they can return to | MEDIUM | Bun server with always-on design |

### Differentiators (Competitive Advantage)

Features that set this apart from both CI/CD tools and generic agent monitors.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Flywheel health metrics (reject rate trends, indicator trends, effectiveness) | No CI/CD tool tracks whether automation quality is improving over time. Unique to autonomous improvement context. | HIGH | Requires indicator_baseline + feedback + implementation_outcomes across runs |
| Per-run self-assessment display (pre + post) | LangSmith shows traces; Langfuse shows scores — but neither shows the agent's own strategic reasoning embedded in the run. Nightwatch's 2-phase assessment is novel. | MEDIUM | Surface pre_assessment (Phase 3.5) + post_assessment (Phase 4.5) in run detail |
| Proposal → Implementation pipeline with outcome tracking | Agent monitoring tools record what happened; they don't close the loop on whether it worked. Closed-loop effectiveness tracking ("did this PR actually move the indicator?") is genuinely novel. | HIGH | Depends on: feedback system, indicator baseline, implementation runs |
| NW-Claude conversational panel with run context | AgentOps/LangSmith let you inspect traces; Nightwatch lets you talk to the agent about them. Chat is scoped to per-target journal + run results. | HIGH | WebSocket chat session via `--input-format stream-json`; auto-brief after run |
| AI-validated config editing (4-step with semantic validation) | YAML editors in DevOps tools are syntax-only. Nightwatch's semantic validation (Linear team resolution, Sentry access check via Haiku) prevents runtime config errors upstream. | HIGH | 4-step: syntax → Haiku semantic → diff → confirm; $0.05 budget cap |
| MCP server exposure (nightwatch as a tool for other Claude sessions) | No analogous tool exposes its state to other AI agents via MCP. This makes nightwatch a composable primitive in a broader Claude workflow. | HIGH | /mcp endpoint with 10 tools; requires server to be running |
| Per-target agent memory isolation | LangSmith/Langfuse share a project namespace. Nightwatch gives each monitored target its own journal so learnings don't cross-contaminate. | MEDIUM | Per-target private-journal dir; injected via --mcp-config per run |
| Indicator baseline measurement (quantified, not qualitative) | Most agent monitoring is qualitative ("it seemed to do better"). Nightwatch measures concrete indicators each run and tracks delta over time. | HIGH | Phase 0.5: count journal mentions, git churn, open issues — numeric baseline |
| Per-run custom prompt injection | CI/CD tools run the same pipeline. Nightwatch lets you give targeted instructions for a specific run ("focus on the auth module"). | LOW | custom_prompt field saved to run artifacts; --append-system-prompt |
| Multi-channel feedback aggregation (PR status + Linear + dashboard + MCP + chat) | LangSmith has annotation queues; Langfuse has human scoring. Nightwatch collects feedback from wherever the user naturally operates (merging a PR = accepted). | MEDIUM | All channels → nightwatch-feedback.yaml → same consumption path |
| Sandboxed execution per target with per-mode policy | No monitoring dashboard controls what the monitored agent can touch. agent-safehouse provides read-only for analysis, read-write for production. | MEDIUM | Policy builder generates safehouse flags per (target, mode) pair |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create specific problems for this system.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Multi-user RBAC | "What if others want to use it?" | Single-user tool running local processes with user-scope credentials. RBAC adds auth surface, permission complexity, and audit requirements that are wildly disproportionate to a personal tool. Engineering cost >> value. | Ship as single-user; if open-sourced, token auth for remote access is sufficient |
| Cron expression scheduling | "More power than intervals" | Cron expressions require a mental model most developers need to look up. For a monitoring tool that runs every few hours, intervals (every 2h) are clearer and mistake-proof. Power users can always set a 1h interval. | Interval-based scheduling; manual trigger for precise timing needs |
| Real-time everything / live dashboard auto-refresh | "I want to see changes instantly" | Polling/websocket for a tool that runs once per interval creates unnecessary complexity. The dashboard is used for review, not continuous monitoring. Auto-refresh on stale data is fine. | SSE for active runs (legitimate real-time need); manual refresh or periodic polling for idle state |
| Cloud dashboard / cross-machine sync | "Access from anywhere" | Requires auth hardening, network security, cloud infrastructure, and secrets management. The primary user is the developer at their machine where the agent runs. Remote access is a security risk for a tool with filesystem + git write access. | Remote mode with token auth as opt-in; localhost default |
| File watch triggers (on git push) | "Run nightwatch when I push" | Adds inotify/fsevents dependency, creates concurrent run risks if pushes cluster. The interval scheduler + manual trigger covers 95% of needs. | Webhook trigger for CI integration; manual trigger for ad-hoc needs |
| Slack reaction feedback (👍/👎 on Slack messages) | "That's where I already am" | Requires Slack MCP read-scoped access, which has security implications. Also creates two feedback entry points with different latency (Slack reaction vs dashboard). The async nature means feedback arrives delayed and out of context. | Dashboard 👍/👎 inline with the action card; MCP for Claude session feedback |
| Custom MCP/plugin per target | "Different targets need different tools" | Plugin configuration per target creates a combinatorial management burden. Claude already loads project .mcp.json from the target's cwd. Extra plugins should be truly additive, not alternative. | `extra_plugin_dirs` and `extra_mcp_config` as additive overrides; rely on project .mcp.json for base |
| Rich text / markdown editing for YAML fields | "Make the config UI easier" | YAML with a proper diff view is more precise than a form editor for complex configs. Form-based editors hide structure, create round-trip fidelity issues, and require field-by-field UI maintenance. | YAML editor with syntax highlighting + schema hints; Add Target wizard for guided first-time creation only |
| Proposal execution without user approval | "Why not auto-implement accepted proposals?" | The entire value of the flywheel is that humans decide what to implement. Auto-implementation without review removes the safety check that makes the feedback loop trustworthy. | Proposal → Implementation pipeline requires explicit accept action; implementation run is separate and visible |
| Per-target auth token management | "Different targets in different accounts" | Auth token lifecycle (rotation, storage, encryption) is a significant security burden. Schema can be prepared but implementation deferred — the vast majority of targets will be same-account repos. | `auth: default` covers 95% of cases; token support is schema-prepared but deferred |

---

## Feature Dependencies

```
[Flywheel Health Display]
    └──requires──> [Indicator Baseline Measurement (Phase 0.5)]
                       └──requires──> [Run Storage + Summary YAML]
    └──requires──> [Feedback System (multi-channel)]
                       └──requires──> [Run detail with action cards]
    └──requires──> [Implementation Outcome Tracking (Phase 0.6)]
                       └──requires──> [Proposal → Implementation Pipeline]
                                          └──requires──> [Feedback System]
                                          └──requires──> [Run Trigger System]

[NW-Claude Chat Panel]
    └──requires──> [Run History + Summaries]
    └──requires──> [Per-target NW Memory Layer]
    └──requires──> [WebSocket server + claude bidirectional streaming]
    └──enhances──> [Feedback System] (user can submit feedback via chat)

[MCP Server]
    └──requires──> [Run Store (query existing runs)]
    └──requires──> [Run Trigger System]
    └──requires──> [Feedback System]
    └──enhances──> [NW-Claude Chat] (MCP tools available in chat session)

[Config Editor (4-step)]
    └──requires──> [YAML Store (read/write)]
    └──requires──> [Semantic Validation (Haiku spawn)]
    └──enhances──> [Add Target Wizard] (wizard uses same save path)

[Add Target Wizard]
    └──requires──> [Config Editor core]
    └──requires──> [YAML Store]

[Real-time Log Streaming]
    └──requires──> [Worker IPC + stream-json parser]
    └──requires──> [SSE server endpoint]

[Phase Progress Bar]
    └──requires──> [Real-time Log Streaming]
    └──requires──> [stream-json phase detection in log-parser.ts]

[Run Detail with Action Cards]
    └──requires──> [Run Storage + Summary YAML]
    └──requires──> [Phase Progress Bar]

[Feedback Buttons (per action)]
    └──requires──> [Run Detail with Action Cards]
    └──requires──> [POST /api/feedback endpoint]

[Proposal → Implementation Pipeline]
    └──requires──> [Run Detail with Action Cards] (shows proposal PR)
    └──requires──> [Feedback Buttons]
    └──requires──> [Worker IPC (enqueue implementation run)]

[Target Card per-card actions]
    └──requires──> [Target List]
    └──requires──> [Run Trigger System]
    └──enhances──> [NW-Claude Chat] ("Chat about this" loads target context)

[Scheduler Status Bar]
    └──requires──> [Worker IPC (status query)]
    └──enhances──> [Manual Run Trigger] (shows next scheduled run)

[Sandboxed Execution (agent-safehouse)]
    └──required by──> [All run execution]
    └──requires──> [Policy builder per (target, mode)]
```

### Dependency Notes

- **Flywheel health requires feedback + baseline + outcomes**: All three need to be present for the health display to mean anything. Shipping health display before feedback collection is ready shows empty/misleading charts.
- **NW-Claude chat requires memory layer**: Without per-target journal injection, chat context is generic. The chat panel is most valuable after several runs of history exist.
- **MCP server requires stable run store**: MCP tools query run history; unstable run storage schema will break external sessions.
- **Implementation pipeline requires feedback first**: Accepting a proposal IS feedback. The feedback system must be in place before the pipeline can function.
- **Config editor 4-step requires Haiku semantic validation**: Step 2 spawns a subprocess. This is the most complex part of the config editor and should be built after basic YAML read/write is stable.

---

## MVP Definition

### Launch With (v1 — core cockpit)

Minimum viable product: the tool is usable as a dashboard replacement for the current cron + YAML-file workflow.

- [ ] Target list with last run status + schedule bar — replaces checking nightwatch-runs.yaml manually
- [ ] Manual run trigger (production / dry-run / self-repair toggle) — replaces CLI `/kc-nightwatch` invocation
- [ ] Real-time log streaming during execution — the single biggest UX improvement over cron
- [ ] Run history list + run detail with phase progress + action summary — replaces reading summary.yaml
- [ ] Feedback buttons per action (👍/👎) + POST /api/feedback — the minimum feedback entry point
- [ ] Interval scheduler (enable/disable, set hours) — replaces launchd plist management
- [ ] YAML config view (read-only) — replaces opening the file in editor
- [ ] Per-target NW memory layer (isolation) — required for all future learning features; implement now or retrofit is painful
- [ ] Sandboxed execution with per-target safehouse policy — non-negotiable safety requirement from day one
- [ ] Basic IPC (server ↔ worker) with status + run lifecycle — foundational; everything else depends on it

### Add After Validation (v1.x — flywheel core)

Add once core cockpit is working and feedback data starts accumulating.

- [ ] Indicator baseline measurement (Phase 0.5) — trigger: a few runs of feedback data exists to compare against
- [ ] Self-assessment display in run detail (Phase 3.5 / 4.5) — trigger: run quality looks good in manual review
- [ ] Config editor with 4-step validation (edit lock + semantic validation) — trigger: config editing via files is becoming painful
- [ ] Add Target wizard — trigger: first time adding a new target post-launch
- [ ] NW-Claude chat panel — trigger: enough run history to make chat context meaningful
- [ ] Webhook trigger — trigger: want to trigger from CI/CD pipeline

### Future Consideration (v2+ — full flywheel)

Defer until the flywheel core has been validated.

- [ ] Implementation outcome tracking (Phase 0.6) — requires several proposal → implementation cycles to have data
- [ ] Flywheel health display (sparklines, reject rate charts) — requires implementation outcomes to be meaningful
- [ ] Proposal → Implementation pipeline (accept → spawn implementation run) — high complexity; validate proposal quality first
- [ ] MCP server — requires stable API surface; valuable once run history is trustworthy
- [ ] Slack reaction feedback (v2) — requires Slack MCP read scope decision
- [ ] PR review comment parsing — requires gh API parsing work

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Target list + schedule bar | HIGH | LOW | P1 |
| Manual run trigger | HIGH | LOW | P1 |
| Real-time log streaming | HIGH | MEDIUM | P1 |
| Run history + detail | HIGH | MEDIUM | P1 |
| Sandboxed execution + IPC | HIGH | HIGH | P1 (safety prerequisite) |
| Interval scheduler | HIGH | MEDIUM | P1 |
| Feedback buttons (👍/👎) | HIGH | LOW | P1 |
| Per-target NW memory | MEDIUM | MEDIUM | P1 (foundational, painful to retrofit) |
| Indicator baseline (Phase 0.5) | HIGH | HIGH | P2 |
| Self-assessment display | MEDIUM | LOW | P2 (display only; data comes from pipeline) |
| Config editor (4-step) | MEDIUM | HIGH | P2 |
| Add Target wizard | MEDIUM | MEDIUM | P2 |
| NW-Claude chat panel | HIGH | HIGH | P2 |
| Webhook trigger | LOW | LOW | P2 |
| Implementation outcome tracking | HIGH | HIGH | P3 |
| Flywheel health display | HIGH | MEDIUM | P3 (depends on outcomes data) |
| Proposal → Implementation pipeline | HIGH | HIGH | P3 |
| MCP server | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for launch — without these, the tool isn't better than cron + YAML files
- P2: Should have — add once P1 is stable; this is where the unique value appears
- P3: Future — deferred until core flywheel is validated

---

## Competitor Feature Analysis

| Feature | LangSmith / Langfuse | GitHub Actions / CircleCI | Google Antigravity / Conductor | Nightwatch Dashboard |
|---------|---------------------|--------------------------|-------------------------------|---------------------|
| Trace / log visibility | Full trace tree with tool calls | Step-level logs, artifact links | Agent task list + artifacts | Phase-structured log stream; tool calls visible via stream-json |
| Human feedback on outputs | Annotation queue, thumbs up/down per trace | N/A (not output feedback) | PR review (accept/reject agent work) | 👍/👎 per action card, multi-channel aggregation |
| Scheduling / triggers | Eval datasets run on schedule | Cron + push + manual | Issue-assigned trigger | Interval + manual + webhook |
| Config editing | Project settings (form-based) | YAML in repo (no UI editor) | N/A | YAML editor with semantic validation |
| Agent direction (chat / instructions) | N/A | N/A | "Assign issue" as direction | NW-Claude chat with run context |
| Improvement tracking over time | Eval scores over time (regression) | Build time trends, MTTR | N/A | Reject rate + indicator trends + implementation effectiveness |
| Multi-agent coordination | LangSmith traces show agent-to-agent calls | N/A | Parallel agents, isolated workspaces | Single agent per run; sequential targets |
| Memory / learning between runs | Dataset + evaluation history | Cache artifacts | N/A | Per-target NW journal + feedback calibration |
| Proposal review UI | N/A | PR review | PR diff + approve/reject | Action cards with feedback + proposal → implementation pipeline |
| MCP / programmatic access | LangSmith REST API | GitHub Actions API | N/A | MCP server (10 tools) |
| Sandboxed execution | N/A (instrument, don't run) | Container isolation | Isolated worktrees | agent-safehouse per-target policy |
| Cost / budget control | Token cost tracking per trace | N/A | N/A | Safety.yaml limits; Haiku budget cap for validation |

---

## Sources

- LangSmith: [AI Agent & LLM Observability Platform](https://www.langchain.com/langsmith/observability), [Insights Agent + Multi-turn Evals](https://blog.langchain.com/insights-agent-multiturn-evals-langsmith/) — MEDIUM confidence
- Langfuse: [Observability Overview](https://langfuse.com/docs/observability/overview), [Scores + Evaluation](https://langfuse.com/docs/evaluation/core-concepts) — MEDIUM confidence
- AgentOps: [Introduction](https://docs.agentops.ai/), [akira.ai comparison](https://www.akira.ai/blog/langsmith-and-agentops-with-ai-agents) — MEDIUM confidence (WebSearch, not Context7)
- GitHub Agentic Workflows: [The New Stack overview](https://thenewstack.io/github-agentic-workflows-overview/) — LOW confidence
- Human-in-the-Loop patterns: [Anthropic research on agent autonomy](https://www.anthropic.com/research/measuring-agent-autonomy), [permit.io HITL patterns](https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo) — MEDIUM confidence
- SSE vs WebSocket: [oneuptime.com 2026 comparison](https://oneuptime.com/blog/post/2026-01-27-sse-vs-websockets/view) — HIGH confidence (confirmed by design spec decision)
- Design spec: `/docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` (812 lines, 2 review rounds) — HIGH confidence (authoritative source)
- PROJECT.md: `kc-nightwatch/.planning/PROJECT.md` — HIGH confidence (authoritative source)

---

*Feature research for: Nightwatch Dashboard — autonomous agent monitoring + improvement cockpit*
*Researched: 2026-03-18*
