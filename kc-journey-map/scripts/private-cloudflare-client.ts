export default {
 fetch(req: Request, env: any) {
  if (req.method !== 'POST' || new URL(req.url).pathname !== '/') return new Response(null, { status: 404 })
  if (req.headers.has('origin')) return new Response('browser requests forbidden', { status: 403 })
  if (req.headers.get('content-type')?.split(';', 1)[0].trim().toLowerCase() !== 'application/json')
   return new Response('JSON required', { status: 415 })
  return env.OPERATOR.fetch(req)
 },
}
