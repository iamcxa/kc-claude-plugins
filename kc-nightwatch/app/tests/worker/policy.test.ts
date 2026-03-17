import { describe, it, expect } from 'bun:test'
import { buildSafehouseFlags } from '../../worker/policy.ts'
import type { Run } from '../../shared/types.ts'

const target = { name: 'test-target', resolved_path: '/tmp/test-target' }
const baseRun: Run = {
  id: 'run-001',
  target: 'test-target',
  mode: 'production',
  trigger: 'manual',
  status: 'queued',
  log_path: '/tmp/runs/run-001/log.jsonl',
}

describe('buildSafehouseFlags', () => {
  it('uses --add-dirs-ro for dry-run mode', () => {
    const flags = buildSafehouseFlags(target, { ...baseRun, mode: 'dry-run' }, '/tmp/runs')
    const idx = flags.indexOf('--add-dirs-ro')
    expect(idx).toBeGreaterThanOrEqual(0)
    expect(flags[idx + 1]).toBe('/tmp/test-target')
  })

  it('uses --add-dirs for production mode', () => {
    const flags = buildSafehouseFlags(target, { ...baseRun, mode: 'production' }, '/tmp/runs')
    // --add-dirs appears for target dir
    expect(flags).toContain('--add-dirs')
    const idx = flags.indexOf('--add-dirs')
    expect(flags[idx + 1]).toBe('/tmp/test-target')
  })

  it('contains no tilde paths', () => {
    const flags = buildSafehouseFlags(target, baseRun, '/tmp/runs')
    const tildes = flags.filter(f => f.startsWith('~'))
    expect(tildes).toHaveLength(0)
  })

  it('includes run artifact dir', () => {
    const flags = buildSafehouseFlags(target, baseRun, '/tmp/runs')
    expect(flags.join(' ')).toContain('/tmp/runs/run-001')
  })
})
