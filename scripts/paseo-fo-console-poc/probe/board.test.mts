import assert from "node:assert/strict";
import { test } from "node:test";
import { type BoardAgent, boardStatus, toRows } from "../shared/board";

const base: BoardAgent = {
  id: "a",
  cwd: "/x",
  status: "idle",
  updatedAt: "2026-10-19T11:00:00.000Z",
  labels: { role: "fo", repo: "r" },
};

test("a pending permission is waiting on Kent even when requiresAttention is false", () => {
  const agent = {
    ...base,
    status: "running",
    requiresAttention: false,
    attentionReason: null,
    pendingPermissions: [{}],
  };
  assert.equal(boardStatus(agent), "waiting on Kent");
});

test("Paseo's own permission attention is waiting on Kent", () => {
  assert.equal(
    boardStatus({
      ...base,
      requiresAttention: true,
      attentionReason: "permission",
    }),
    "waiting on Kent",
  );
});

test("running without a prompt is busy, a finished idle agent is idle", () => {
  assert.equal(boardStatus({ ...base, status: "running" }), "busy");
  assert.equal(
    boardStatus({
      ...base,
      requiresAttention: true,
      attentionReason: "finished",
    }),
    "idle",
  );
});

test("only role=fo agents are rows, newest activity first", () => {
  const rows = toRows([
    { ...base, id: "old", updatedAt: "2026-10-19T10:00:00.000Z" },
    { ...base, id: "new", updatedAt: "2026-10-19T12:00:00.000Z" },
    { ...base, id: "coord", labels: { role: "coordinator" } },
    { ...base, id: "none", labels: undefined },
  ]);
  assert.deepEqual(
    rows.map((r) => r.id),
    ["new", "old"],
  );
});
