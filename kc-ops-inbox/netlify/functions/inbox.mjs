import { getStore } from "@netlify/blobs";
import { handle } from "../../core/inbox-core.mjs";
import { configReport } from "../../core/inbox-config.mjs";

// A configuration fault is logged once at load; every event is then refused with 500 and /inbox/health names the fault.
export const makeHandler = (open = getStore, env = process.env) => {
  const report = configReport(env);
  if (!report.ok) console.error(JSON.stringify({ evt: "misconfigured", report }));
  return async (req) => handle(req, { store: open({ name: "ops-inbox", consistency: "strong" }), fetchImpl: fetch, env });
};

export default makeHandler();

export const config = { path: ["/inbox", "/inbox/health"] };
