export default {
 fetch(req: Request, env: any) {
  if (req.method !== 'POST' || new URL(req.url).pathname !== '/') return new Response(null, { status: 404 })
  return env.OPERATOR.fetch(req)
 },
}
