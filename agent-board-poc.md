---
title: A Codex session asks on a local board and an idle Claude session wakes and answers
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-agent-board-poc
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
started: 2026-10-13T08:57:55Z
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

### Dispatch Retries

- Retry 1: implementation — agent-error (API session limit, HTTP 429, after commit 44e8de6d, no stage report); nudged

## Stage Report: implementation

- DONE: AC-1: an idle Claude Code session launched with Conductor's flags starts a new turn after a board post with no user input between, reads and replies through the MCP server, and waits again; evidence is its stream-json output with timestamps, for each wake candidate tried, naming which worked
  Both candidates worked, run at 44e8de6d with `scripts/agent-board-poc/replica.py` (Conductor's flag set, haiku, one user message sent in total, stdout lines timestamped UTC). Candidate 1, Stop-hook `asyncRewake` (exit 2): post 09:55:01.325, new turn `session_state_changed` 09:55:01.475, `post_message` tool call 09:55:10.713, turn result 09:55:15; the same candidate on Conductor's own binary 2.1.286: post 09:56:31.295, new turn 09:56:31.490, answer 09:56:39.9. Candidate 2, background `board.py wait` the session starts itself: post 09:55:45.582, `task_notification` 09:55:45.742, `post_message` 09:55:58.485. In every run `REPLICA sent user message` appears once, before the first READY/started turn. Earlier pre-final runs also re-armed: a second CLI post to the same hook session was answered ("Paris", 1.4s after post).
- DONE: AC-2: a `codex exec` session with the board MCP configured posts a question, waits with bounded `wait_for_messages` calls, and prints the woken Claude's answer; evidence is the Codex output plus the board log
  `exchange.sh hook|shell` runs `codex exec` (0.153.4, per-run `-c mcp_servers.board.*`, stdin `/dev/null`) against the replica; Codex printed `ANSWER: 42` (hook, Conductor-binary hook) and `ANSWER: 6 times 7 is 42.` (shell); board logs below. Limit: `codex exec`, not a Conductor-hosted Codex; calling a stdio MCP tool from a Conductor-hosted Codex was NOT RUN.
- DONE: AC-3: one command prints every message of the AC-1/AC-2 exchange with sender, harness, time and text; evidence is that output, plus the cleanup done and what the POC does not prove
  `AGENT_BOARD_DB=<db> python3 scripts/agent-board-poc/board.py log` printed, for the hook run: `#1 2026-10-13T09:55:01.325+00:00 codex (codex-exec): What is 6 times 7?` / `#2 2026-10-13T09:55:10.717+00:00 claude (claude-code): 42`; shell run `#1 ...09:55:45.582 codex (codex-exec)` / `#2 ...09:55:58.500 claude (claude-code): 6 times 7 is 42.`; Conductor-binary run `#1 ...09:56:31.295` / `#2 ...09:56:39.961`. Cleanup and limits are under Summary.

### Summary

Built a stdlib-only Python board (`scripts/agent-board-poc/board.py`: one SQLite thread, MCP tools `post_message`, `read_messages`, `wait_for_messages` capped at 25 s, plus `log`/`post`/`wait`), a plugin dir with `.mcp.json` and a Stop-hook `asyncRewake` waiter, a Conductor-flag replica driver and `exchange.sh`. Commit 44e8de6d; no dependency added; plugin dir has no `plugin.json` because git's `*` pathspec in `version-parity-check.sh` would count a nested one (`bash scripts/version-parity-check.sh` and `skill-frontmatter-lint.sh` pass). `comment_ratio.py`: 2 comment lines of 236 code lines, 0.8%, under 5%; `number_guards.py check`: PASS; `doc_impact.py` lists 14 documents that only share the identifiers `wait_after`/`call_tool`: unaffected: unrelated symbol-name collisions; no ADR (POC, no decision beyond the Captain's rulings). The first final-evidence pass (09:14-09:50) hit the Claude session limit (HTTP 429, replica answered "You've hit your session limit"), so it was discarded and rerun after the reset.

Findings that shape the next decision: (1) a `SessionStart` `asyncRewake` hook blocks the replica before its first turn (14 hooks started, 13 returned, no `init`, observed 2 of 2 runs), so the waiter is armed by the `Stop` hook after the first turn, not at start; (2) the hook's text reaches the model as a system reminder and haiku first answered it in plain text instead of the tool (1 run), fixed by a one-line reply hint in the hook output; (3) the shell candidate relies on the model restarting the wait itself, the hook re-arms by itself; (4) the board claims delivery with a SQLite cursor, 3 concurrent waiters delivered #1 exactly once; (5) a waiter exits when its parent dies (`getppid()==1`) or after 900 s/600 s.

Does not prove: a session inside the Conductor app (replica only, same flags, haiku model; PATH `claude` 2.1.296 and Conductor's 2.1.286 both used); an idle Conductor-hosted Codex (never woken, by ruling); more than one exchange per session for the final runs; behaviour of stronger models or long idle times (idle in runs was seconds, not hours); concurrent threads, routing, or auth between sessions; the replica loads the user's real hooks and plugins (`--setting-sources=user,project,local`), which was left as Conductor does.

Cleanup: deleted every `/tmp/abp-*` store, scratch files and the `exchange.sh` temp dirs; killed the orphan replica Claude and waiters by captured PID (two earlier orphans were left by my own runs; the replica now terminates Claude on SIGTERM); no process remains. `codex exec -C <tmpdir>` wrote five `[projects."/private/tmp/abp-..."] trust_level = "trusted"` entries into `~/.codex/config.toml`; I removed exactly those 15 lines (diff-checked, no `abp` left). No user-level MCP, hook or Claude settings were edited. One slip: I used `pkill -f` on the waiter pattern once at about 09:10; it matched only my own POC processes.
