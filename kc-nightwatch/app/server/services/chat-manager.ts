import Anthropic from '@anthropic-ai/sdk'
import type { MessageParam } from '@anthropic-ai/sdk/resources/messages'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'
import { randomUUID } from 'node:crypto'
import { log } from '../../shared/logger.ts'
import type { RunSummary } from '../../shared/types.ts'
import { loadOrCreateAppConfig } from './yaml-store.ts'

type SSEWriter = { writeSSE: (data: { data: string; event?: string }) => Promise<void> }

interface ChatSession {
  targetName: string
  messages: MessageParam[]
  briefContext?: RunSummary
  subscribers: Set<SSEWriter>
  mcpClient?: Client // Lazy-initialized MCP client per session
}

// ============================================================
// NW tool schemas — 15 Anthropic tool definitions
// (7 query + 1 search + 4 action + 3 outcome = 15 MCP tools)
// ============================================================
export const NW_TOOLS: Anthropic.Tool[] = [
  // Query (7)
  {
    name: 'nw_get_targets',
    description: 'List all configured nightwatch monitoring targets with their type, north star, and indicators',
    input_schema: { type: 'object', properties: {}, required: [] },
  },
  {
    name: 'nw_get_latest_run',
    description: 'Get the most recent run. Optionally filter by target name.',
    input_schema: {
      type: 'object',
      properties: {
        target: { type: 'string', description: 'Target name to filter (optional)' },
      },
      required: [],
    },
  },
  {
    name: 'nw_get_run',
    description: 'Get details for a specific run by ID, including summary with actions and indicator baselines',
    input_schema: {
      type: 'object',
      properties: {
        run_id: { type: 'string', description: 'The run ID to fetch' },
      },
      required: ['run_id'],
    },
  },
  {
    name: 'nw_get_proposals',
    description: 'Get runs that contain proposal actions. Optionally filter by target.',
    input_schema: {
      type: 'object',
      properties: {
        target: { type: 'string', description: 'Target name to filter (optional)' },
      },
      required: [],
    },
  },
  {
    name: 'nw_get_config_warnings',
    description: 'Get configuration warnings from the last self-repair run',
    input_schema: { type: 'object', properties: {}, required: [] },
  },
  {
    name: 'nw_get_schedule',
    description: 'Get the current nightwatch schedule configuration (enabled, interval, self-repair)',
    input_schema: { type: 'object', properties: {}, required: [] },
  },
  {
    name: 'nw_read_journal',
    description:
      'Read recent entries from a target-specific nightwatch journal. Contains debug process, technical insights, feedback trends.',
    input_schema: {
      type: 'object',
      properties: {
        target: { type: 'string', description: 'Target name' },
        limit: { type: 'number', description: 'Max entries to return (default 5)' },
      },
      required: ['target'],
    },
  },
  // Search (1)
  {
    name: 'nw_search_journal',
    description: 'Search a target-specific nightwatch journal for entries matching a query string',
    input_schema: {
      type: 'object',
      properties: {
        target: { type: 'string', description: 'Target name' },
        query: { type: 'string', description: 'Search query (case-insensitive)' },
      },
      required: ['target', 'query'],
    },
  },
  // Action (4)
  {
    name: 'nw_trigger_run',
    description: 'Trigger a nightwatch run for a target. Returns the run ID. Use __all__ for all targets.',
    input_schema: {
      type: 'object',
      properties: {
        target: { type: 'string', description: 'Target name or __all__' },
        mode: {
          type: 'string',
          enum: ['production', 'dry-run'],
          description: 'Run mode (default: production)',
        },
        custom_prompt: { type: 'string', description: 'Optional custom instructions for the run' },
      },
      required: ['target'],
    },
  },
  {
    name: 'nw_submit_feedback',
    description:
      'Submit feedback (accepted/rejected) for a signal action. Used to calibrate future improvement decisions.',
    input_schema: {
      type: 'object',
      properties: {
        signal_id: { type: 'string', description: 'Signal ID from an action card' },
        target: { type: 'string', description: 'Target name' },
        run_id: { type: 'string', description: 'Run ID the signal belongs to' },
        verdict: { type: 'string', enum: ['accepted', 'rejected'], description: 'Feedback verdict' },
        reason: { type: 'string', description: 'Optional reason for the verdict' },
      },
      required: ['signal_id', 'target', 'run_id', 'verdict'],
    },
  },
  {
    name: 'nw_update_schedule',
    description: 'Update the nightwatch schedule. Can enable/disable or change interval.',
    input_schema: {
      type: 'object',
      properties: {
        enabled: { type: 'boolean', description: 'Enable or disable the scheduler' },
        interval_hours: { type: 'number', description: 'Hours between scheduled runs' },
      },
      required: [],
    },
  },
  {
    name: 'nw_implement_proposal',
    description:
      'Request implementation of a nightwatch proposal. Currently a stub that suggests using nw_trigger_run instead.',
    input_schema: {
      type: 'object',
      properties: {
        proposal_id: { type: 'string', description: 'Proposal ID to implement' },
      },
      required: ['proposal_id'],
    },
  },
  // Outcome (3)
  {
    name: 'nw_get_outcomes',
    description: 'List nightwatch-created PRs and Linear issues. Filter by target, type (pr/linear_issue), status, or date range (since).',
    input_schema: {
      type: 'object',
      properties: {
        target: { type: 'string', description: 'Filter by target name (optional)' },
        type: { type: 'string', enum: ['pr', 'linear_issue'], description: 'Filter by outcome type (optional)' },
        status: { type: 'string', description: 'Filter by status: open, merged, closed, completed, cancelled (optional)' },
        since: { type: 'string', description: 'Filter by created_at >= this ISO date (e.g. 2026-03-20) (optional)' },
      },
      required: [],
    },
  },
  {
    name: 'nw_get_outcome_status',
    description: 'Check the live status of a specific outcome (PR or Linear issue) by its outcome ID. Polls GitHub/Linear API for current state.',
    input_schema: {
      type: 'object',
      properties: {
        outcome_id: { type: 'string', description: 'The outcome record ID to check live status for' },
      },
      required: ['outcome_id'],
    },
  },
  {
    name: 'nw_outcome_summary',
    description: 'Get aggregated outcome stats: total count, count by type+status, count by target, recent 7-day count. Use for overview questions.',
    input_schema: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
]

const MAX_TOOL_ROUNDS = 10

const sessions = new Map<string, ChatSession>()
let anthropicClient: Anthropic | null = null

function getClient(): Anthropic {
  if (!anthropicClient) {
    anthropicClient = new Anthropic()
  }
  return anthropicClient
}

async function getMcpClient(session: ChatSession): Promise<Client> {
  if (session.mcpClient) return session.mcpClient

  const config = await loadOrCreateAppConfig()
  const port = config.port ?? 3200
  const token = config.auth_token

  const client = new Client({ name: 'nw-chat', version: '1.0.0' })
  const transportOpts = token
    ? { requestInit: { headers: { Authorization: `Bearer ${token}` } } }
    : undefined
  const transport = new StreamableHTTPClientTransport(new URL(`http://localhost:${port}/mcp`), transportOpts)
  await client.connect(transport)
  session.mcpClient = client
  return client
}

export function getOrCreateSession(targetName: string): ChatSession {
  if (!sessions.has(targetName)) {
    sessions.set(targetName, {
      targetName,
      messages: [],
      subscribers: new Set(),
    })
  }
  return sessions.get(targetName)!
}

export function killSession(targetName: string): void {
  const session = sessions.get(targetName)
  if (session?.mcpClient) {
    session.mcpClient.close().catch(() => {}) // Best-effort close
  }
  sessions.delete(targetName)
  log.info({ component: 'chat', msg: `Session killed for target: ${targetName}` })
}

export function killAllSessions(): void {
  for (const [, session] of sessions) {
    if (session.mcpClient) {
      session.mcpClient.close().catch(() => {})
    }
  }
  sessions.clear()
}

export function listSessions(): string[] {
  return [...sessions.keys()]
}

export function subscribeToTarget(targetName: string, writer: SSEWriter, signal: AbortSignal): () => void {
  const session = getOrCreateSession(targetName)
  session.subscribers.add(writer)
  const cleanup = () => session.subscribers.delete(writer)
  signal.addEventListener('abort', cleanup)
  return cleanup
}

export function setBriefContext(targetName: string, summary: RunSummary): void {
  const session = getOrCreateSession(targetName)
  session.briefContext = summary
}

export async function sendMessage(targetName: string, userMessage: string): Promise<void> {
  const session = getOrCreateSession(targetName)
  const client = getClient()

  // Add user message to history
  session.messages.push({ role: 'user', content: userMessage })

  // Build system prompt with target context
  const systemPrompt = buildSystemPrompt(targetName, session.briefContext)

  try {
    // Signal start of response
    for (const writer of session.subscribers) {
      void writer.writeSSE({ data: JSON.stringify({ type: 'start', id: randomUUID() }), event: 'chat' })
    }

    let rounds = 0
    let fullResponse = ''

    while (rounds < MAX_TOOL_ROUNDS) {
      rounds++

      const response = await client.messages.create({
        model: 'claude-haiku-4-5',
        max_tokens: 2048,
        system: systemPrompt,
        messages: session.messages,
        tools: NW_TOOLS,
      })

      // Process content blocks
      let hasToolUse = false
      const toolResults: MessageParam[] = []

      for (const block of response.content) {
        if (block.type === 'text') {
          fullResponse += block.text
          // Stream text deltas to subscribers
          for (const writer of session.subscribers) {
            void writer.writeSSE({ data: JSON.stringify({ type: 'delta', content: block.text }), event: 'chat' })
          }
        } else if (block.type === 'tool_use') {
          hasToolUse = true
          // Route tool call to MCP server
          try {
            const mcpClient = await getMcpClient(session)
            const result = await mcpClient.callTool({
              name: block.name,
              arguments: block.input as Record<string, unknown>,
            })
            const resultText = (result.content as Array<{ type: string; text: string }>).map((c) => c.text).join('\n')

            // Build tool_result message
            toolResults.push({
              role: 'user',
              content: [
                {
                  type: 'tool_result' as const,
                  tool_use_id: block.id,
                  content: resultText,
                },
              ] as unknown as string,
            })
          } catch (err) {
            toolResults.push({
              role: 'user',
              content: [
                {
                  type: 'tool_result' as const,
                  tool_use_id: block.id,
                  content: `Tool error: ${String(err)}`,
                  is_error: true,
                },
              ] as unknown as string,
            })
          }
        }
      }

      // Append assistant message (with text + tool_use blocks)
      session.messages.push({ role: 'assistant', content: response.content as unknown as string })

      if (hasToolUse && toolResults.length > 0) {
        // Append tool results and continue loop
        session.messages.push(...toolResults)
      }

      if (response.stop_reason !== 'tool_use') {
        break // Final response — no more tool calls
      }
    }

    // Signal end of response
    for (const writer of session.subscribers) {
      void writer.writeSSE({ data: JSON.stringify({ type: 'end', content: fullResponse }), event: 'chat' })
    }
  } catch (err) {
    log.error({ component: 'chat', msg: `Chat error for ${targetName}: ${String(err)}` })
    for (const writer of session.subscribers) {
      void writer.writeSSE({ data: JSON.stringify({ type: 'error', error: String(err) }), event: 'chat' })
    }
  }
}

function buildSystemPrompt(targetName: string, briefContext?: RunSummary): string {
  let prompt = `You are NW-Claude, the Nightwatch assistant for target "${targetName}". `
  prompt += 'Help the user understand run results, config changes, improvement signals, and trends. '
  prompt += 'Be concise and direct. Refer to specific signals, indicators, and actions from recent runs.'

  if (briefContext) {
    const targetData = briefContext.per_target[targetName]
    if (targetData) {
      prompt += `\n\nLatest run summary for ${targetName}:\n`
      prompt += `- Signals found: ${targetData.pipeline.found}\n`
      prompt += `- Actions taken: ${targetData.actions.length}\n`
      if (targetData.actions.length > 0) {
        prompt += '- Actions:\n'
        for (const a of targetData.actions) {
          prompt += `  - [${a.type}] ${a.summary} (indicator: ${a.indicator}, confidence: ${a.assessment.confidence})\n`
        }
      }
      if (Object.keys(targetData.indicator_baseline).length > 0) {
        prompt += '- Indicator baselines:\n'
        for (const [name, b] of Object.entries(targetData.indicator_baseline)) {
          prompt += `  - ${name}: ${b.value} (${b.measurement}, trend: ${b.trend})\n`
        }
      }
      if (targetData.pre_assessment) prompt += `\nPre-action assessment: ${targetData.pre_assessment}\n`
      if (targetData.post_assessment) prompt += `Post-action reflection: ${targetData.post_assessment}\n`
    }
  }

  return prompt
}
