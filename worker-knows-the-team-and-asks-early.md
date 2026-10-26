---
title: A dispatched worker knows it works in a team toward one goal, checks what others did, and asks FO early
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:worker-knows-the-team-and-asks-early:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:worker-knows-the-team-and-asks-early-backlog-1
              briefing:
                id: briefing:worker-knows-the-team-and-asks-early:backlog:attempt-1:revision-1
                digest: sha256:80552830fef60c96866e01329cc23c37d5c4d0c491f095580b20dd75f4291551
                room-ref: ./worker-knows-the-team-and-asks-early/review/backlog/briefing-1
---

## Scope

- Source: the Captain (chat, 2026-10-26): 「一個額外的問題目前派工給worker時候沒有提醒他們是在一個多agent的合作團隊裡面，目的是合作完成專案任務？」, then, answering 「要開這張票嗎？」: 「要開。我覺得這一張跟peer有點關係，不只是讓他們知道有其他人在，他們也要知道目標是合作完成任務，所以要主動去思考，是不是有人做過是不是有人遇過，是不是有其他人在忙，特別是什麼時候應該提早問fo」.
- Outcome he named: a worker knows (1) it is one member of a multi-agent team whose goal is finishing the project task together; (2) to think actively whether someone already did this, already hit this, or is busy on it now; (3) when to ask FO early.
- Added 2026-10-26, the Captain (chat): 「要注意接手的不見得是codex但是重點是它要知道它在一個大流程的環節內，交棒是為了完成更遠大的目標，不是盲目努力完成不可能的目標」. So the wording names roles, not a vendor (whoever picks up next may be any reviewer or worker), and states that a handoff serves the larger goal: a worker that cannot finish hands back with what it found rather than pushing on toward an impossible target.
- Facts (2026-10-26): Spacedock 0.27.3 `skills/ensign` gives the completion channel and teams-mode mechanics, not the team's purpose or members; dev2 0.30.0 stage skills and the README's Dispatch facts give the worker's own boundaries only; the peers extension tells FO, not workers, how to ask another session.
- Bite: a validator ran a bare `git reset` in the shared state checkout and could have unstaged another FO's file (2026-10-24); a validator ran `git config` in a scratch clone (2026-10-25); several workers were unsure whether to signal `team-lead` or `main`; workers re-derived facts another session already held (FO relayed them by hand).
- Upstream first: Spacedock ensign skill (generic; changing it needs its owner and the Captain's approval); dev2 README `Dispatch facts` context section (read by every dispatch); `peers` EXTENSION.md; backlog new-work-checks-what-exists-first (same "check what exists first" theme for new work; ideation decides merge or order).
- Non-goals: letting workers message peer sessions directly; changing who decides.
- Added 2026-10-26, the Captain (chat, 2026-10-26): 「派工worker合作心態那張呢？考慮一個點，peers 放入 FO 合作心態，然後 paseo ext 放入如何使用 paseo cli 以及相關功能，這樣合理嗎？」, then, answering 「需要你決定：paseo 擴充放在 dev2 裡（跟 peers 放一起，比較好找），還是放在 spacedock 的 Paseo 外掛（符合 10/21 的裁定）？」: 「paseo ext 放到 dev2，而 SD+paseo 則是更高層次的人與 agent fleet 的合作關係，前者是 fleet 內怎麼合作」. The FO half of the mindset goes to `peers` (task peers-rules-name-each-host-binding); this task keeps the worker half, carried by every dispatch, since `peers` is FO-only and optional.

## FO alignment

Alignment: needed at ideation: how much a worker may do on its own (look, ask FO, ask a peer) is the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
