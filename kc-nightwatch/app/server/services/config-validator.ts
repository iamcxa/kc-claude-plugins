import { parse } from 'yaml'
import Anthropic from '@anthropic-ai/sdk'
import { log } from '../../shared/logger.ts'
import type { ConfigValidationResult } from '../../shared/types.ts'

const HAIKU_MODEL = 'claude-haiku-4-5'
const HAIKU_MAX_TOKENS = 200  // $0.05 cap enforcement

// Simple in-memory write lock per config file (Pitfall 4 from RESEARCH.md)
const writeLocks = new Map<string, Promise<void>>()

export async function withWriteLock<T>(file: string, fn: () => Promise<T>): Promise<T> {
  const prev = writeLocks.get(file) ?? Promise.resolve()
  let resolve!: () => void
  const lock = new Promise<void>(r => { resolve = r })
  writeLocks.set(file, lock)
  await prev
  try {
    return await fn()
  } finally {
    resolve()
  }
}

export async function validateConfigSave(
  file: 'targets' | 'safety',
  newYaml: string,
  originalYaml: string
): Promise<ConfigValidationResult> {
  // Step 1: Static YAML parse
  try {
    parse(newYaml)
  } catch (e) {
    return { valid: false, step: 'static', error: String(e) }
  }

  // Step 2: Haiku semantic check
  try {
    const client = new Anthropic()
    const check = await client.messages.create({
      model: HAIKU_MODEL,
      max_tokens: HAIKU_MAX_TOKENS,
      messages: [{
        role: 'user',
        content: `Review this nightwatch ${file} config change. Are there any dangerous, invalid, or problematic values? Respond with exactly "OK" if everything looks fine, or "WARN: [reason]" if there are concerns.\n\nOriginal:\n\`\`\`yaml\n${originalYaml}\n\`\`\`\n\nNew:\n\`\`\`yaml\n${newYaml}\n\`\`\``,
      }],
    })
    const verdict = check.content[0].type === 'text' ? check.content[0].text : 'OK'

    // Step 3: Compute line diff
    const diff = computeLineDiff(originalYaml, newYaml)

    return { valid: true, step: 'ready', haiku_verdict: verdict, diff }
  } catch (err) {
    log.warn({ component: 'config-validator', msg: `Haiku check failed: ${String(err)}` })
    // Fail open — if Haiku fails, still allow save but warn
    const diff = computeLineDiff(originalYaml, newYaml)
    return { valid: true, step: 'ready', haiku_verdict: `WARN: Semantic check unavailable (${String(err)})`, diff }
  }
}

function computeLineDiff(
  original: string,
  updated: string
): Array<{ type: 'add' | 'remove' | 'same'; line: string }> {
  const origLines = original.split('\n')
  const newLines = updated.split('\n')
  const result: Array<{ type: 'add' | 'remove' | 'same'; line: string }> = []

  let oi = 0, ni = 0
  while (oi < origLines.length || ni < newLines.length) {
    const origLine = oi < origLines.length ? origLines[oi] : undefined
    const newLine = ni < newLines.length ? newLines[ni] : undefined

    if (origLine === newLine) {
      result.push({ type: 'same', line: origLine ?? '' })
      oi++; ni++
    } else if (origLine !== undefined && !newLines.includes(origLine)) {
      result.push({ type: 'remove', line: origLine })
      oi++
    } else if (newLine !== undefined && !origLines.includes(newLine)) {
      result.push({ type: 'add', line: newLine })
      ni++
    } else {
      // Changed line — show as remove + add
      if (origLine !== undefined) {
        result.push({ type: 'remove', line: origLine })
        oi++
      }
      if (newLine !== undefined) {
        result.push({ type: 'add', line: newLine })
        ni++
      }
    }
  }
  return result
}
