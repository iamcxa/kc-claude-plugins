import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The front-end a shared viewer reaches: the board and its images, and nothing else.
const API = `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`

export default defineConfig(() => ({
	plugins: [react()],
	root: import.meta.dirname + '/server/client',
	server: {
		port: Number(process.env.JOURNEY_SHARE_PORT ?? 3738),
		strictPort: true,
		host: '127.0.0.1',
		allowedHosts: true,
		proxy: {
			'/connect/': { target: API, ws: true, changeOrigin: true },
			'/uploads/': { target: API, changeOrigin: true },
		},
	},
	optimizeDeps: { exclude: ['@tldraw/assets'] },
}))
