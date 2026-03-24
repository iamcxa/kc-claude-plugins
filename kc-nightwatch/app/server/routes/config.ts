import { Hono } from 'hono'
import path from 'node:path'
import os from 'node:os'
import { parse, stringify } from 'yaml'
import { readYamlFile, TARGETS_YAML_PATH } from '../services/yaml-store.ts'
import { validateConfigSave, withWriteLock } from '../services/config-validator.ts'
import { sendToWorker } from '../ipc.ts'
import { MIN_SCHEDULE_INTERVAL_HOURS } from '../../shared/constants.ts'

export const configRoutes = new Hono()

const SAFETY_YAML_PATH = path.resolve(new URL('../../../config/safety.yaml', import.meta.url).pathname)
const SELF_REPAIR_YAML_PATH = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-self-repair.yaml')

const CONFIG_PATHS: Record<string, string> = {
  targets: TARGETS_YAML_PATH,
  safety: SAFETY_YAML_PATH,
}

// GET /api/config/warnings — read self-repair warnings (must be BEFORE /api/config/:file to avoid param capture)
configRoutes.get('/api/config/warnings', async (c) => {
  const data = await readYamlFile<Record<string, unknown>>(SELF_REPAIR_YAML_PATH)
  return c.json({ warnings: data ?? {} })
})

// GET /api/config/:file — read raw YAML text
configRoutes.get('/api/config/:file', async (c) => {
  const file = c.req.param('file')
  const filePath = CONFIG_PATHS[file]
  if (!filePath) return c.json({ error: 'unknown config file' }, 400)

  try {
    const content = await Bun.file(filePath).text()
    return c.json({ content })
  } catch {
    return c.json({ content: '' })
  }
})

// PUT /api/config/:file — validate and write config
configRoutes.put('/api/config/:file', async (c) => {
  const file = c.req.param('file') as 'targets' | 'safety'
  const filePath = CONFIG_PATHS[file]
  if (!filePath) return c.json({ error: 'unknown config file' }, 400)

  const { content, confirm } = await c.req.json<{ content: string; confirm?: boolean }>()

  if (confirm) {
    // Final write — uses write lock to prevent race (Pitfall 4)
    await withWriteLock(file, async () => {
      await Bun.write(filePath, content)
    })
    return c.json({ ok: true })
  }

  // Validation only (confirm=false or absent)
  const original = await Bun.file(filePath).text().catch(() => '')
  const result = await validateConfigSave(file, content, original)
  return c.json(result)
})

// POST /api/config/targets/add — add a new target entry
configRoutes.post('/api/config/targets/add', async (c) => {
  const { name, target } = await c.req.json<{ name: string; target: Record<string, unknown> }>()
  if (!name?.trim()) return c.json({ error: 'name required' }, 400)

  let conflict = false
  await withWriteLock('targets', async () => {
    const raw = await Bun.file(TARGETS_YAML_PATH).text().catch(() => 'targets: {}')
    const parsed = (parse(raw) as { targets: Record<string, unknown> }) ?? { targets: {} }
    if (!parsed.targets) parsed.targets = {}
    if (parsed.targets[name]) {
      conflict = true
      return
    }
    parsed.targets[name] = target
    await Bun.write(TARGETS_YAML_PATH, stringify(parsed))
  })
  if (conflict) return c.json({ error: 'target already exists' }, 409)
  return c.json({ ok: true }, 201)
})

// PUT /api/config/targets/:name — edit an existing target (merge, not replace)
configRoutes.put('/api/config/targets/:name', async (c) => {
  const name = decodeURIComponent(c.req.param('name'))
  const { target } = await c.req.json<{ target: Record<string, unknown> }>()

  let notFound = false
  await withWriteLock('targets', async () => {
    const raw = await Bun.file(TARGETS_YAML_PATH).text()
    const parsed = parse(raw) as { targets: Record<string, unknown> }
    if (!parsed.targets?.[name]) {
      notFound = true
      return
    }
    // Merge wizard fields into existing target — preserves fields the wizard
    // doesn't manage (repo, proxy_signals, sentry_projects, extra_plugin_dirs, etc.)
    const existing = parsed.targets[name] as Record<string, unknown>
    parsed.targets[name] = { ...existing, ...target }
    // If wizard sends useGlobalSchedule (no schedule key), remove any existing per-target schedule
    if (!target.schedule && existing.schedule) {
      delete (parsed.targets[name] as Record<string, unknown>).schedule
    }
    await Bun.write(TARGETS_YAML_PATH, stringify(parsed))
  })
  if (notFound) return c.json({ error: 'target not found' }, 404)

  // Validate min interval (server-side, mirrors api.ts validation)
  const schedule = target.schedule as { interval_hours?: number } | undefined
  if (schedule?.interval_hours !== undefined && schedule.interval_hours < MIN_SCHEDULE_INTERVAL_HOURS) {
    return c.json({ error: `interval_hours ${schedule.interval_hours} is below minimum ${MIN_SCHEDULE_INTERVAL_HOURS} hours` }, 400)
  }

  // Reload scheduler with updated config so timer changes take effect immediately
  const scheduleConfig = await readYamlFile<{ schedule?: { enabled: boolean; interval_hours: number } }>(
    path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-config.yaml')
  )
  if (scheduleConfig?.schedule) {
    sendToWorker({ type: 'schedule', config: scheduleConfig.schedule as any })
  }

  return c.json({ ok: true })
})

// DELETE /api/config/targets/:name — remove a target
configRoutes.delete('/api/config/targets/:name', async (c) => {
  const name = decodeURIComponent(c.req.param('name'))

  let notFound = false
  await withWriteLock('targets', async () => {
    const raw = await Bun.file(TARGETS_YAML_PATH).text()
    const parsed = parse(raw) as { targets: Record<string, unknown> }
    if (!parsed.targets?.[name]) {
      notFound = true
      return
    }
    delete parsed.targets[name]
    await Bun.write(TARGETS_YAML_PATH, stringify(parsed))
  })
  if (notFound) return c.json({ error: 'target not found' }, 404)
  return c.json({ ok: true })
})
