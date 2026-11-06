import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { clientApiProxy } from './server/client-api-proxy.ts'

const API = `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

export default defineConfig(() => ({
	plugins: [react()],
	root: import.meta.dirname + '/server/client',
	server: {
		port: Number(process.env.JOURNEY_SHARE_PORT ?? 3738),
		strictPort: true,
		host: '127.0.0.1',
		allowedHosts: true,
		proxy: clientApiProxy(API, 'share'),
	},
	optimizeDeps: { exclude: ['@tldraw/assets'] },
}))
