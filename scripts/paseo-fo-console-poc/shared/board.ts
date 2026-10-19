import type { PaseoApi } from "@getpaseo/client";

export const ROLE_LABEL = "role";
export const ROLE_FO = "fo";
export const ROLE_COORDINATOR = "coordinator";

export type BoardStatus = "busy" | "idle" | "waiting on Kent" | "error";

export interface BoardAgent {
  id: string;
  title?: string | null;
  cwd: string;
  status: string;
  labels?: Record<string, string>;
  requiresAttention?: boolean;
  attentionReason?: string | null;
  pendingPermissions?: readonly unknown[];
  updatedAt: string;
}

export interface BoardRow {
  id: string;
  title: string;
  repo: string;
  task: string;
  status: BoardStatus;
  lastActivityAt: string;
}

export function boardStatus(agent: BoardAgent): BoardStatus {
  if (agent.pendingPermissions?.length) return "waiting on Kent";
  if (agent.requiresAttention && agent.attentionReason === "permission")
    return "waiting on Kent";
  if (agent.status === "error" || agent.attentionReason === "error")
    return "error";
  if (agent.status === "running" || agent.status === "initializing")
    return "busy";
  return "idle";
}

export function isFo(agent: BoardAgent): boolean {
  return agent.labels?.[ROLE_LABEL] === ROLE_FO;
}

export function toRow(agent: BoardAgent): BoardRow {
  return {
    id: agent.id,
    title: agent.title ?? "",
    repo: agent.labels?.repo ?? "",
    task: agent.labels?.task ?? "",
    status: boardStatus(agent),
    lastActivityAt: agent.updatedAt,
  };
}

export function toRows(agents: Iterable<BoardAgent>): BoardRow[] {
  return [...agents]
    .filter(isFo)
    .map(toRow)
    .sort((a, b) => b.lastActivityAt.localeCompare(a.lastActivityAt));
}

export async function observeBoard(
  paseo: PaseoApi,
  onRows: (rows: BoardRow[]) => void,
): Promise<() => void> {
  const known = new Map<string, BoardAgent>();
  const emit = () => onRows(toRows(known.values()));
  const { subscription } = await paseo.agents.list({ subscribe: {} });
  subscription.subscribe({
    snapshot: ({ entries }) => {
      known.clear();
      for (const { agent } of entries) known.set(agent.id, agent as BoardAgent);
      emit();
    },
    update: (message) => {
      if (message.type !== "agent_update") return;
      const update = message.payload;
      if (update.kind === "upsert")
        known.set(update.agent.id, update.agent as BoardAgent);
      else known.delete(update.agentId);
      emit();
    },
  });
  return () => subscription.release();
}
