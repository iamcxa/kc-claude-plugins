import { describe, it, expect, mock } from 'bun:test'

// Mock Anthropic SDK before importing
mock.module('@anthropic-ai/sdk', () => ({
  default: class MockAnthropic {
    messages = {
      create: async () => ({
        content: [{ type: 'text', text: 'OK' }],
      }),
    }
  },
}))

import { validateConfigSave, withWriteLock } from '../../server/services/config-validator.ts'

describe('config-validator', () => {
  it('rejects invalid YAML at step 1 (static parse)', async () => {
    const result = await validateConfigSave('targets', '{ broken yaml: [', 'valid: true')
    expect(result.valid).toBe(false)
    expect(result.step).toBe('static')
    expect(result.error).toBeDefined()
  })

  it('passes valid YAML through all 4 steps', async () => {
    const result = await validateConfigSave('targets', 'valid: true\nfoo: bar', 'valid: true')
    expect(result.valid).toBe(true)
    expect(result.step).toBe('ready')
    expect(result.haiku_verdict).toBeDefined()
    expect(result.diff).toBeDefined()
  })

  it('computes diff correctly for added lines', async () => {
    const result = await validateConfigSave('targets', 'a: 1\nb: 2\nc: 3', 'a: 1\nb: 2')
    expect(result.diff).toBeDefined()
    const addedLines = result.diff!.filter(d => d.type === 'add')
    expect(addedLines.length).toBeGreaterThan(0)
    expect(addedLines.some(d => d.line === 'c: 3')).toBe(true)
  })

  it('computes diff correctly for removed lines', async () => {
    const result = await validateConfigSave('targets', 'a: 1', 'a: 1\nb: 2')
    expect(result.diff).toBeDefined()
    const removedLines = result.diff!.filter(d => d.type === 'remove')
    expect(removedLines.length).toBeGreaterThan(0)
    expect(removedLines.some(d => d.line === 'b: 2')).toBe(true)
  })

  it('withWriteLock serializes concurrent writes', async () => {
    const order: number[] = []
    const p1 = withWriteLock('test', async () => {
      await Bun.sleep(50)
      order.push(1)
    })
    const p2 = withWriteLock('test', async () => {
      order.push(2)
    })
    await Promise.all([p1, p2])
    expect(order).toEqual([1, 2])
  })
})
