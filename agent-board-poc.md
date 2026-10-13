---
title: A Codex session asks on a local board and an idle Claude session wakes and answers
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:agent-board-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:agent-board-poc-backlog-1
              briefing:
                id: briefing:agent-board-poc:backlog:attempt-1:revision-1
                digest: sha256:f74b07571bde05cf0684e29537791bb1dfe82754b2c50b987aef97f929d0af8d
                room-ref: ./agent-board-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:agent-board-poc:backlog:1
                briefing: briefing:agent-board-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T08:56:52.329629Z"
                decision: approve
                reason: 'Captain approved outcome, scope, non-goals, budget and stop condition: 「准」 (2026-10-13 chat)'
              application:
                target-stage: implementation
                state: consumed
---

Claude Code sessions can message each other and wake the receiver, but nothing crosses
to Codex. Measured on 2026-10-12: from Claude, `codex queue --thread <id> --message`
reached a Conductor-hosted Codex session, but it did not wake that session, and the
message never showed in Conductor, so the Captain could not see what was sent.
Codex has no channel back to Claude at all. The Captain wants agents in different
harnesses to find the session that knows an answer without him relaying. This POC
tests the riskiest assumption under that: an idle Claude session can be pulled in by
a message from a Codex session, through one MCP server both of them use.

bite: the Captain relays every Codex↔Claude question by hand today, and a `codex queue`
message is invisible to him (2026-10-12 measurement above).
consumer: the Captain's own Conductor sessions, and later the kc-dev-flow-2 `peers`
extension, which today covers same-harness peers only.

## Scope

Captain rulings, 2026-10-13: v1 is Claude Code and Codex on this Mac only (「可以」 to
"no dot, no Sites, no phone view in v1"); build our own small POC rather than adopt an
existing system (「照建議做 poc」); route is the dev2 POC workflow (「1」).

In scope:
- One local MCP server (stdio) with one thread: post a message, read messages,
  and a bounded `wait_for_messages` long-poll. The store is one SQLite file, which is
  also the log the Captain reads.
- Packaging as a Claude Code plugin directory loadable for the test, plus the
  Codex MCP registration needed for the test (per-run `-c` override preferred over
  editing `~/.codex/config.toml`).
- Two Claude wake candidates, both tried and compared:
  1. a plugin hook with `asyncRewake: true` that blocks until a new message exists and
     exits 2 (Claude Code hooks docs: "runs in the background and wakes Claude on exit
     code 2");
  2. a background shell command the session itself starts that blocks until a new
     message exists and exits (the mechanism that already wakes Conductor sessions,
     for example `pr_watch.py wait`).
- Codex as the asker only: it posts, then repeats bounded `wait_for_messages` calls
  inside its own turn until the reply arrives.

Non-goals: dot, GPT Sites or any hosted service; a phone or web view; several threads
or projects; session registration, routing or claiming; waking an idle Codex (Codex
read its own runtime on 2026-10-13: an app-server it does not own, such as Conductor's
private stdio child, cannot be reached from outside); Claude Code Channels (Conductor
launches claude in stream-json mode, which the Channels docs say ignores the
development-channels flag); permission relay; marketplace registration or a release.

Budget and stop condition: one implementation cycle. Stop and report if neither wake
candidate starts a new Claude turn in AC-1; the rest of the POC is then a shared file
and not worth building. Stop and report if the proof needs anything outside this list
(a daemon on a fixed port, a change to Conductor, a user-level config left installed).

Prior art read 2026-10-13, borrow designs only: agent-inbox (`asyncRewake` wake),
claude-message-mcp (`wait_for_messages` plus idle-command split), agent-mailbox-mcp
(SQLite schema and tool shapes), Agent Intercom (bounded-wait loop for Codex).
None is adopted: licence (GPL, AGPL, unclear), a required hub or broker, or Windows-only.

Cleanup: delete the test store and any test-only config; leave no user-level MCP or
hook registration installed. The POC code may be disposable; record what it does not
prove.

## FO alignment

Alignment with the Captain before implementation: not needed. Scope, route, non-goals
and the build-vs-adopt choice were each ruled by the Captain on 2026-10-13 in this
session; POC defaults to no consultation.

## Acceptance criteria

**AC-1**: An idle Claude Code session launched with the flags Conductor uses
(`--input-format stream-json --output-format stream-json --permission-prompt-tool stdio`)
starts a new turn when a message is posted to the board, reads it through the MCP
server, posts a reply, and is waiting again, with no user message sent to it in between.
Verified by: the session's stream-json output showing a new turn whose start time is
after the post time and no user input between them, for each wake candidate tried, and
which candidates worked. Limit: a replica of Conductor's launch, not a session inside
the Conductor app; the validation acceptance script carries the in-app check.

**AC-2**: A `codex exec` session with the board's MCP server configured posts a
question, waits with bounded `wait_for_messages` calls, and receives and prints the
answer the woken Claude session posted.
Verified by: the Codex run's output containing the Claude answer, and the board log
showing question then answer with their times. Limit: `codex exec`, not a
Conductor-hosted Codex session; whether that one can call a stdio MCP tool is recorded
as observed or not run.

**AC-3**: Every message either side sent in AC-1 and AC-2 is readable by the Captain
from one command, with sender, harness, time and text.
Verified by: that command's output covering the full exchange.
