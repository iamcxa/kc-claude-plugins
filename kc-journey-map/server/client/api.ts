const configured = import.meta.env.VITE_JOURNEY_API_URL || window.location.origin
const base = new URL(configured.replace(/\/$/, '') + '/', window.location.origin)

export type HumanContext = { member: string; backend: string; signInAt: number; room: string }
let humanContext: HumanContext | null = null
let activity:AbortController|null=null
export const setHumanContext = (context: typeof humanContext) => {
 if(!context){activity?.abort();activity=null}
 else if(!activity || activity.signal.aborted)activity=new AbortController()
 humanContext=context
}
export const journeyFetch:typeof fetch=(input,init={})=>fetch(input,{...init,signal:activity?init.signal?AbortSignal.any([activity.signal,init.signal]):activity.signal:init.signal})
export const journeyApi = (path: string, context = humanContext) => {
 const url = new URL(path.replace(/^\//, ''), base)
 if (context && (!path.startsWith('/auth/') || path.startsWith('/auth/rooms') || path.startsWith('/auth/account'))) {
  url.searchParams.set('_human', context.member)
  url.searchParams.set('_backend', context.backend)
  url.searchParams.set('_humanAt', String(context.signInAt))
  url.searchParams.set('_humanRoom', context.room)
 }
 return url.href
}
