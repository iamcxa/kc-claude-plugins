import { createServer, type IncomingMessage, type Server } from "node:http";

export interface ToolResult {
  text: string;
  isError?: boolean;
}

export interface ToolDefinition {
  name: string;
  description: string;
  properties: Record<string, { type: "string"; description: string }>;
  call(slot: string, args: Record<string, unknown>): Promise<ToolResult>;
}

const PROTOCOL_FALLBACK = "2025-03-26";

async function readJson(req: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(chunk as Buffer);
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startMcpServer(tools: ToolDefinition[]): Promise<{ server: Server; port: number }> {
  const byName = new Map(tools.map((tool) => [tool.name, tool]));
  const server = createServer(async (req, res) => {
    const slot = /^\/mcp\/([0-9a-f]{32})$/.exec(req.url ?? "")?.[1];
    if (!slot) {
      res.writeHead(404).end();
      return;
    }
    if (req.method === "DELETE") {
      res.writeHead(200).end();
      return;
    }
    if (req.method !== "POST") {
      res.writeHead(405, { Allow: "POST, DELETE" }).end();
      return;
    }
    let message: { id?: string | number; method?: string; params?: Record<string, unknown> };
    try {
      message = (await readJson(req)) as typeof message;
    } catch {
      res.writeHead(400).end();
      return;
    }
    if (message.id === undefined) {
      res.writeHead(202).end();
      return;
    }
    const reply = (result: unknown) => {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ jsonrpc: "2.0", id: message.id, result }));
    };
    const fail = (code: number, text: string) => {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ jsonrpc: "2.0", id: message.id, error: { code, message: text } }));
    };
    switch (message.method) {
      case "initialize":
        reply({
          protocolVersion: (message.params?.protocolVersion as string) ?? PROTOCOL_FALLBACK,
          capabilities: { tools: {} },
          serverInfo: { name: "peer", version: "0.0.0" },
        });
        return;
      case "ping":
        reply({});
        return;
      case "tools/list":
        reply({
          tools: tools.map((tool) => ({
            name: tool.name,
            description: tool.description,
            inputSchema: {
              type: "object",
              properties: tool.properties,
              required: Object.keys(tool.properties),
            },
          })),
        });
        return;
      case "tools/call": {
        const tool = byName.get(message.params?.name as string);
        if (!tool) {
          fail(-32602, "unknown tool");
          return;
        }
        try {
          const result = await tool.call(slot, (message.params?.arguments ?? {}) as Record<string, unknown>);
          reply({ content: [{ type: "text", text: result.text }], isError: result.isError === true });
        } catch (error) {
          reply({ content: [{ type: "text", text: `error: ${String(error)}` }], isError: true });
        }
        return;
      }
      default:
        fail(-32601, "method not found");
    }
  });
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      resolve({ server, port: typeof address === "object" && address ? address.port : 0 });
    });
  });
}
