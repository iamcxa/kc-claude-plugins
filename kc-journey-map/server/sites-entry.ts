export interface SitesJourneyConfig {
	siteOrigin: string
	backendOrigin: string
	pathPrefix: string
	rooms: string[]
}

export function validateSitesJourneyConfig(config: SitesJourneyConfig) {
	for (const origin of [config.siteOrigin, config.backendOrigin]) {
		const url = new URL(origin)
		if (url.protocol !== 'https:' || url.origin !== origin || url.username || url.password) throw new Error('Exact HTTPS origins required')
	}
	if (config.siteOrigin === config.backendOrigin || !/^\/[a-zA-Z0-9_-]+$/.test(config.pathPrefix)) throw new Error('Distinct backend and one route prefix required')
	if (!config.rooms.length || config.rooms.some(room => !/^[a-zA-Z0-9_-]+$/.test(room)) || new Set(config.rooms).size !== config.rooms.length) throw new Error('Unique canonical rooms required')
	return config
}

export function createSitesJourneyEntry(input: SitesJourneyConfig, upstream: typeof fetch = fetch) {
	const config = validateSitesJourneyConfig({ ...input, rooms: [...input.rooms] })
	const prefix = config.pathPrefix + '/api'
	return async (request: Request, env: { JOURNEY_SITES_BEARER?: string }): Promise<Response | null> => {
		const url = new URL(request.url)
		if (url.pathname !== prefix && !url.pathname.startsWith(prefix + '/')) return null
		const fail = (status: number) => new Response('Journey entry unavailable', { status, headers: { 'Cache-Control': 'no-store' } })
		if (url.origin !== config.siteOrigin || !request.headers.get('oai-authenticated-user-id')) return fail(403)
		const origin = request.headers.get('origin')
		const path = url.pathname.slice(prefix.length)
		const socket = path.startsWith('/connect/')
		if ((socket || request.method !== 'GET' || origin) && origin !== config.siteOrigin) return fail(403)
		if (!env.JOURNEY_SITES_BEARER) return fail(503)
		if (socket && request.headers.get('upgrade')?.toLowerCase() !== 'websocket') return fail(426)
		const allowedMethod = request.method === 'GET' || (path === '/save' && request.method === 'POST')
		if (!allowedMethod || (!socket && !['/health', '/doc', '/save', '/repo-doc', '/capabilities'].includes(path))) return fail(404)
		const keys = [...url.searchParams.keys()]
		if (keys.some(key => url.searchParams.getAll(key).length !== 1)) return fail(400)
		const room = socket ? path.slice('/connect/'.length) : url.searchParams.get('room')
		if (path !== '/health' && (!room || !config.rooms.includes(room))) return fail(403)
		const headers = new Headers({ Authorization: 'Bearer ' + env.JOURNEY_SITES_BEARER, Origin: config.siteOrigin })
		if (socket) headers.set('Upgrade', 'websocket')
		if (request.headers.has('content-type')) headers.set('Content-Type', request.headers.get('content-type')!)
		try {
			const response = await upstream(config.backendOrigin + path + url.search, { method: request.method, headers, redirect: 'manual', body: request.method === 'POST' ? await request.arrayBuffer() : undefined })
			if (response.status === 101) return response
			if (response.status >= 300 && response.status < 400) return fail(502)
			if (path === '/health' && response.ok) {
				const inventory = await response.json() as { rooms: string[]; active: { roomId: string }[] }
				return Response.json({ rooms: inventory.rooms.filter(room => config.rooms.includes(room)), active: inventory.active.filter(room => config.rooms.includes(room.roomId)) }, { headers: { 'Cache-Control': 'no-store' } })
			}
			if (path === '/capabilities' && response.ok) return Response.json({ ...await response.json() as object, assets: false }, { headers: { 'Cache-Control': 'no-store' } })
			const outputHeaders = new Headers(response.headers)
			outputHeaders.delete('set-cookie')
			outputHeaders.set('Cache-Control', 'no-store')
			return new Response(response.body, { status: response.status, headers: outputHeaders })
		} catch { return fail(502) }
	}
}
