import { describe, it, expect, beforeEach, mock } from 'bun:test'
import type { Message, Tool } from '@anthropic-ai/sdk/resources/messages'

// ============================================================
// Mocks — must precede chat-manager import
// ============================================================

// Mock Anthropic SDK
let mockMessagesCreateCallCount = 0
let mockMessagesCreateResponses: Partial<Message>[] = []

const mockMessagesCreate = mock(async (_params: unknown): Promise<Partial<Message>> => {
  const response = mockMessagesCreateResponses[mockMessagesCreateCallCount] ?? {
    id: 'msg-end',
    type: 'message',
    role: 'assistant',
    content: [{ type: 'text', text: 'No more responses configured' }],
    stop_reason: 'end_turn',
    model: 'claude-haiku-4-5',
    usage: { input_tokens: 10, output_tokens: 10 },
  }
  mockMessagesCreateCallCount++
  return response
})

// Mock MCP client
let mockMcpClientCallToolCalls: Array<{ name: string; arguments: unknown }> = []
const mockMcpCallTool = mock(async (params: { name: string; arguments: unknown }) => {
  mockMcpClientCallToolCalls.push(params)
  return { content: [{ type: 'text', text: JSON.stringify({ result: 'mock_result_for_' + params.name }) }] }
})

let mockMcpClientConnected = false
const mockMcpClose = mock(async () => {
  mockMcpClientConnected = false
})
const mockMcpConnect = mock(async () => {
  mockMcpClientConnected = true
})

// Track created MCP client instances
let mockMcpClientInstance: { callTool: typeof mockMcpCallTool; close: typeof mockMcpClose; connect: typeof mockMcpConnect } | null = null

mock.module('@anthropic-ai/sdk', () => ({
  default: class MockAnthropic {
    messages = { create: mockMessagesCreate }
  },
}))

mock.module('@modelcontextprotocol/sdk/client/index.js', () => ({
  Client: class MockClient {
    callTool = mockMcpCallTool
    close = mockMcpClose
    connect = mockMcpConnect
    constructor() {
      mockMcpClientInstance = this as typeof mockMcpClientInstance
    }
  },
}))

mock.module('@modelcontextprotocol/sdk/client/streamableHttp.js', () => ({
  StreamableHTTPClientTransport: class MockTransport {
    constructor(_url: URL, _opts?: unknown) {}
  },
}))

mock.module('../../server/services/yaml-store.ts', () => ({
  loadOrCreateAppConfig: mock(async () => ({
    host: '127.0.0.1',
    port: 3200,
    schedule: { enabled: false, self_repair_before: true },
    max_concurrent_runs: 1,
    plugins_dir: '/tmp/plugins',
  })),
}))

// ============================================================
// Import after mocks
// ============================================================
const {
  getOrCreateSession,
  killSession,
  killAllSessions,
  NW_TOOLS,
} = await import('../../server/services/chat-manager.ts')

// ============================================================
// Helper: reset state between tests
// ============================================================
function resetMocks() {
  // killAllSessions BEFORE clearing mock counts — prevents leftover close() calls bleeding into next test
  killAllSessions()
  mockMessagesCreateCallCount = 0
  mockMessagesCreateResponses = []
  mockMcpClientCallToolCalls = []
  mockMcpClientInstance = null
  mockMcpClientConnected = false
  mockMessagesCreate.mockClear()
  mockMcpCallTool.mockClear()
  mockMcpClose.mockClear()
  mockMcpConnect.mockClear()
}

// ============================================================
// NW_TOOLS array tests
// ============================================================
describe('NW_TOOLS', () => {
  it('NW_TOOLS is exported and is an array', () => {
    expect(Array.isArray(NW_TOOLS)).toBe(true)
  })

  it('NW_TOOLS has 15 entries (7 query + 1 search + 4 action + 3 outcome)', () => {
    expect(NW_TOOLS.length).toBe(15)
  })

  it('each tool has name, description, and input_schema', () => {
    for (const tool of NW_TOOLS as Tool[]) {
      expect(typeof tool.name).toBe('string')
      expect(typeof tool.description).toBe('string')
      expect(typeof tool.input_schema).toBe('object')
      expect(tool.input_schema.type).toBe('object')
    }
  })

  it('each tool name starts with nw_', () => {
    for (const tool of NW_TOOLS as Tool[]) {
      expect(tool.name.startsWith('nw_')).toBe(true)
    }
  })

  it('contains all required tool names', () => {
    const names = (NW_TOOLS as Tool[]).map((t) => t.name)
    // 7 query tools
    expect(names).toContain('nw_get_targets')
    expect(names).toContain('nw_get_latest_run')
    expect(names).toContain('nw_get_run')
    expect(names).toContain('nw_get_proposals')
    expect(names).toContain('nw_get_config_warnings')
    expect(names).toContain('nw_get_schedule')
    expect(names).toContain('nw_read_journal')
    // 1 search
    expect(names).toContain('nw_search_journal')
    // 4 action
    expect(names).toContain('nw_trigger_run')
    expect(names).toContain('nw_submit_feedback')
    expect(names).toContain('nw_update_schedule')
    expect(names).toContain('nw_implement_proposal')
    // 3 outcome (Phase 10)
    expect(names).toContain('nw_get_outcomes')
    expect(names).toContain('nw_get_outcome_status')
    expect(names).toContain('nw_outcome_summary')
  })
})

// ============================================================
// sendMessage passes tools to Anthropic API
// ============================================================
describe('sendMessage — tool_use routing', () => {
  beforeEach(resetMocks)

  it('passes NW_TOOLS to messages.create', async () => {
    const { sendMessage } = await import('../../server/services/chat-manager.ts')
    mockMessagesCreateResponses = [
      {
        id: 'msg-end',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'text', text: 'Hello!' }],
        stop_reason: 'end_turn',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 10, output_tokens: 10 },
      } as Message,
    ]

    await sendMessage('test-target', 'hello')

    expect(mockMessagesCreate.mock.calls.length).toBeGreaterThan(0)
    const callArgs = mockMessagesCreate.mock.calls[0]![0] as { tools: Tool[] }
    expect(callArgs.tools).toBeDefined()
    expect(Array.isArray(callArgs.tools)).toBe(true)
    expect(callArgs.tools.length).toBe(15)
  })

  it('routes tool_use block to MCP client and appends tool_result', async () => {
    const { sendMessage } = await import('../../server/services/chat-manager.ts')

    // First response: tool_use block
    mockMessagesCreateResponses = [
      {
        id: 'msg-1',
        type: 'message',
        role: 'assistant',
        content: [
          {
            type: 'tool_use',
            id: 'toolu_1',
            name: 'nw_get_targets',
            input: {},
          },
        ],
        stop_reason: 'tool_use',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 10, output_tokens: 10 },
      } as unknown as Message,
      // Second response: end_turn
      {
        id: 'msg-2',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'text', text: 'Here are the targets.' }],
        stop_reason: 'end_turn',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 20, output_tokens: 20 },
      } as Message,
    ]

    await sendMessage('test-target', 'list targets')

    // MCP client should have been called once
    expect(mockMcpCallTool.mock.calls.length).toBe(1)
    expect(mockMcpCallTool.mock.calls[0]![0]).toMatchObject({
      name: 'nw_get_targets',
    })

    // messages.create should have been called twice (1st for tool_use, 2nd after tool_result)
    expect(mockMessagesCreate.mock.calls.length).toBe(2)

    // Second call should include tool_result message
    const secondCallMessages = (mockMessagesCreate.mock.calls[1]![0] as { messages: Array<{ role: string; content: unknown }> }).messages
    const toolResultMsg = secondCallMessages.find((m) => m.role === 'user' && Array.isArray(m.content))
    expect(toolResultMsg).toBeDefined()
  })

  it('tool_use loop continues until stop_reason !== tool_use', async () => {
    const { sendMessage } = await import('../../server/services/chat-manager.ts')

    // 3 rounds of tool_use, then end_turn
    mockMessagesCreateResponses = [
      {
        id: 'msg-1',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'tool_use', id: 'toolu_1', name: 'nw_get_targets', input: {} }],
        stop_reason: 'tool_use',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 10, output_tokens: 10 },
      } as unknown as Message,
      {
        id: 'msg-2',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'tool_use', id: 'toolu_2', name: 'nw_get_schedule', input: {} }],
        stop_reason: 'tool_use',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 15, output_tokens: 15 },
      } as unknown as Message,
      {
        id: 'msg-3',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'text', text: 'Done with tools.' }],
        stop_reason: 'end_turn',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 20, output_tokens: 20 },
      } as Message,
    ]

    await sendMessage('test-target', 'multi-tool query')

    // 2 tool calls made
    expect(mockMcpCallTool.mock.calls.length).toBe(2)
    // 3 messages.create calls (3 rounds)
    expect(mockMessagesCreate.mock.calls.length).toBe(3)
  })

  it('stops after MAX_TOOL_ROUNDS (10) to prevent infinite loop', async () => {
    const { sendMessage } = await import('../../server/services/chat-manager.ts')

    // Always return tool_use (never terminates naturally)
    mockMessagesCreateResponses = Array(15).fill({
      id: 'msg-loop',
      type: 'message',
      role: 'assistant',
      content: [{ type: 'tool_use', id: 'toolu_loop', name: 'nw_get_targets', input: {} }],
      stop_reason: 'tool_use',
      model: 'claude-haiku-4-5',
      usage: { input_tokens: 10, output_tokens: 10 },
    } as unknown as Message)

    await sendMessage('test-target', 'infinite loop test')

    // Should have stopped at MAX_TOOL_ROUNDS (10)
    expect(mockMessagesCreate.mock.calls.length).toBeLessThanOrEqual(10)
  })

  it('MCP client is lazy-initialized per session (not per message)', async () => {
    const { sendMessage } = await import('../../server/services/chat-manager.ts')

    // Configure 2 tool_use responses then end_turn
    mockMessagesCreateResponses = [
      {
        id: 'msg-1',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'tool_use', id: 'toolu_1', name: 'nw_get_targets', input: {} }],
        stop_reason: 'tool_use',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 10, output_tokens: 10 },
      } as unknown as Message,
      {
        id: 'msg-2',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'text', text: 'First message done.' }],
        stop_reason: 'end_turn',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 15, output_tokens: 15 },
      } as Message,
      // Second sendMessage call
      {
        id: 'msg-3',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'tool_use', id: 'toolu_2', name: 'nw_get_schedule', input: {} }],
        stop_reason: 'tool_use',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 10, output_tokens: 10 },
      } as unknown as Message,
      {
        id: 'msg-4',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'text', text: 'Second message done.' }],
        stop_reason: 'end_turn',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 15, output_tokens: 15 },
      } as Message,
    ]

    await sendMessage('lazy-client-target', 'first message')
    await sendMessage('lazy-client-target', 'second message')

    // Client.connect should only be called ONCE (lazy init, reused for session)
    expect(mockMcpConnect.mock.calls.length).toBe(1)
  })
})

// ============================================================
// killSession closes MCP client
// ============================================================
describe('killSession — MCP client cleanup', () => {
  beforeEach(resetMocks)

  it('killSession closes MCP client if present', async () => {
    const { sendMessage } = await import('../../server/services/chat-manager.ts')

    // Trigger MCP client creation via tool_use
    mockMessagesCreateResponses = [
      {
        id: 'msg-1',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'tool_use', id: 'toolu_1', name: 'nw_get_targets', input: {} }],
        stop_reason: 'tool_use',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 10, output_tokens: 10 },
      } as unknown as Message,
      {
        id: 'msg-2',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'text', text: 'Done.' }],
        stop_reason: 'end_turn',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 15, output_tokens: 15 },
      } as Message,
    ]

    await sendMessage('cleanup-target', 'trigger mcp client creation')

    // MCP client should have been created
    expect(mockMcpConnect.mock.calls.length).toBe(1)

    // Now kill the session — should close the MCP client
    killSession('cleanup-target')

    // MCP close should have been called
    expect(mockMcpClose.mock.calls.length).toBe(1)
  })

  it('killSession with no MCP client does not throw', () => {
    getOrCreateSession('no-client-target')
    expect(() => killSession('no-client-target')).not.toThrow()
  })
})

// ============================================================
// Streaming text deltas
// ============================================================
describe('sendMessage — streaming text deltas', () => {
  beforeEach(resetMocks)

  it('streams text deltas to subscribers between tool calls', async () => {
    const { sendMessage, subscribeToTarget } = await import('../../server/services/chat-manager.ts')
    const events: Array<{ data: string; event?: string }> = []
    const writer = { writeSSE: async (d: { data: string; event?: string }) => { events.push(d) } }
    const ac = new AbortController()
    subscribeToTarget('stream-target', writer, ac.signal)

    mockMessagesCreateResponses = [
      {
        id: 'msg-1',
        type: 'message',
        role: 'assistant',
        content: [
          { type: 'text', text: 'Checking...' },
          { type: 'tool_use', id: 'toolu_1', name: 'nw_get_targets', input: {} },
        ],
        stop_reason: 'tool_use',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 10, output_tokens: 10 },
      } as unknown as Message,
      {
        id: 'msg-2',
        type: 'message',
        role: 'assistant',
        content: [{ type: 'text', text: 'Here are the targets.' }],
        stop_reason: 'end_turn',
        model: 'claude-haiku-4-5',
        usage: { input_tokens: 20, output_tokens: 20 },
      } as Message,
    ]

    await sendMessage('stream-target', 'list targets')
    ac.abort()

    const parsedEvents = events.map((e) => JSON.parse(e.data))
    // Should have start event
    const startEvents = parsedEvents.filter((e) => e.type === 'start')
    expect(startEvents.length).toBe(1)
    // Should have delta events for text content
    const deltaEvents = parsedEvents.filter((e) => e.type === 'delta')
    expect(deltaEvents.length).toBeGreaterThan(0)
    // Should have end event
    const endEvents = parsedEvents.filter((e) => e.type === 'end')
    expect(endEvents.length).toBe(1)
  })
})
