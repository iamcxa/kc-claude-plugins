import { getStore } from "@netlify/blobs";
import { handle } from "../../core/inbox-core.mjs";

export default async (req) =>
  handle(req, {
    store: getStore({ name: "ops-inbox", consistency: "strong" }),
    fetchImpl: fetch,
    env: process.env,
  });

export const config = { path: ["/inbox", "/inbox/health"] };
