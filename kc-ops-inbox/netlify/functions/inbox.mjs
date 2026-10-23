import { getStore } from "@netlify/blobs";
import { handle } from "../../core/inbox-core.mjs";

export const makeHandler = (open = getStore, env = process.env) => async (req) =>
  handle(req, { store: open({ name: "ops-inbox", consistency: "strong" }), fetchImpl: fetch, env });

export default makeHandler();

export const config = { path: ["/inbox", "/inbox/health"] };
