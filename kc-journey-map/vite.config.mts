import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig(() => ({
	plugins: [react()],
	root: import.meta.dirname + '/server/client',
	server: { port: 3737 },
	optimizeDeps: { exclude: ['@tldraw/assets'] },
}))
