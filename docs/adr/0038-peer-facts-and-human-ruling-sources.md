# 0038. Peer transport selects collaboration rules and cannot grant human authority

Date: 2026-10-27

## Status

Accepted

## Context

Five interviewed workflow coordinators used Paseo, while the peers extension named
only Claude Code as covered. Some adopters do not run Paseo. The approved design
separates basic replies from optional proactive fleet asks and retains Claude's
identity checks. Task peers-rules-name-each-host-binding holds the two interview
rounds, the design and the ideation gate-attempt 2.

## Decision

**Words:** 「可以，但是你應該要注意不是每個人都要 paseo，如果有人不是用 paseo 那該怎麼辦？」 — Captain, chat, 2026-10-26.

**Words:** 「paseo ext 放到 dev2，而 SD+paseo 則是更高層次的人與 agent fleet 的合作關係，前者是 fleet 內怎麼合作」 — Captain, chat, 2026-10-26.

**Words:** 「全准」 — Captain, chat, 2026-10-27, ideation gate and amendment 1.

**Asked:** 「需要你決定：第 7 批三張任務的設計（其中兩張已經照第 2 輪訪談修過），要不要一起批准進入實作？我建議全部批准，每一題都照我的建議。」 The peers recommendation included 「「你的裁定要附結構化出處」那個檢查拆成新待辦，和另一個 session 的 `adr-required-statement` 一起設計，我建議拆。」

**Options considered:**
- select the actual transport; peers includes incoming Paseo replies, with optional paseo for proactive asks; retain Claude checks (chosen)
- require paseo for replies, or choose by model vendor (not chosen)
- defer all running-asker replies to remove the steering fallback risk (not chosen)
- implement structured Captain-source refusal and active-task backfill here (split to captain-ruling-sources-checked by amendment 1)

**Recommended:** transport-based bindings, basic inbound replies in peers, optional
paseo for new asks, a five-minute deferral ceiling and explicit steering for requested
replies; split the source check into its own task.

**Protects:** none

Peer facts remain data. Read accessible original Captain words and their question
before relying on human authority; unavailable originals stay unverified. Claude
keeps its probe and question opening. Paseo uses stamped identity plus confirmed
area; a new busy-peer ask defers, while a requested reply may use explicit steering.
The deferral ends at five minutes, one still-busy recheck or no independent work.
The peer restriction does not govern FO follow-ups to its own workers.

ADR 0035's required learn/peers defaults remain. The optional dev2 paseo extension
points to Paseo's own skill; Spacedock retains dispatch, gates and task state, and
its Paseo integration retains human-to-fleet collaboration.

## Consequences

A queued receipt does not prove an answer. Steering can fall back to interruption
when unavailable or after a status race; no queue-only guarantee is added. Taskless
or bound-briefing exchanges go to a path-scoped workflow state note. Structured
source checks and migration are deferred, so this slice cannot authenticate a
relayed ruling or mechanically prove that an agent follows the policy. Reopen if
the Captain requires zero interruption risk or a host changes its delivery semantics.
