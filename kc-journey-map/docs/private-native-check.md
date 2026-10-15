# Bounded native-client check on fresh Node

This is a ready recipe for independent validation, not evidence that the current
candidate ran native clients. Use the normal approved Claude Code and Codex CLI
authentication. The helper is loopback-only, runs one phase without automatic
retries, supplies credentials only in the child environment, and enables only
three named MCP tools. A client version that rejects these flags is a tooling
boundary; do not compensate with unrestricted permissions.

Run from `kc-journey-map`. Use a new mode-0700 directory, separate empty private
storage and a finite future expiry chosen for this test. Issue `claude` for A and
`codex` for A,B with `scripts/journey-grant.ts`; token files must remain mode0600.
Start the normal private Node server using `JOURNEY_PRIVATE_DIR`,
`JOURNEY_GRANTS_FILE`, `JOURNEY_ORIGIN=https://localhost` and an unused loopback
`JOURNEY_API_PORT`. The helper never starts, deploys or modifies a provider.
Confirm `/health` initially has no rooms before creating only A/B. Capture the
candidate and client versions in local receipts. No old POC URL or credential is
an acceptable target. The server example in private-host.md owns startup details.

Prepare three prompt files without secrets:

1. `claude-write.txt`: Read A with get_doc; identify its page ID. Use patch_doc
   to add one complete standard note record with ID `shape:claude-private-check`
   and text `Claude private check`, preserving all existing records. Read A back.
   Attempt get_doc B exactly once and report the expected permission denial.
2. `codex-write.txt`: Read A and confirm Claude's note. Add a second complete note
   `shape:codex-private-check`, text `Codex private check`, then read A. Read B;
   add `shape:b-private-check`, text `B isolated check`; read B and confirm no A
   shapes. Stop after at most eight calls.
3. `claude-read.txt`: Read A; report both exact note IDs/texts. No writes.

To avoid asking a model to guess tldraw's complete-record schema, append JSON from
`note()` in `lib/records.mjs` to each write prompt, using the page ID returned by
the fresh room GET. Give each note a distinct x coordinate. This uses the existing
record helper and full-record PATCH contract, not a new operation.

Run sequentially, stopping on the first failure; replace only the local paths and
port. Endpoint and token-file path are ordinary arguments, never token values:

```sh
node scripts/private-native-client.mjs claude http://127.0.0.1:5858 /absolute/private-check/claude.token /absolute/private-check/claude-write.txt /absolute/private-check/claude-write
node scripts/private-native-client.mjs codex http://127.0.0.1:5858 /absolute/private-check/codex.token /absolute/private-check/codex-write.txt /absolute/private-check/codex-write
node scripts/private-native-client.mjs claude http://127.0.0.1:5858 /absolute/private-check/claude.token /absolute/private-check/claude-read.txt /absolute/private-check/claude-read
```

Inspect raw stream receipts for actual tool discovery/calls and independently read
A/B through the existing HTTP API. Verify exact note text and no cross-room shapes;
an agent summary or process exit is insufficient. These are actual native clients
only if the commands run and their MCP calls appear. Generic scripted HTTP/MCP
requests are synthetic clients and must be labelled separately.

Stop the owned server, revoke both disposable IDs through the stopped Node operator
control, verify policy/readback as appropriate, and remove the raw token files.
Retain sanitized receipts locally. Do not copy credentials, provider identities,
raw documents or private evidence paths into public task state.
