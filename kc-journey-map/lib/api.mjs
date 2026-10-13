export async function apiFetch(url, options = {}) {
 const headers = new Headers(options.headers)
 if (process.env.JOURNEY_API_TOKEN) headers.set('Authorization', 'Bearer ' + process.env.JOURNEY_API_TOKEN)
 const response = await fetch(url, { ...options, headers })
 if (response.status === 401 || response.status === 403) throw new Error(`journey API credential/room denied (HTTP ${response.status})`)
 if (!response.ok) throw new Error(`journey API failed (HTTP ${response.status}): ${await response.text()}`)
 return response
}
