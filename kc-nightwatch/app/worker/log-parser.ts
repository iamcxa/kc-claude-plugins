import type { ParsedLogEvent } from '../shared/types.ts'

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

    return { type, content, raw: line }
  } catch {
    return { type: 'text', raw: line }
  }
}
