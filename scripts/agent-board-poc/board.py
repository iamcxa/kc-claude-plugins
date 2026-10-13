#!/usr/bin/env python3
"""One-thread message board backed by a SQLite file (stdlib only).

serve  MCP server over stdio: post_message, read_messages, wait_for_messages
log    print every message with id, time, sender, harness and text
post   append a message from the command line
wait   block until another sender has posted since this reader's cursor
"""
import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL,
  sender TEXT NOT NULL, harness TEXT NOT NULL, text TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cursors(reader TEXT PRIMARY KEY, last_id INTEGER NOT NULL);
"""
MAX_WAIT_S = 25
REPLY_HINT = ("New message on the agent board, addressed to you. Answer it by calling the board "
              "MCP server's post_message tool (not by replying in text):\n")
POLL_S = 0.2


def connect():
    path = os.environ.get("AGENT_BOARD_DB")
    if not path:
        sys.exit("AGENT_BOARD_DB is not set")
    db = sqlite3.connect(path, timeout=10, isolation_level=None)
    db.executescript(SCHEMA)
    return db


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def post(db, sender, harness, text):
    cur = db.execute(
        "INSERT INTO messages(ts, sender, harness, text) VALUES (?,?,?,?)",
        (now(), sender, harness, text),
    )
    return cur.lastrowid


def rows(db, after_id, not_sender=None):
    q = "SELECT id, ts, sender, harness, text FROM messages WHERE id > ?"
    args = [after_id]
    if not_sender:
        q += " AND sender != ?"
        args.append(not_sender)
    keys = ("id", "ts", "sender", "harness", "text")
    return [dict(zip(keys, r)) for r in db.execute(q + " ORDER BY id", args)]


def fmt(m):
    return f"#{m['id']} {m['ts']} {m['sender']} ({m['harness']}): {m['text']}"


def wait_after(db, after_id, not_sender, timeout_s):
    deadline = time.monotonic() + timeout_s
    while True:
        found = rows(db, after_id, not_sender)
        if found or time.monotonic() >= deadline:
            return found
        time.sleep(POLL_S)


def claim(db, reader):
    """Atomically move the reader's cursor to the newest id; return others' messages passed over."""
    db.execute("BEGIN IMMEDIATE")
    try:
        row = db.execute("SELECT last_id FROM cursors WHERE reader=?", (reader,)).fetchone()
        last = row[0] if row else 0
        found = rows(db, last, reader)
        if found:
            top = db.execute("SELECT MAX(id) FROM messages").fetchone()[0]
            db.execute("INSERT OR REPLACE INTO cursors VALUES (?,?)", (reader, top))
        db.execute("COMMIT")
        return found
    except BaseException:
        db.execute("ROLLBACK")
        raise


def cmd_wait(a):
    db = connect()
    deadline = time.monotonic() + a.timeout
    while True:
        found = claim(db, a.reader)
        if found:
            out = REPLY_HINT + "\n".join(fmt(m) for m in found)
            if a.hook:
                print(out, file=sys.stderr)
                return 2
            print(out)
            return 0
        if time.monotonic() >= deadline or os.getppid() == 1:
            return 0
        time.sleep(POLL_S)


def cmd_log(a):
    for m in rows(connect(), 0):
        print(fmt(m))
    return 0


def cmd_post(a):
    print(post(connect(), a.sender, a.harness, a.text))
    return 0


TOOLS = [
    {"name": "post_message", "description": "Post a message to the board.",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "read_messages", "description": "Return every message with id greater than after_id (default 0).",
     "inputSchema": {"type": "object", "properties": {"after_id": {"type": "integer"}}}},
    {"name": "wait_for_messages",
     "description": f"Wait up to timeout_s (max {MAX_WAIT_S}) for a message from another sender with id greater than "
                    "after_id. Returns an empty list on timeout; call again with the same after_id to keep waiting.",
     "inputSchema": {"type": "object", "properties": {
         "after_id": {"type": "integer"}, "timeout_s": {"type": "number"}}, "required": ["after_id"]}},
]


def call_tool(db, name, args):
    sender = os.environ.get("AGENT_BOARD_SENDER", "unknown")
    harness = os.environ.get("AGENT_BOARD_HARNESS", "unknown")
    if name == "post_message":
        return {"id": post(db, sender, harness, args["text"])}
    if name == "read_messages":
        return {"messages": rows(db, int(args.get("after_id", 0)))}
    if name == "wait_for_messages":
        t = min(float(args.get("timeout_s", MAX_WAIT_S)), MAX_WAIT_S)
        return {"messages": wait_after(db, int(args["after_id"]), sender, t)}
    raise ValueError(f"unknown tool {name}")


def handle(db, req):
    method, rid = req.get("method"), req.get("id")
    if method == "initialize":
        return {"protocolVersion": req["params"].get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}}, "serverInfo": {"name": "board", "version": "0"}}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        p = req["params"]
        try:
            out = call_tool(db, p["name"], p.get("arguments") or {})
            return {"content": [{"type": "text", "text": json.dumps(out)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": str(e)}], "isError": True}
    if method == "ping":
        return {}
    if rid is None:
        return None
    raise LookupError(method)


def cmd_serve(a):
    db = connect()
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        try:
            result = handle(db, req)
            resp = None if result is None else {"jsonrpc": "2.0", "id": req["id"], "result": result}
        except LookupError as e:
            resp = {"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32601, "message": f"no method {e}"}}
        if resp:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve").set_defaults(fn=cmd_serve)
    sub.add_parser("log").set_defaults(fn=cmd_log)
    sp = sub.add_parser("post")
    sp.add_argument("--sender", required=True)
    sp.add_argument("--harness", required=True)
    sp.add_argument("text")
    sp.set_defaults(fn=cmd_post)
    sw = sub.add_parser("wait")
    sw.add_argument("--reader", required=True)
    sw.add_argument("--timeout", type=float, default=900)
    sw.add_argument("--hook", action="store_true", help="print to stderr and exit 2 on delivery")
    sw.set_defaults(fn=cmd_wait)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
