import { hostname } from 'node:os'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The machine's own hostname is always admitted; JOURNEY_ALLOWED_HOSTS adds a
// comma-separated list (e.g. a cloud or Tailscale DNS name) without editing this file.
const extraHosts = (process.env.JOURNEY_ALLOWED_HOSTS ?? '')
	.split(',')
	.map((h) => h.trim())
	.filter(Boolean)

const API = `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

export default defineConfig(() => ({
	plugins: [react()],
	root: import.meta.dirname + '/server/client',
	server: {
		port: Number(process.env.JOURNEY_CANVAS_PORT ?? 3737),
		allowedHosts: [hostname(), ...extraHosts],
		proxy: {
			'/connect': { target: API, ws: true },
			'/uploads/': { target: API },
			'/repo-doc': { target: API },
			'/save': { target: API },
		},
	},
	optimizeDeps: { exclude: ['@tldraw/assets'] },
}))
