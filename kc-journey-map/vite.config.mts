import { hostname } from 'node:os'
import { readFileSync } from 'node:fs'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { clientApiProxy } from './server/client-api-proxy.ts'

// The machine's own hostname is always admitted; JOURNEY_ALLOWED_HOSTS adds a
// comma-separated list (e.g. a cloud or Tailscale DNS name) without editing this file.
const extraHosts = (process.env.JOURNEY_ALLOWED_HOSTS ?? '')
	.split(',')
	.map((h) => h.trim())
	.filter(Boolean)

const API = `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

export default defineConfig(() => ({
 define: { 'import.meta.env.VITE_JOURNEY_HUMAN_ENTRY': JSON.stringify(process.env.JOURNEY_HUMAN_CONFIG ? 'true' : process.env.VITE_JOURNEY_HUMAN_ENTRY || 'false') },
	plugins: [react(), {
   name: 'private-local-entry-loopback',
   configureServer(server) {
    const file = process.env.JOURNEY_HUMAN_CONFIG
    if (!file || JSON.parse(readFileSync(file, 'utf8')).mode !== 'local') return
    const bind = server.config.server.host
    if (bind !== undefined && bind !== '127.0.0.1' && bind !== 'localhost' && bind !== '::1') throw new Error('local human entry requires loopback-only browser binding')
    server.middlewares.use((req, res, next) => {
     if (!['127.0.0.1', '::1', '::ffff:127.0.0.1'].includes(req.socket.remoteAddress || '')) { res.writeHead(403); res.end('local entry requires loopback peer'); return }
     next()
    })
   },
  }],
	root: import.meta.dirname + '/server/client',
	server: {
		port: Number(process.env.JOURNEY_CANVAS_PORT ?? 3737),
		allowedHosts: [hostname(), ...extraHosts],
		proxy: clientApiProxy(API, 'operator'),
	},
	optimizeDeps: { exclude: ['@tldraw/assets'] },
}))
