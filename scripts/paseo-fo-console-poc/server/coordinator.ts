import { mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { PaseoApi } from "@getpaseo/client";
import { ROLE_COORDINATOR, ROLE_LABEL } from "../shared/board";
import {
  COORDINATOR_OPTIONS,
  COORDINATOR_PROMPT,
  COORDINATOR_PROVIDER,
} from "../shared/coordinator";

let inFlight: Promise<{ agentId: string; created: boolean }> | null = null;

export interface CoordinatorOptions {
  provider?: string;
  role?: string;
}

export function ensureCoordinator(
  paseo: PaseoApi,
  options: CoordinatorOptions = {},
): Promise<{ agentId: string; created: boolean }> {
  inFlight ??= open(
    paseo,
    options.provider ?? COORDINATOR_PROVIDER,
    options.role ?? ROLE_COORDINATOR,
  ).finally(() => {
    inFlight = null;
  });
  return inFlight;
}

async function open(paseo: PaseoApi, provider: string, role: string) {
  const { entries } = await paseo.agents.list({
    filter: { labels: { [ROLE_LABEL]: role } },
  });
  const existing = entries[0]?.agent;
  if (existing) return { agentId: existing.id, created: false };

  const cwd = join(tmpdir(), "paseo-fo-coordinator");
  await mkdir(cwd, { recursive: true });
  const agent = await paseo.agents.create({
    config: {
      provider,
      systemPrompt: COORDINATOR_PROMPT,
      options: COORDINATOR_OPTIONS,
    },
    cwd,
    title: "FO coordinator",
    labels: { [ROLE_LABEL]: role },
  });
  return { agentId: agent.id, created: true };
}
