import { createPaseoClient } from "@getpaseo/client";
import { observeBoard, toRows, type BoardAgent } from "../shared/board";
import { createFo } from "../shared/fo";
import { ensureCoordinator } from "../server/coordinator";
import { COORDINATOR_OPTIONS } from "../shared/coordinator";
import { mkdirSync } from "node:fs";

const [command, ...args] = process.argv.slice(2);
const client = createPaseoClient({
  url: process.env.PASEO_URL ?? "ws://127.0.0.1:6767/ws",
});
await client.connect();

async function listed(labels?: Record<string, string>): Promise<BoardAgent[]> {
  const { entries } = await client.agents.list(
    labels ? { filter: { labels } } : {},
  );
  return entries.map(({ agent }) => agent as BoardAgent);
}

const short = (id: string) => id.slice(0, 7);

switch (command) {
  case "board": {
    const only = new Set(args);
    const agents = await listed({ role: "fo" });
    const rows = toRows(agents).filter(
      (r) => only.size === 0 || only.has(short(r.id)),
    );
    console.log(
      JSON.stringify(
        rows.map((r) => ({ ...r, id: short(r.id) })),
        null,
        1,
      ),
    );
    break;
  }
  case "raw": {
    const only = new Set(args);
    const agents = (await listed()).filter((a) => only.has(short(a.id)));
    console.log(
      JSON.stringify(
        agents.map((a) => ({
          id: short(a.id),
          status: a.status,
          pendingPermissions: a.pendingPermissions?.length ?? 0,
          requiresAttention: a.requiresAttention,
          attentionReason: a.attentionReason,
          labels: a.labels,
          updatedAt: a.updatedAt,
        })),
        null,
        1,
      ),
    );
    break;
  }
  case "observe": {
    const seconds = Number(args[0] ?? "60");
    const only = new Set(args.slice(1));
    let last = "";
    const stop = await observeBoard(client, (rows) => {
      const view = JSON.stringify(
        rows
          .filter((r) => only.size === 0 || only.has(short(r.id)))
          .map((r) => `${short(r.id)} ${r.repo}|${r.task}|${r.status}`),
      );
      if (view !== last) console.log(new Date().toISOString(), view);
      last = view;
    });
    await new Promise((resolve) => setTimeout(resolve, seconds * 1000));
    stop();
    break;
  }
  case "new-fo": {
    const [workspaceId, repo, provider, prompt] = args;
    console.log(
      await createFo(client, { workspaceId, repo, provider, prompt }),
    );
    break;
  }
  case "open-coordinator": {
    const options = { provider: args[0], role: args[1] };
    const results = await Promise.all(
      Array.from({ length: Number(args[2] ?? "1") }, () =>
        ensureCoordinator(client, options),
      ),
    );
    console.log(
      JSON.stringify(results.map((r) => ({ ...r, agentId: short(r.agentId) }))),
    );
    break;
  }
  case "workspaces": {
    const { entries } = await client.workspaces.list();
    console.log(
      JSON.stringify(
        entries.map((w) => ({
          id: w.id,
          repo: w.projectDisplayName,
          name: w.name,
          dir: w.workspaceDirectory,
        })),
      ),
    );
    break;
  }
  case "ask-agent": {
    const [workspaceId, title, prompt] = args;
    const agent = await client.workspaces.ref(workspaceId).agents.create({
      config: {
        provider: "claude/claude-haiku-5-5",
        modeId: "default",
        options: { settings: { permissions: { ask: ["Bash"] } } },
      },
      title,
      prompt,
    });
    console.log(agent.id);
    break;
  }
  case "mechanism-agent": {
    const [variant, prompt] = args;
    mkdirSync("/tmp/paseo-fo-poc/mechanism", { recursive: true });
    const agent = await client.agents.create({
      config: {
        provider: "claude/claude-haiku-5-5",
        systemPrompt:
          "You are a test agent. When asked to answer a permission prompt, do it with the respond_to_permission tool and report the exact tool result or error.",
        options:
          variant === "restricted"
            ? COORDINATOR_OPTIONS
            : { allowedTools: COORDINATOR_OPTIONS.allowedTools },
      },
      cwd: "/tmp/paseo-fo-poc/mechanism",
      title: `poc-mechanism-${variant}`,
      prompt,
    });
    console.log(agent.id);
    break;
  }
  case "variant-agent": {
    const [optionsJson, prompt] = args;
    mkdirSync("/tmp/paseo-fo-poc/mechanism", { recursive: true });
    const agent = await client.agents.create({
      config: {
        provider: "claude/claude-haiku-5-5",
        systemPrompt:
          "You are a test agent. When asked to answer a permission prompt, do it with the respond_to_permission tool and report the exact tool result or error.",
        options: JSON.parse(optionsJson),
      },
      cwd: "/tmp/paseo-fo-poc/mechanism",
      title: "poc-mechanism-variant",
      prompt,
    });
    console.log(agent.id);
    break;
  }
  case "send": {
    const [agentId, text] = args;
    await client.agents.ref(agentId).send(text);
    console.log("sent");
    break;
  }
  case "ids": {
    const agents = await listed();
    console.log(
      JSON.stringify(
        agents.map((a) => `${short(a.id)}:${a.labels?.role ?? "-"}`).sort(),
      ),
    );
    break;
  }
  case "workspace-open": {
    const workspace = await client.workspaces.open(args[0]);
    console.log(JSON.stringify({ id: workspace.id, name: workspace.name }));
    break;
  }
  case "workspace-archive": {
    console.log(JSON.stringify(await client.workspaces.archive(args[0])));
    break;
  }
  default:
    console.error(
      "usage: board|raw|observe|new-fo|open-coordinator|workspaces|workspace-open|workspace-archive",
    );
    process.exitCode = 2;
}
await client.close();
