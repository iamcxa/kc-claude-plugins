import { z } from "zod";

/**
 * Source enum for store_insight — valid values are silently coerced to "manual"
 * when missing or invalid. This prevents MCP -32602 errors from agents that
 * send malformed source values (e.g., XML tag drop → empty string).
 */
export const sourceSchema = z
  .enum(["auto", "handoff", "read", "journal", "manual"])
  .catch("manual")
  .default("manual");

export type InsightSource = z.infer<typeof sourceSchema>;
