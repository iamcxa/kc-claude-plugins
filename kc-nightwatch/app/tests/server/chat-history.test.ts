import { describe, it, expect } from 'bun:test'
import { extractDisplayContent } from '../../server/routes/chat.ts'

describe('extractDisplayContent', () => {
  it('returns string content as-is', () => {
    expect(extractDisplayContent('hello world')).toBe('hello world')
  })

  it('extracts text from text-only content blocks', () => {
    const blocks = [{ type: 'text', text: 'Here is the answer.' }]
    expect(extractDisplayContent(blocks)).toBe('Here is the answer.')
  })

  it('extracts text from mixed text + tool_use blocks', () => {
    const blocks = [
      { type: 'text', text: 'Let me check that.' },
      { type: 'tool_use', id: 'tu_1', name: 'nw_get_targets', input: {} },
      { type: 'text', text: 'Found 3 targets.' },
    ]
    expect(extractDisplayContent(blocks)).toBe('Let me check that.\nFound 3 targets.')
  })

  it('returns null for tool_result messages', () => {
    const blocks = [
      { type: 'tool_result', tool_use_id: 'tu_1', content: '{"targets":[]}' },
    ]
    expect(extractDisplayContent(blocks)).toBeNull()
  })

  it('returns null for tool_use-only blocks (no text)', () => {
    const blocks = [
      { type: 'tool_use', id: 'tu_1', name: 'nw_get_targets', input: {} },
    ]
    // No text parts → empty join → null
    expect(extractDisplayContent(blocks)).toBeNull()
  })

  it('returns null for empty array', () => {
    expect(extractDisplayContent([])).toBeNull()
  })

  it('stringifies non-string non-array content', () => {
    expect(extractDisplayContent(42)).toBe('42')
  })
})
