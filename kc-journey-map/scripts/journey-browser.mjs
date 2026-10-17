import { chromium } from 'playwright'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
export async function browserSession(context, origin, credential) {
 const response = await context.request.post(origin + '/session', { headers: { Authorization: 'Bearer ' + credential, Origin: origin } })
 if (!response.ok()) throw new Error('browser session denied: HTTP ' + response.status())
 return response.json()
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
 const [origin, room = 'default'] = process.argv.slice(2)
 if (!origin || !process.env.JOURNEY_API_TOKEN) throw new Error('usage: JOURNEY_API_TOKEN=<credential> node scripts/journey-browser.mjs <HTTPS origin> [room]')
 const browser = await chromium.launch({ headless: false })
 try {
  const context = await browser.newContext()
  await browserSession(context, origin, process.env.JOURNEY_API_TOKEN)
  const page = await context.newPage()
  await page.goto(origin + '/?room=' + encodeURIComponent(room))
  await new Promise(resolve => page.once('close', resolve))
 } finally { await browser.close() }
}
