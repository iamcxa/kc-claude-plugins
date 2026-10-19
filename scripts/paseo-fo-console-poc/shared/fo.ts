import type { PaseoApi } from "@getpaseo/client";
import { ROLE_FO, ROLE_LABEL } from "./board";

export const DEFAULT_FO_PROVIDER = "claude/claude-opus-5-5";

export const DEFAULT_FO_PROMPT =
  "You are the first officer (FO) for this repository. Follow its workflow's FO instructions. " +
  "Keep your `task` label current: whenever the task you work on changes, set it with update_agent " +
  "(labels: {task: <short task name>}) on your own agent id.";

export interface NewFoInput {
  workspaceId: string;
  repo: string;
  provider?: string;
  prompt?: string;
}

export async function createFo(
  paseo: PaseoApi,
  input: NewFoInput,
): Promise<string> {
  const agent = await paseo.workspaces.ref(input.workspaceId).agents.create({
    config: { provider: input.provider ?? DEFAULT_FO_PROVIDER },
    prompt: input.prompt ?? DEFAULT_FO_PROMPT,
    labels: { [ROLE_LABEL]: ROLE_FO, repo: input.repo },
  });
  return agent.id;
}
