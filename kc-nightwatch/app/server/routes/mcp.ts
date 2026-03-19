import { Hono } from 'hono'
import { WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js'
import { createMcpServer } from '../services/mcp-tools.ts'

export const mcpRoutes = new Hono()

// Stateless: new transport + server per request (no session tracking)
// Handles both POST (JSON-RPC requests) and GET (SSE stream) on the same path
mcpRoutes.all('/mcp', async (c) => {
  const transport = new WebStandardStreamableHTTPServerTransport()
  const server = createMcpServer()
  await server.connect(transport)
  return transport.handleRequest(c.req.raw)
})
