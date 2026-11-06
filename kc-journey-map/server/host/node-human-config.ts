import { readFileSync } from 'node:fs'
import { validateHumanConfig } from './human-store'

export function nodeHumanConfig(env: NodeJS.ProcessEnv = process.env) {
 if (!env.JOURNEY_HUMAN_CONFIG) return undefined
 if (!env.JOURNEY_PRIVATE_DIR) throw new Error('human entry requires private storage')
 const config = validateHumanConfig(JSON.parse(readFileSync(env.JOURNEY_HUMAN_CONFIG, 'utf8')), env.JOURNEY_ORIGIN || 'http://localhost:3737')
 if (config.mode === 'local' && config.localOwnerUid !== process.geteuid?.()) throw new Error('local owner must be the service OS account')
 return config
}
