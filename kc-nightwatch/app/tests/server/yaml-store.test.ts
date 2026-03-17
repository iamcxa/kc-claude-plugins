import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { loadOrCreateAppConfig, readYamlFile, writeYamlFile } from '../../server/services/yaml-store.ts'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

let testDir: string

beforeEach(async () => {
  testDir = await mkdtemp(join(tmpdir(), 'nw-yaml-'))
})

afterEach(async () => {
  await rm(testDir, { recursive: true, force: true })
})

describe('loadOrCreateAppConfig', () => {
  it('creates file with valid defaults on first call', async () => {
    const configPath = join(testDir, 'nightwatch-app.yaml')
    const config = await loadOrCreateAppConfig(configPath)
    expect(config.host).toBe('127.0.0.1')
    expect(config.port).toBe(3200)
    expect(config.max_concurrent_runs).toBe(1)
    expect(config.schedule.enabled).toBe(false)
    expect(await Bun.file(configPath).exists()).toBe(true)
  })

  it('reads existing file on second call without overwriting', async () => {
    const configPath = join(testDir, 'nightwatch-app.yaml')
    await loadOrCreateAppConfig(configPath)
    // Modify file manually
    await Bun.write(configPath, 'host: 127.0.0.1\nport: 9999\nmax_concurrent_runs: 1\nplugins_dir: /tmp\nschedule:\n  enabled: false\n  self_repair_before: true\n')
    const config2 = await loadOrCreateAppConfig(configPath)
    expect(config2.port).toBe(9999)
  })

  it('throws Zod error on invalid max_concurrent_runs', async () => {
    const configPath = join(testDir, 'nightwatch-app.yaml')
    await Bun.write(configPath, 'host: 127.0.0.1\nport: 3200\nmax_concurrent_runs: 2\nplugins_dir: /tmp\nschedule:\n  enabled: false\n  self_repair_before: true\n')
    await expect(loadOrCreateAppConfig(configPath)).rejects.toThrow()
  })
})

describe('readYamlFile', () => {
  it('returns null for non-existent file', async () => {
    const result = await readYamlFile(join(testDir, 'nonexistent.yaml'))
    expect(result).toBeNull()
  })

  it('roundtrips data through write then read', async () => {
    const filePath = join(testDir, 'test.yaml')
    const data = { name: 'test', value: 42, nested: { flag: true } }
    await writeYamlFile(filePath, data)
    const result = await readYamlFile<typeof data>(filePath)
    expect(result?.name).toBe('test')
    expect(result?.value).toBe(42)
    expect(result?.nested.flag).toBe(true)
  })
})
