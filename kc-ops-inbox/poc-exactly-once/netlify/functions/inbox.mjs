import { getStore } from "@netlify/blobs";
import { handle } from "../../inbox-core.mjs";

export default async (req) =>
  handle(req, {
    store: getStore({ name: "ops-inbox-dedupe", consistency: "strong" }),
    fetchImpl: fetch,
    env: process.env,
  });

export const config = { path: "/inbox" };
