import { describe, it, expect } from 'bun:test'
import { parseStreamJsonLine } from '../../worker/log-parser.ts'

describe('parseStreamJsonLine', () => {
  it('parses result event type', () => {
    const e = parseStreamJsonLine('{"type":"result","result":"done"}')
    expect(e.type).toBe('result')
    expect(e.content).toBe('done')
  })

  it('extracts text from assistant message', () => {
    const line = JSON.stringify({
      type: 'assistant',
      message: { content: [{ type: 'text', text: 'Phase 1 complete' }] }
    })
    const e = parseStreamJsonLine(line)
    expect(e.type).toBe('assistant')
    expect(e.content).toContain('Phase 1')
  })

  it('handles invalid JSON gracefully', () => {
    const e = parseStreamJsonLine('not json at all')
    expect(e.type).toBe('text')
    expect(e.raw).toBe('not json at all')
  })

  it('preserves raw line in all cases', () => {
    const line = '{"type":"tool_use","id":"abc"}'
    const e = parseStreamJsonLine(line)
    expect(e.raw).toBe(line)
  })
})
