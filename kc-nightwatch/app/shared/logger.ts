// shared/logger.ts
type Level = 'debug' | 'info' | 'warn' | 'error'
type LogEntry = { ts?: string; level?: Level; component: string; msg: string; [key: string]: unknown }

const LOG_LEVEL: Level = (process.env.LOG_LEVEL as Level) ?? 'info'
const LEVELS: Record<Level, number> = { debug: 0, info: 1, warn: 2, error: 3 }

export const log = {
  debug: (e: LogEntry) => LEVELS[LOG_LEVEL] <= 0 && console.log(JSON.stringify({ ts: new Date().toISOString(), level: 'debug', ...e })),
  info:  (e: LogEntry) => LEVELS[LOG_LEVEL] <= 1 && console.log(JSON.stringify({ ts: new Date().toISOString(), level: 'info', ...e })),
  warn:  (e: LogEntry) => LEVELS[LOG_LEVEL] <= 2 && console.warn(JSON.stringify({ ts: new Date().toISOString(), level: 'warn', ...e })),
  error: (e: LogEntry) => LEVELS[LOG_LEVEL] <= 3 && console.error(JSON.stringify({ ts: new Date().toISOString(), level: 'error', ...e })),
}
