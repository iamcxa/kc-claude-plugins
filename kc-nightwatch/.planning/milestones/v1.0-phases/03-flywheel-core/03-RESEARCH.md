# Phase 3: Flywheel Core - Research

**Researched:** 2026-03-18
**Domain:** WebSocket/SSE chat, YAML config editor, feedback pipeline, self-assessment display
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Chat Panel:**
- Right-side slide-over drawer (overlay, ~400px), not a new page or inline panel
- Drawer can be opened from any page (Dashboard, Runs, Config) — use `position: fixed` overlay
- Does not displace or shrink main content
- Run completion triggers auto-open of chat drawer with NW-Claude briefing the run summary
- Auto-brief mechanism: Worker IPC `run:completed` → server SSE `brief-ready` event → frontend auto-opens drawer
- Need a global SSE connection (not per-run) so auto-brief works from any page

**Chat Backend:**
- Claude CLI `--input-format stream-json` as primary chat engine (inherits all plugin/MCP/permission settings)
- First task in plan must be a minimal spike: spawn `claude -p --input-format stream-json`, send a message, verify response
- If spike fails → fallback to Anthropic SDK (loses plugin context, document the tradeoff)
- If spike succeeds → full CLI route

**IMPORTANT override from STATE.md:** "Use Anthropic SDK as chat default — `--input-format stream-json` unreliable for long sessions". The spike is still required (verify current behavior), but default path should be SDK.

**Chat Session Lifecycle:**
- Each target gets its own claude -p process (no sharing)
- Switch target → kill old process → spawn new with target-specific context
- Close drawer → keep process alive in background → reopen = continue conversation
- Reset button → kill + respawn fresh session
- NW-Claude has NW journal access for the focused target (via `--mcp-config`)

**Config Editor:**
- YAML textarea as main editor with syntax highlighting (if achievable without heavy deps)
- Edit lock: read-only by default, explicit "Edit" button to unlock
- 4-step save validation flow: static YAML parse → Haiku semantic check → diff preview → confirm save
- Validation UX: Claude's discretion (wizard-style or inline feedback — whatever fits best)
- Config page uses tab layout: Targets tab + Safety tab, each with its own YAML editor
- Config warnings from self-repair.yaml displayed inline in the relevant tab
- $0.05 cap on Haiku semantic validation call (from PROJECT.md constraints)

**Add/Edit/Remove Target:**
- Add Target: 4-step modal wizard (consistent with TriggerDialog pattern) — type → goals → monitors/respond → validate
- Edit Target: same modal wizard, pre-filled with existing values
- Remove Target: confirm dialog (like existing remove pattern in TargetDetail)
- Wizard generates YAML and appends to targets.yaml → runs 4-step validation before writing

**Feedback Buttons:**
- Thumbs up/down on each action card in run detail (per signal granularity)
- POST /api/feedback with signal_id, verdict (accepted/rejected), optional reason
- MCP feedback tool (nw_submit_feedback) for NW-Claude to also submit feedback
- Visual: compact thumbs up/down icons, fills/highlights on selection, disabled after submission

**Implicit Feedback Collection:**
- Worker polls PR and Linear issue status periodically (every 6h or before each run)
- Uses `gh` CLI for PR status (merged = accepted, closed without merge = rejected)
- Uses Linear MCP for issue status (closed/done = accepted)
- Results written to feedback store and NW journal

**Reject Rate Calibration:**
- Config page shows per-indicator calibration data (reject rate + current confidence threshold) for transparency
- Feedback trends written to NW journal for NW-Claude slow learning path
- Calibration adjustments happen automatically — user can see but not manually override

**Self-Assessment Display:**
- Phase 3.5 (pre-action strategy) and Phase 4.5 (post-action reflection) embedded inside action cards
- Action card expanded view: top = strategy rationale, bottom = reflection on outcome
- Co-located with feedback buttons — user reads assessment then gives feedback

**Indicator Baseline Display:**
- Phase 0.5 baselines shown as a summary card at top of run detail
- Each indicator: one row with name, current_value, trend arrow (up/down/flat)
- Compact, always visible (not collapsible) — provides context for all action cards below

### Claude's Discretion
- 4-step validation UX specifics (wizard vs inline — whatever works best for the flow)
- YAML syntax highlighting approach (simple regex vs library)
- Chat drawer animation/transition details
- Auto-brief prompt construction (how to summarize run for NW-Claude context)
- Exact polling interval for implicit feedback (6h is suggested, not mandatory)
- Baseline summary card visual design

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CONF-01 | YAML editor for targets.yaml (read-only by default, unlock to edit) | Config editor patterns, existing yaml-store.ts, readYamlFile/writeYamlFile |
| CONF-02 | YAML editor for safety.yaml | Same config editor patterns, two-tab layout |
| CONF-03 | Edit lock (must explicitly enable editing) | Preact useState + disabled textarea pattern |
| CONF-04 | 4-step save validation (static parse → semantic via Haiku → diff → confirm) | Anthropic SDK Haiku call, yaml package parse, diff display pattern |
| CONF-05 | Config warnings panel (from self-repair.yaml, inline markers) | readYamlFile on nightwatch-self-repair.yaml, inline UI pattern |
| CONF-06 | Add Target wizard (4 steps: type → goals → monitors/respond → validate) | TriggerDialog multi-step pattern |
| CONF-07 | Edit Target (same wizard, pre-filled) | Same wizard with initial state injection |
| CONF-08 | Remove Target (confirm dialog) | Existing TargetDetail remove confirm pattern |
| CHAT-01 | NW-Claude chat panel (right side of dashboard) | Slide-over drawer, position:fixed overlay |
| CHAT-02 | Auto-brief after run completes (spawn Claude with run summary as context) | Global SSE + IPC run:completed → brief-ready event |
| CHAT-03 | Bidirectional Claude session (stream-json primary, SDK fallback) | Claude CLI --input-format stream-json + @anthropic-ai/sdk |
| CHAT-04 | NW-Claude has NW-MCP access (trigger runs, query state, submit feedback) | --mcp-config injection, existing writeNwJournalConfig pattern |
| CHAT-05 | NW-Claude has target-specific NW journal access | Per-target journal dir via ensureNwMemoryDir |
| CHAT-06 | Per-target chat focus ("Chat about this" from target card) | Target context passed to chat session spawn |
| CHAT-07 | Session lifecycle (persist until close/reset, switch context prompt on new run) | Process map keyed by target, kill/respawn pattern |
| FEED-01 | Dashboard feedback buttons (thumbs up/down) per action card | RunSummaryAction already has signal_id, new FeedbackEntry type |
| FEED-02 | Feedback API endpoint (POST /api/feedback) | Hono route pattern from api.ts |
| FEED-03 | MCP feedback tool (nw_submit_feedback) | Phase 4 MCP; for Phase 3 add to NW-Claude chat MCP config |
| FEED-04 | PR status collection (merged = accepted, closed = rejected) | gh CLI subprocess, existing Bun.spawn pattern |
| FEED-05 | Linear issue status collection | Linear MCP tool call in worker |
| FEED-06 | Reject rate calibration (per indicator, adjust confidence threshold) | feedback-store.ts + calibration logic |
| FEED-07 | Feedback trends written to NW journal (slow learning path) | writeNwJournalConfig + journal write pattern |
| ASSESS-01 | Phase 3.5 pre-action strategy assessment (in orchestrator skill) | NW skill YAML modifications |
| ASSESS-02 | Phase 4.5 post-action reflection assessment (in orchestrator skill) | NW skill YAML modifications |
| ASSESS-03 | Assessment display in run detail (per action card) | RunSummaryAction.assessment already typed, expand action card UI |
| ASSESS-04 | Assessment in Slack report | NW skill Slack phase modifications |
| MEAS-01 | Phase 0.5 indicator baseline measurement (quantified values) | IndicatorBaseline already typed in shared/types.ts |
| MEAS-02 | Indicator trend tracking (previous_value + trend direction) | IndicatorBaseline.trend already defined |
| MEAS-03 | Baseline display in run detail | New summary card UI at top of run detail page |
</phase_requirements>

---

## Summary

Phase 3 turns the nightwatch dashboard from a passive cockpit into a learning system. Four largely-independent subsystems need to be built: (1) a slide-over chat drawer backed by Claude CLI or SDK, (2) a config editor with 4-step validation, (3) a feedback pipeline that collects explicit and implicit signals, and (4) self-assessment + measurement display in run detail.

The good news: the type system is already prepared. `RunSummaryAction.assessment`, `IndicatorBaseline`, and `PerTargetSummary.pre_assessment/post_assessment` are already defined in `shared/types.ts`. The data structures were designed in Phase 2 anticipating Phase 3. What is missing is (a) the server services to persist feedback and config writes, (b) the chat session manager, (c) the global SSE broadcast channel for auto-brief, and (d) the UI components for each feature.

The most technically novel piece is the chat system. The Claude CLI `--input-format stream-json` flag exists and is confirmed available in v2.1.78. However, STATE.md records a confirmed decision: "Use Anthropic SDK as chat default — `--input-format stream-json` unreliable for long sessions". The spike is still the first task (to document current behavior), but implementation should default to `@anthropic-ai/sdk` v0.79.0 (latest confirmed). The SDK loses plugin/MCP context that CLI inherits, but provides reliable streaming.

**Primary recommendation:** Plan the four subsystems as parallel tracks (03-01 Chat, 03-02 Config, 03-03 Feedback, 03-04 Assessment). The chat spike must go first within 03-01 before committing to the full CLI path. Each subsystem has clear seams against existing code — use them.

---

## Standard Stack

### Core (already in use)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Bun | 1.3.9 | Runtime, test runner, transpiler | Project baseline |
| Hono | ^4.12.8 | HTTP server + SSE | Already used for all routes |
| yaml | ^2.8.2 | YAML parse/stringify | Used in yaml-store.ts |
| zod | ^3.0.0 (pinned v3) | Schema validation | Pinned — v4 has breaking changes |
| Preact + HTM | vendored ESM | Frontend UI | No-bundler architecture |

### New for Phase 3
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @anthropic-ai/sdk | 0.79.0 (latest) | Chat SDK fallback (default path per STATE.md) | Chat sessions when CLI unreliable |
| hono/ws (built-in) | 4.12.8 | WebSocket support via Bun.serve websocket handler | Chat message transport if not SSE |

### Chat Transport Decision
The chat endpoint can use either WebSocket or SSE. Given the project uses SSE everywhere (streamSSE from hono/streaming), **use SSE for server-to-client streaming and POST for client-to-server messages**. This matches the existing LogStream pattern exactly and avoids adding WebSocket complexity.

Pattern: `POST /api/chat/:sessionId/message` → triggers response → `/api/chat/:sessionId/stream` SSE for response chunks.

### Installation (new dependency only)
```bash
cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app
bun add @anthropic-ai/sdk
```

**Version verification:** `@anthropic-ai/sdk` v0.79.0 confirmed via `npm view @anthropic-ai/sdk version` on 2026-03-18.

---

## Architecture Patterns

### Recommended New File Structure
```
app/
├── server/
│   ├── routes/
│   │   ├── api.ts              # extend with /api/feedback, /api/config/:file
│   │   ├── stream.ts           # extend with /api/events (global SSE)
│   │   └── chat.ts             # NEW: /api/chat routes (POST message + GET stream)
│   └── services/
│       ├── yaml-store.ts       # extend with readRawYaml, writeYamlSafe
│       ├── feedback-store.ts   # NEW: FeedbackEntry persistence
│       ├── chat-manager.ts     # NEW: chat session process map + SDK client
│       └── config-validator.ts # NEW: 4-step validation logic
├── worker/
│   ├── executor.ts             # extend: emit assessment + baseline in RunSummary
│   └── feedback-collector.ts  # NEW: PR/Linear status polling
├── shared/
│   └── types.ts                # extend: FeedbackEntry, ChatMessage, ConfigValidationResult
└── frontend/
    ├── components/
    │   ├── chat-drawer.ts      # NEW: slide-over drawer
    │   ├── action-card.ts      # NEW: extracted from runs.ts (feedback + assessment)
    │   └── baseline-card.ts   # NEW: indicator baseline summary
    └── pages/
        └── config.ts           # REPLACE placeholder with full config editor
```

### Pattern 1: Global SSE Broadcast (auto-brief trigger)
The existing SSE fan-out in `ipc.ts` is run-scoped (`Map<runId, Set<SSEWriter>>`). Phase 3 needs a **global** channel for events that are not tied to a run ID (like `brief-ready`).

**What:** Add a parallel global SSE subscriber set alongside the run-scoped one.
**When to use:** Any event that needs to reach all connected clients regardless of which page they're on.

```typescript
// In ipc.ts — add global broadcast alongside existing run-scoped subscribers
const globalSubscribers = new Set<SSEWriter>()

export function subscribeGlobal(writer: SSEWriter, signal: AbortSignal): () => void {
  globalSubscribers.add(writer)
  const cleanup = () => globalSubscribers.delete(writer)
  signal.addEventListener('abort', cleanup)
  return cleanup
}

export function broadcastGlobal(event: string, data: unknown): void {
  const payload = JSON.stringify(data)
  for (const writer of globalSubscribers) {
    void writer.writeSSE({ data: payload, event })
  }
}
```

In `handleWorkerMessage`, when `run:completed` fires:
```typescript
case 'run:completed':
  closeRunSubscribers(msg.run_id)
  broadcastGlobal('brief-ready', { run_id: msg.run_id, summary: msg.summary })
  break
```

Frontend global SSE in `app.ts`:
```typescript
const globalEs = new EventSource('/api/events')
globalEs.addEventListener('brief-ready', (e) => {
  // auto-open chat drawer with summary context
  setChatDrawerOpen(true)
  setChatBriefContext(JSON.parse(e.data))
})
```

### Pattern 2: Chat Session Manager
**What:** Server-side process manager that maintains one Claude process (or SDK client) per target.
**When to use:** For all NW-Claude chat operations.

```typescript
// chat-manager.ts
interface ChatSession {
  targetName: string
  // CLI path: child process handle
  proc?: ReturnType<typeof Bun.spawn>
  // SDK path: Anthropic client + message history
  sdkClient?: Anthropic
  messages?: MessageParam[]
  briefContext?: RunSummary
}

const sessions = new Map<string, ChatSession>()

export function getOrCreateSession(targetName: string): ChatSession {
  if (!sessions.has(targetName)) {
    sessions.set(targetName, { targetName })
  }
  return sessions.get(targetName)!
}

export function killSession(targetName: string): void {
  const session = sessions.get(targetName)
  if (session?.proc) {
    session.proc.kill('SIGKILL')
  }
  sessions.delete(targetName)
}
```

SDK streaming pattern:
```typescript
// Source: @anthropic-ai/sdk streaming docs
const stream = await anthropic.messages.stream({
  model: 'claude-haiku-4-5',  // fast responses for chat
  max_tokens: 1024,
  messages: session.messages,
})
for await (const chunk of stream) {
  // fan-out to SSE subscribers
}
```

**Model selection for chat:** Use `claude-haiku-4-5` for fast interactive responses. Reserve opus for the actual NW pipeline runs. The $0.05 cap constraint from CONTEXT.md applies to Haiku semantic validation, not chat.

### Pattern 3: Config Validation Flow
**What:** 4-step gated save: static parse → Haiku semantic check → diff preview → confirm write.
**When to use:** Any config save from the UI.

```typescript
// config-validator.ts
export async function validateConfigSave(
  file: 'targets' | 'safety',
  newYaml: string,
  originalYaml: string
): Promise<ConfigValidationResult> {
  // Step 1: Static YAML parse
  try {
    parse(newYaml) // throws on invalid YAML
  } catch (e) {
    return { valid: false, step: 'static', error: String(e) }
  }

  // Step 2: Haiku semantic check ($0.05 cap enforced via max_tokens)
  const haiku = new Anthropic()
  const check = await haiku.messages.create({
    model: 'claude-haiku-4-5',
    max_tokens: 200,  // $0.05 cap enforcement
    messages: [{
      role: 'user',
      content: `Review this nightwatch ${file} config change. Are there any dangerous or invalid values? Reply with OK or WARN:<reason>.\n\nOriginal:\n${originalYaml}\n\nNew:\n${newYaml}`
    }]
  })

  // Step 3: Diff (compute in-process, return to client)
  const diff = computeLineDiff(originalYaml, newYaml)

  return { valid: true, step: 'ready', haiku_verdict: check.content[0].text, diff }
}
```

**Diff display:** Use a simple line-by-line comparison (no external diff library needed). Lines prefixed with `+` / `-` colored green/red.

### Pattern 4: Feedback Store
**What:** Append-only YAML/JSON file per target, keyed by signal_id.
**When to use:** All feedback submissions (explicit buttons + implicit polling).

```typescript
// feedback-store.ts
export interface FeedbackEntry {
  signal_id: string
  target: string
  verdict: 'accepted' | 'rejected'
  reason?: string
  source: 'user' | 'pr_status' | 'linear_status'
  submitted_at: string
  calibration?: { indicator: string; reject_rate: number; threshold: number }
}

const FEEDBACK_PATH = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-feedback.yaml')

export async function appendFeedback(entry: FeedbackEntry): Promise<void> {
  const existing = await readYamlFile<{ feedback: FeedbackEntry[] }>(FEEDBACK_PATH) ?? { feedback: [] }
  existing.feedback.push(entry)
  await writeYamlFile(FEEDBACK_PATH, existing)
}
```

Note: `nightwatch-feedback.yaml` is already defined in CLAUDE.md as "Written each run by --self-repair session; Feedback from PR/issue status; read by regular pipeline". Phase 3 extends it with explicit user feedback.

### Pattern 5: Action Card Component
**What:** Extract action card rendering from `runs.ts` into a standalone `action-card.ts` component with feedback + assessment sections.
**When to use:** Run detail view (previously inline in runs.ts, now component).

The `RunSummaryAction` type already has `signal_id`, `assessment`, `pr_url`. The component needs:
- Expand/collapse toggle (assessment text can be long)
- Feedback buttons (thumbs up/down) — send POST /api/feedback
- Disabled state after feedback submitted (track in local `Set<signal_id>`)

### Anti-Patterns to Avoid
- **Sharing Claude processes across targets:** Each target MUST have its own chat session. Cross-target context leaks are a correctness bug.
- **Using `~` in file paths:** CLAUDE.md anti-pattern rule — always use `os.homedir()` + `path.join()`.
- **Reusing Bun.file handle after write:** Established project pitfall — always re-create handle for reads after writes.
- **Putting side effects in shared module imports:** Importing `server/index.ts` or `worker/index.ts` triggers `Bun.serve()`/`Bun.spawn()` — keep testable services in leaf modules (project-documented pitfall from Phase 2).
- **Blocking the run:completed IPC handler:** The global broadcast in `handleWorkerMessage` must be synchronous and fast. No async file I/O inside switch cases.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML parse/stringify | Custom YAML parser | `yaml` package (already in deps) | Edge cases: multi-document, anchors, unicode |
| Token cost cap on Haiku | Manual token counting | Set `max_tokens: 200` in SDK call | SDK enforces server-side |
| Claude API streaming | Manual HTTP fetch + SSE parsing | `@anthropic-ai/sdk` `messages.stream()` | Handles reconnection, partial chunks, error codes |
| Diff computation | Myers diff algorithm | Simple line-by-line diff (sufficient for YAML) | Config files are small; Myers is overkill |
| YAML syntax highlighting | Full highlight library (CodeMirror/Monaco) | Simple regex-based CSS classes | CLAUDE.md context: no bundler, vendor complexity high |
| Process lifecycle | Custom process registry with PID files | In-memory Map (chat-manager.ts) | Server process restarts clear the map; reconnect naturally re-spawns |
| PR status polling | GitHub API REST calls | `gh` CLI via `Bun.spawn` | Already proven pattern in existing NW pipeline; avoids OAuth token mgmt |

**Key insight:** The config editor and feedback store are both small-file YAML operations. The project already has `readYamlFile` / `writeYamlFile` in `yaml-store.ts` — extend these, don't create parallel file I/O patterns.

---

## Common Pitfalls

### Pitfall 1: CLI Chat Process Hanging After Result
**What goes wrong:** `claude -p --output-format stream-json` hangs after emitting result because active MCP connections prevent clean `process.exit()` (GitHub #25629).
**Why it happens:** Same root cause as the executor.ts pattern already worked around.
**How to avoid:** Apply the same `RESULT_FORCE_KILL_DELAY_MS` force-kill pattern used in `executor.ts`. For chat sessions using CLI, detect the `result` event and schedule SIGKILL.
**Warning signs:** Chat drawer shows "thinking..." indefinitely after first response.

### Pitfall 2: CLI --input-format stream-json Session Continuity
**What goes wrong:** `--input-format stream-json` feeds messages to the same session via stdin. If the process is killed and respawned, the session history is lost (no persistence).
**Why it happens:** Session state lives in the CLI process memory.
**How to avoid:** For SDK path, maintain message history as a `MessageParam[]` array in chat-manager.ts. For CLI path, rebuild context from NW journal + run summary on each reconnect.
**Warning signs:** NW-Claude "forgets" previous conversation after drawer close/reopen.

### Pitfall 3: Global SSE vs Per-Run SSE Confusion
**What goes wrong:** Frontend subscribes to per-run `/api/runs/:id/stream` expecting global events, or the global `/api/events` stream gets run-specific log noise.
**Why it happens:** Two separate SSE channels with different semantics.
**How to avoid:** Keep them strictly separated. `/api/events` = global lifecycle events only (brief-ready, config-changed). `/api/runs/:id/stream` = run log events only.
**Warning signs:** Console errors about unexpected event types; auto-brief fires on wrong page.

### Pitfall 4: Config Write Race Condition
**What goes wrong:** Two concurrent save requests for the same file corrupt the YAML.
**Why it happens:** Async file writes without locking.
**How to avoid:** Use a simple in-memory write lock per config file (a `Map<filename, Promise>`). Each write queues behind the previous one.
**Warning signs:** YAML syntax errors on load after what appeared to be a successful save.

### Pitfall 5: Feedback Button Double-Submit
**What goes wrong:** User clicks thumbs-up/down twice (network lag), submitting duplicate feedback entries.
**Why it happens:** Button not immediately disabled after first click.
**How to avoid:** Disable button optimistically on click (before API response). Track submitted signal_ids in frontend component state.
**Warning signs:** Same signal_id appears twice in feedback-store.yaml.

### Pitfall 6: Haiku Semantic Check Cost Overrun
**What goes wrong:** CONF-04 validation makes expensive Haiku calls for every keystroke or on large configs.
**Why it happens:** Haiku call triggered too eagerly.
**How to avoid:** Only call Haiku after user explicitly clicks "Validate" or "Save" (not on every textarea change). Use `max_tokens: 200` as hard cap. Log estimated cost in server response for transparency.
**Warning signs:** Anthropic billing spikes.

### Pitfall 7: Preact State Stale Closure in EventSource Handler
**What goes wrong:** Chat drawer EventSource handler captures stale state (e.g., old session ID) due to closure over initial render value.
**Why it happens:** EventSource handlers are registered once in useEffect but reference state values that change.
**How to avoid:** Use `useRef` for the EventSource instance and session ID, not `useState`. Close and reopen EventSource when target changes.
**Warning signs:** Chat responses appear in wrong target's drawer.

---

## Code Examples

Verified patterns from existing codebase:

### Extending IPC for Global SSE (ipc.ts pattern)
```typescript
// Source: app/server/ipc.ts — adapt existing SSEWriter type
type SSEWriter = { writeSSE: (data: { data: string; event?: string }) => Promise<void> }
const globalSubscribers = new Set<SSEWriter>()

// New route: GET /api/events
// Pattern mirrors stream.ts subscribeToRun
streamRoutes.get('/api/events', (c) => {
  return streamSSE(c, async (stream) => {
    const cleanup = subscribeGlobal(stream, c.req.raw.signal)
    const pingTimer = setInterval(() => {
      void stream.writeSSE({ data: '', event: 'ping' })
    }, 60_000)
    await stream.sleep(60 * 60_000)  // 1 hour max
    clearInterval(pingTimer)
    cleanup()
  })
})
```

### Chat Route (POST message pattern)
```typescript
// Source: app/server/routes/api.ts pattern
chatRoutes.post('/api/chat/:target/message', async (c) => {
  const target = decodeURIComponent(c.req.param('target'))
  const { message } = await c.req.json<{ message: string }>()
  const sessionId = randomUUID()

  // Enqueue message to chat-manager — non-blocking
  void chatManager.sendMessage(target, message, sessionId)
  return c.json({ session_id: sessionId }, 202)
})

chatRoutes.get('/api/chat/:target/stream', (c) => {
  const target = decodeURIComponent(c.req.param('target'))
  return streamSSE(c, async (stream) => {
    const cleanup = chatManager.subscribeToTarget(target, stream, c.req.raw.signal)
    await stream.sleep(10 * 60_000)  // 10 min timeout for chat
    cleanup()
  })
})
```

### Config Read/Write API Route
```typescript
// Source: yaml-store.ts readYamlFile pattern
configRoutes.get('/api/config/:file', async (c) => {
  const file = c.req.param('file') as 'targets' | 'safety'
  const paths = { targets: TARGETS_YAML_PATH, safety: SAFETY_YAML_PATH }
  if (!paths[file]) return c.json({ error: 'unknown config file' }, 400)
  const content = await Bun.file(paths[file]).text().catch(() => '')
  return c.json({ content })
})

configRoutes.put('/api/config/:file', async (c) => {
  const file = c.req.param('file') as 'targets' | 'safety'
  const { content } = await c.req.json<{ content: string }>()
  // Run 4-step validation before writing
  const result = await validateConfigSave(file, content, await Bun.file(paths[file]).text())
  if (!result.valid) return c.json(result, 422)
  await Bun.write(paths[file], content)
  return c.json({ ok: true })
})
```

### Frontend: Slide-Over Drawer Pattern
```typescript
// Source: trigger-dialog.ts pattern (position:fixed overlay)
// Drawer: position:fixed, right:0, top:0, height:100%, width:400px
// translate: 0 (open) vs translateX(100%) (closed)
function ChatDrawer({ isOpen, onClose, targetName }: Props) {
  if (typeof document === 'undefined') return null

  return html`
    <div style="
      position: fixed;
      inset: 0;
      z-index: 200;
      pointer-events: ${isOpen ? 'all' : 'none'};
    ">
      <!-- Backdrop (subtle, not modal-dark) -->
      <div
        style="position:absolute;inset:0;background:rgba(0,0,0,${isOpen ? '0.3' : '0'});transition:background 200ms;"
        onClick=${onClose}
      />
      <!-- Drawer panel -->
      <div style="
        position: absolute;
        right: 0; top: 0; bottom: 0;
        width: 400px;
        background: var(--panel);
        border-left: 1px solid var(--border);
        transform: translateX(${isOpen ? '0' : '100%'});
        transition: transform 200ms ease-out;
        display: flex;
        flex-direction: column;
      ">
        <!-- chat content -->
      </div>
    </div>
  `
}
```

### Feedback Button in Action Card
```typescript
// New action-card.ts
function FeedbackButtons({ signalId, onFeedback }: { signalId: string; onFeedback: (verdict: string) => void }) {
  const [submitted, setSubmitted] = useState<'accepted' | 'rejected' | null>(null)

  async function handleFeedback(verdict: 'accepted' | 'rejected') {
    setSubmitted(verdict)  // optimistic disable
    await api.submitFeedback({ signal_id: signalId, verdict })
  }

  return html`
    <div style="display:flex;gap:4px;">
      <button
        disabled=${submitted !== null}
        onClick=${() => handleFeedback('accepted')}
        style="
          padding: 3px 8px; font-size: 12px;
          background: ${submitted === 'accepted' ? 'var(--success)' : 'var(--btn-secondary)'};
          color: ${submitted === 'accepted' ? '#fff' : 'var(--muted)'};
          border: 1px solid ${submitted === 'accepted' ? 'var(--success)' : 'var(--border)'};
          border-radius: 4px; cursor: ${submitted ? 'default' : 'pointer'};
        "
      >+1</button>
      <button
        disabled=${submitted !== null}
        onClick=${() => handleFeedback('rejected')}
        style="
          padding: 3px 8px; font-size: 12px;
          background: ${submitted === 'rejected' ? 'var(--error)' : 'var(--btn-secondary)'};
          color: ${submitted === 'rejected' ? '#fff' : 'var(--muted)'};
          border: 1px solid ${submitted === 'rejected' ? 'var(--error)' : 'var(--border)'};
          border-radius: 4px; cursor: ${submitted ? 'default' : 'pointer'};
        "
      >-1</button>
    </div>
  `
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Claude CLI session for chat | @anthropic-ai/sdk (default) + CLI as spike/fallback | STATE.md decision 2026-03-18 | SDK loses plugin context but is reliable; document tradeoff in chat-manager.ts |
| Run-only SSE channels | Global SSE channel for lifecycle events | Phase 3 | Enables cross-page auto-brief without polling |
| Config edited via CLI | YAML editor with 4-step validation in UI | Phase 3 | Reduces config edit errors; safety rail before writing |
| Manual feedback only | Explicit (buttons) + implicit (PR/Linear polling) | Phase 3 | Flywheel seeded from both sources |

**Deprecated/outdated in this codebase:**
- `phases_completed` in RunSummary: Legacy Phase 1 compat field — still populated but superseded by `per_target` detailed structure
- Placeholder Config page (`app/frontend/pages/config.ts`): The full 13-line placeholder is replaced in Phase 3

---

## Open Questions

1. **Claude CLI --input-format stream-json session continuity for long chats**
   - What we know: Flag exists in v2.1.78; STATE.md says unreliable for long sessions
   - What's unclear: At what message count / session duration does it fail?
   - Recommendation: Spike uses a 5-message exchange. If clean, document the threshold. Default to SDK regardless.

2. **Haiku model name for validation**
   - What we know: `claude-haiku-4-5` is latest; previous versions used `claude-haiku-3-5`
   - What's unclear: Model availability in the user's API account
   - Recommendation: Make model name a constant in `config-validator.ts`. Default `claude-haiku-4-5`, fallback documented.

3. **nw_submit_feedback MCP tool scope**
   - What we know: FEED-03 requires MCP feedback tool; Phase 4 covers the full MCP server
   - What's unclear: Should the feedback tool be available to NW-Claude chat in Phase 3 (before full MCP server)?
   - Recommendation: Wire nw_submit_feedback as a direct REST call inside chat-manager.ts (NW-Claude calls the feedback API directly), not requiring the MCP server. Full MCP wiring deferred to Phase 4.

4. **Feedback store collision with existing nightwatch-feedback.yaml**
   - What we know: CLAUDE.md says this file is "Written each run by --self-repair session; Feedback from PR/issue status"
   - What's unclear: Does Phase 3 feedback.yaml extend the existing schema or use a separate explicit-feedback.yaml?
   - Recommendation: Extend the existing file with a new top-level `explicit_feedback:` key, keeping `pr_feedback:` and `linear_feedback:` separate. No migration needed.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Bun test (built-in) |
| Config file | none — `bun test` auto-discovers `**/*.test.ts` |
| Quick run command | `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test --timeout 10000` |
| Full suite command | `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONF-01/02/03 | Config read returns raw YAML text; locked state prevents PUT | unit | `bun test tests/server/config.test.ts` | ❌ Wave 0 |
| CONF-04 | 4-step validation rejects invalid YAML, calls Haiku, returns diff | unit (mock Haiku) | `bun test tests/server/config-validator.test.ts` | ❌ Wave 0 |
| CONF-05 | Config warnings read from self-repair.yaml | unit | included in config.test.ts | ❌ Wave 0 |
| CONF-06/07/08 | Add/Edit/Remove target wizard updates targets.yaml | unit | `bun test tests/server/config.test.ts` | ❌ Wave 0 |
| CHAT-03 | Chat session sends message, receives streaming response | integration (mock SDK) | `bun test tests/server/chat.test.ts` | ❌ Wave 0 |
| CHAT-07 | Kill session on target switch; keep alive on close | unit | included in chat.test.ts | ❌ Wave 0 |
| FEED-01/02 | POST /api/feedback appends entry to feedback store | unit | `bun test tests/server/feedback.test.ts` | ❌ Wave 0 |
| FEED-04/05 | PR/Linear polling writes feedback entries | unit (mock gh CLI) | `bun test tests/worker/feedback-collector.test.ts` | ❌ Wave 0 |
| FEED-06 | Reject rate calibration calculates threshold correctly | unit | included in feedback.test.ts | ❌ Wave 0 |
| ASSESS-03 | RunSummary.per_target[x].actions[y].assessment rendered in UI | manual smoke | visual check in browser | manual |
| MEAS-03 | Baseline summary card renders from RunSummary | manual smoke | visual check in browser | manual |

### Sampling Rate
- **Per task commit:** `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test --timeout 10000`
- **Per wave merge:** `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/server/config.test.ts` — covers CONF-01 through CONF-08
- [ ] `tests/server/config-validator.test.ts` — covers CONF-04 (mock Anthropic SDK call)
- [ ] `tests/server/chat.test.ts` — covers CHAT-03, CHAT-07 (mock SDK streaming)
- [ ] `tests/server/feedback.test.ts` — covers FEED-01, FEED-02, FEED-06
- [ ] `tests/worker/feedback-collector.test.ts` — covers FEED-04, FEED-05 (mock gh CLI)

---

## Sources

### Primary (HIGH confidence)
- Codebase direct read — `app/shared/types.ts`: RunSummaryAction, IndicatorBaseline, PerTargetSummary already typed
- Codebase direct read — `app/server/ipc.ts`: SSEWriter type, fan-out pattern, handleWorkerMessage
- Codebase direct read — `app/server/routes/api.ts`: Hono route pattern, error codes
- Codebase direct read — `app/server/routes/stream.ts`: streamSSE, keepalive ping, timeout pattern
- Codebase direct read — `app/server/services/yaml-store.ts`: readYamlFile, writeYamlFile, TARGETS_YAML_PATH
- Codebase direct read — `app/worker/executor.ts`: writeNwJournalConfig, ensureNwMemoryDir, RESULT_FORCE_KILL_DELAY_MS
- Codebase direct read — `app/frontend/components/trigger-dialog.ts`: modal pattern with role="dialog"
- Codebase direct read — `app/frontend/components/log-stream.ts`: EventSource SSE connection pattern
- `.planning/STATE.md`: Decision — "Use Anthropic SDK as chat default"
- `claude --help` output: `--input-format stream-json` confirmed available in v2.1.78

### Secondary (MEDIUM confidence)
- `npm view @anthropic-ai/sdk version` — v0.79.0 confirmed current on 2026-03-18
- `CLAUDE.md` (kc-nightwatch) — file ownership table for nightwatch-feedback.yaml
- `.planning/phases/03-flywheel-core/03-CONTEXT.md` — all implementation decisions

### Tertiary (LOW confidence)
- Haiku model name `claude-haiku-4-5` — from training data; verify before first call
- Chat message history approach for CLI path — inference from CLI behavior documentation

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — packages verified via npm, Bun version confirmed
- Architecture: HIGH — based on direct codebase reads, existing proven patterns
- Chat CLI pitfalls: MEDIUM — CLI hang pattern confirmed from executor.ts workaround; session reliability from STATE.md decision
- Haiku model naming: LOW — model names change; verify via API or docs before coding

**Research date:** 2026-03-18
**Valid until:** 2026-04-18 (stable patterns; @anthropic-ai/sdk may update)
