import Anthropic from '@anthropic-ai/sdk'
import type { MessageParam } from '@anthropic-ai/sdk/resources/messages'
import { randomUUID } from 'node:crypto'
import { log } from '../../shared/logger.ts'
import type { ChatMessage, RunSummary } from '../../shared/types.ts'

type SSEWriter = { writeSSE: (data: { data: string; event?: string }) => Promise<void> }

interface ChatSession {
  targetName: string
  messages: MessageParam[]
  briefContext?: RunSummary
  subscribers: Set<SSEWriter>
}

const sessions = new Map<string, ChatSession>()
let anthropicClient: Anthropic | null = null

function getClient(): Anthropic {
  if (!anthropicClient) {
    anthropicClient = new Anthropic()
  }
  return anthropicClient
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
  sessions.delete(targetName)
  log.info({ component: 'chat', msg: `Session killed for target: ${targetName}` })
}

export function killAllSessions(): void {
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
    const stream = client.messages.stream({
      model: 'claude-haiku-4-5',
      max_tokens: 2048,
      system: systemPrompt,
      messages: session.messages,
    })

    let fullResponse = ''

    // Signal start of response
    for (const writer of session.subscribers) {
      void writer.writeSSE({ data: JSON.stringify({ type: 'start', id: randomUUID() }), event: 'chat' })
    }

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
        const chunk = event.delta.text
        fullResponse += chunk
        for (const writer of session.subscribers) {
          void writer.writeSSE({ data: JSON.stringify({ type: 'delta', content: chunk }), event: 'chat' })
        }
      }
    }

    // Add assistant response to history
    session.messages.push({ role: 'assistant', content: fullResponse })

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
