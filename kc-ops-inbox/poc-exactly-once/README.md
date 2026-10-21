# Inbox exactly-once delivery POC

Disposable proof, not a package. Local rig: `npm install && npm test`
(`RIG_REAL_WAIT=1` adds a real 61.5 s gap before the third send).

Platform boundary: `inbox-core.mjs` (signature verify, dedupe, dispatch, Slack) takes a Web
`Request`, a store `{ set, delete }`, `fetch` and an env map, and imports nothing from Netlify;
the test rig drives it with an in-memory store. Netlify-specific code is only
`netlify/functions/inbox.mjs` (11 lines: `getStore`, the `config.path` route),
`netlify.toml` (6 lines) and the `@netlify/blobs` entry in `package.json`.

Send: `WEBHOOK_SECRET=... node send.mjs https://<site>/inbox <event-id> [tamper]`.
