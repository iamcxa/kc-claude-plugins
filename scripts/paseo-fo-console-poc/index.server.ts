import type { PluginServerContext } from "@getpaseo/plugin/server";
import { ensureCoordinator } from "./server/coordinator";
import {
  COORDINATOR_PROMPT,
  RESPONDER_TOOL,
  openCoordinator,
} from "./shared/coordinator";

export default function contribute(server: PluginServerContext) {
  server.handle(openCoordinator, (_input, { paseo }) =>
    ensureCoordinator(paseo),
  );

  // create_agent copies a same-provider caller's providerOptions onto the agent it starts;
  // without this the FOs a coordinator starts would carry its tool restrictions.
  server.before("agent.create", ({ request }) => {
    const options = request.config.providerOptions ?? {};
    const inherited =
      request.config.systemPrompt !== COORDINATOR_PROMPT &&
      JSON.stringify(options.settings ?? null).includes(RESPONDER_TOOL);
    if (!inherited) return undefined;
    const { allowedTools: _allowed, settings: _settings, ...rest } = options;
    return { ...request, config: { ...request.config, providerOptions: rest } };
  });

  return () => {};
}
