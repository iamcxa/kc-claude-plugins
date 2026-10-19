const configured = import.meta.env.VITE_JOURNEY_API_URL || window.location.origin
const base = new URL(configured.replace(/\/$/, '') + '/', window.location.origin)

let humanContext: { member: string; backend: string; signInAt: number; room: string } | null = null
export const setHumanContext = (context: typeof humanContext) => { humanContext = context }
export const journeyApi = (path: string) => {
 const url = new URL(path.replace(/^\//, ''), base)
 if (humanContext && !path.startsWith('/auth/')) {
  url.searchParams.set('_human', humanContext.member)
  url.searchParams.set('_backend', humanContext.backend)
  url.searchParams.set('_humanAt', String(humanContext.signInAt))
  url.searchParams.set('_humanRoom', humanContext.room)
 }
 return url.href
}
