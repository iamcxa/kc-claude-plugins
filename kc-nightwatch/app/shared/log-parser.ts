import type { ParsedLogEvent } from './types.ts'

export function parseStreamJsonLine(line: string): ParsedLogEvent {
  try {
    const obj = JSON.parse(line) as Record<string, unknown>
    const type = typeof obj.type === 'string' ? obj.type : 'unknown'

    // Extract readable content from assistant messages
    let content: string | undefined
    if (type === 'assistant' && obj.message && typeof obj.message === 'object') {
      const msg = obj.message as Record<string, unknown>
      if (Array.isArray(msg.content)) {
        const textBlock = msg.content.find(
          (b: unknown) => typeof b === 'object' && b !== null && (b as Record<string, unknown>).type === 'text'
        ) as Record<string, unknown> | undefined
        if (textBlock) content = String(textBlock.text ?? '')
      }
    }
    if (type === 'result' && typeof obj.result === 'string') {
      content = obj.result
    }

    // Phase 2: extract phase, tool_name, agent_name
    let phase: string | undefined
    let tool_name: string | undefined
    let agent_name: string | undefined
    let is_phase_start: boolean | undefined

    if (type === 'assistant' && content) {
      const phaseMatch = content.match(/Phase\s+(\d+(?:\.\d+)?)/i)
      if (phaseMatch) {
        phase = `Phase ${phaseMatch[1]}`
        is_phase_start = true
      }
      const agentMatch = content.match(/(?:Dispatching|Running|Starting)\s+(\S+)\s+agent/i)
      if (agentMatch) agent_name = agentMatch[1]
    }
    if (type === 'tool_use' && typeof obj.name === 'string') {
      tool_name = obj.name
    }

    return { type, content, raw: line, phase, tool_name, agent_name, is_phase_start }
  } catch {
    return { type: 'text', raw: line }
  }
}
