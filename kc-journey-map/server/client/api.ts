const configured = import.meta.env.VITE_JOURNEY_API_URL || window.location.origin
const base = new URL(configured.replace(/\/$/, '') + '/', window.location.origin)

export const journeyApi = (path: string) => new URL(path.replace(/^\//, ''), base).href
