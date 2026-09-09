---
id: 20w9we1wvtdy500nf9rc3a65
title: Reverse a story map out of a Linear project, and see whether it survives contact
status: implementation
source: captain
product: kc-team-ops
planning-window:
planning-outcome:
sprint: journey-map-poc
sprint-readiness: ready
started: 2026-09-09T03:45:05Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-reverse-a-story-map-from-linear
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:20w9we1wvtdy500nf9rc3a65:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:20w9we1wvtdy500nf9rc3a65-backlog-1
              briefing:
                id: briefing:20w9we1wvtdy500nf9rc3a65:backlog:attempt-1:revision-1
                digest: sha256:fd087955f59c08344668c6da75bd585963b41d5332092b60b4c9bf59a9406a39
                room-ref: ./reverse-a-story-map-from-linear/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:20w9we1wvtdy500nf9rc3a65:backlog:1
                briefing: briefing:20w9we1wvtdy500nf9rc3a65:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-09T03:43:59.766489Z"
                decision: approve
                reason: 'Captain approved the seed at the backlog gate: the POC question, the falsifier against an independently drawn map, and the stop point at a story map plus an unattachable-issue list. Constraint recorded as AC-1 and Non-goals: draw into a separate room and file, leave the existing planning board untouched.'
              application:
                target-stage: ideation
                state: consumed
---

## The problem

Every board `kc-journey-map` has drawn so far was drawn by its author, for its author. The
tool's own risk register covers whether it breaks; nothing covers whether it is useful. The
untested assumption is that these boards get a team to aligned value faster than talking
without them, and no second person has drawn one.

The captain has supplied a Linear project and will supply a second map of the same project
drawn independently from another engineer's angle. Two independent readings of one project
are the cheapest thing that can falsify the assumption: if they are noticeably orthogonal,
comparing them is the alignment work the tool claims to accelerate. If the reversed backbone
is unrecognisable to the people doing the work, reversing from a tracker is the wrong input
and that branch closes cheaply.

## Work profile receipt

**Profile:** POC — bounded exploration.

**Next decision:** whether a journey map reversed from a tracker is a usable starting point
for a value-alignment conversation, or whether the backbone must come from people.

**Cheapest credible falsifier:** draw one story map from the named Linear project, then set
it beside the independently drawn map the captain supplies. The captain judges whether the
invented backbone is recognisable.

**Budget:** one worker dispatch to draw, one comparison round.

**Observable stop point:** a story map for the project plus a list of issues that attach to
no activity, presented to the captain. Stop there. Do not draw a journey board or a function
map for it.

## Accepted outcome

A story map reversed from the project, and a named account of what was invented rather than
read.

## Non-goals

- Do not modify the existing planning board or the worked example. This work draws into its
  own room and its own file.
- No journey board, no function map, no plan-flow handoff.
- No change to the reversing mechanism itself unless drawing proves impossible without one.

## Acceptance evidence

**AC-1** A story map file exists for the Linear project, rendered to a room of its own, with
the existing `draw-a-journey` room and `journey.example.yaml` unchanged.

**AC-2** Every backbone activity is marked as read from the tracker or invented by the
worker. A map that does not distinguish them fails this criterion.

**AC-3** Every issue in the project is either attached to an activity or listed as
unattachable, with a reason. No issue is silently dropped.

**AC-4** The captain, shown the map beside the independently drawn one, states whether the
invented backbone is recognisable. This is the value criterion the other three serve.

## Route-back conditions

Return `poc_outcome` to planning. Create no delivery work from this task.

## Measurement

Count of issues that attach to no activity, and the captain's verdict on AC-4.

## Stage Report: implementation

- FAILED: Read the captain's named Linear project and draw one story map from it, into its own room and its own journey file, leaving the existing draw-a-journey room and journey.example.yaml byte-identical.
  The CODE worktree this dispatch assigned (montpellier-v1/.worktrees/spacedock-ensign-reverse-a-story-map-from-linear, cut from bb6f737b) carries no kc-team-ops/skills/kc-journey-map at all — `find kc-team-ops -iname "*journey*"` returns nothing there. origin/main carries an older kc-journey-map (SKILL.md, board-template.html, cell-contract.md only). The three files this dispatch names (map-from-conversation.md, canvas.md, journey.example.yaml) plus lib/journey-render.mjs exist only on origin/iamcxa/journey-map-skill-merge @ ba9625ce, unmerged. Escalated via `SendMessage(to="team-lead", ...)`: no agent named team-lead was reachable (tool returned "No agent named 'team-lead' is reachable"), and no `ListAgents`-class tool is available in this session either, so the standard escalation channel is not live here. Did not merge, rebase, or reset any branch myself — re-pointing the worktree's base is a call that belongs to whoever built the dispatch, not to the ensign. `journey.example.yaml` and the `draw-a-journey` room were never touched by this session (verified: no commit or write against tacoma or origin/main; the worktree's own git status is clean).
- DONE: Mark every backbone activity as read-from-the-tracker or invented, so the captain can tell which is which without asking.
  Drafted in reverse-a-story-map-from-linear.journey-draft.yaml (this directory) against the schema read from canvas.md/journey.example.yaml/map-from-conversation.md (read-only, from tacoma's iamcxa/journey-map-skill-merge branch — no writes made there). All 6 backbone activities are marked INVENTED in their `note:` field, with the specific tickets each was synthesized from named. The persona line is marked read-from-tracker (the project's own summary field, quoted verbatim). This satisfies the marking requirement even though rendering is blocked — the file itself carries it, per the AC's own wording.
- DONE: Account for every issue in the project: attached to an activity, or listed as unattachable with a reason. None silently dropped.
  Read all 48 issues in the project via `list_issues(project=..., includeArchived=true)`, `hasNextPage: false`. 41 attached across the 6 invented activities, 7 listed under `unattachable:` with a one-line reason each (process/governance/decision/theme tickets that don't correspond to one step). Verified by extracting every `DRC-####` id the draft file references and diffing against the full id list pulled from Linear: zero missing, zero duplicated.

### Summary

The Linear-read half of this task is complete and durable (48/48 issues accounted for, backbone drafted with explicit tracker/invented marking) in `reverse-a-story-map-from-linear.journey-draft.yaml`. The draw-half is blocked: the dispatched CODE worktree does not carry the kc-journey-map tool at all — it exists only on tacoma's unmerged `iamcxa/journey-map-skill-merge` branch, which is also this dispatch's own session id per the checkpoint refs, suggesting the dispatch was authored against tacoma's state but the worktree was cut from montpellier-v1's older HEAD. Needs a decision: re-point/rebuild the worktree from that branch, or another source for the tool, before the file can be rendered into a room and AC-1/AC-4 can be judged. No Linear writes made; no existing journey-map files or rooms touched.

## Stage Report: implementation (cycle 2)

- DONE: Put the worktree on the branch that has the tool, install from that fresh checkout, and report whether the install worked without a fix.
  Fetched and `git reset --hard origin/iamcxa/journey-map-skill-merge` (ba9625ce) onto the ensign's own branch, per FO decision — no merge/rebase judgment made by this session. `npm install` in `kc-team-ops/` completed clean (267 packages, 0 vulnerabilities) with no workaround. One drift found: install rewrote `package-lock.json` (+3 lines) — npm normalizing the root package entry to carry the `engines` field already in `package.json` but not previously recorded in the committed lock. Left uncommitted in the CODE worktree; not reverted, not committed. `npm run doctor` correctly reported both ports busy (the running shared canvas) — this is `doctor.mjs` working as designed, not an install defect.
- FAILED: Render the drafted journey file into a room of its own, export both pages as PNG, open the images and say what is on them.
  Render succeeded in isolation: started a private doc-API server (`JOURNEY_API_PORT=0` → OS-assigned `127.0.0.1:55098`, confirmed via its own startup line and `/health`), ran `node lib/journey-render.mjs <draft> linear-reverse` against it — `200, 137 shapes`. `.rooms/` is gitignored and gets its own directory per server process (`server/rooms.ts`: `JOURNEY_ROOMS_DIR ?? './.rooms'`), so this never touched the shared canvas's room store; confirmed by `GET :5858/health` before and after — room list `[draw-a-journey, live-check, review-room, smoke-36754, smoke-37506, storymap-demo]`, no `linear-reverse` at any point. PNG export is structurally blocked without touching the shared canvas or editing code: `server/client/App.tsx:6` hard-codes `SERVER_URL = http://localhost:5858` — a literal, no env var, no query param, no build-time injection anywhere in the 43-line file. `journey-export.mjs` always opens `http://localhost:3737/?room=<id>` via agent-browser. Any vite client — the shared one on 3737, or a fresh one on another port — loads that same bundle and syncs over websocket to port 5858 only, i.e. to the shared canvas, never to a privately-ported server. There is no combination of `JOURNEY_API_PORT` and vite port that gets the browser to my isolated room: `JOURNEY_API_PORT` only reaches `server/canvas-server.ts` and `lib/render.mjs`'s HTTP write path, not the compiled client. Additionally, `npm run canvas` cannot even be attempted stand-alone here: its `precanvas` hook runs `doctor.mjs`, which probes only the fixed 5858/3737 (`lib/doctor.mjs:51-52`, no `JOURNEY_API_PORT` read) and fails closed while the shared canvas is up — the FO's own `JOURNEY_API_PORT=0` path only works by hand-invoking `tsx server/canvas-server.ts` outside `npm run canvas`. Per this stage's DO NOT ("if the render is impossible without a code change, stop and say so"): stopped without writing to the shared canvas and without editing `App.tsx`. No PNGs exist to open.
- DONE: Report the render's own release-coverage output; say where the 10 releaseless stories land; leave `draw-a-journey` and `journey.example.yaml` byte-identical.
  Coverage lines from the render (verbatim): `a1: covers 4/6 activities  not touched: leave-feedback, revoke-the-share` / `a2: covers 2/6  not touched: get-the-tools, open-and-read, leave-feedback, revoke-the-share` / `d: covers 1/6  not touched: get-the-tools, publish-and-hand-out-link, leave-feedback, read-feedback-back, revoke-the-share` / `b: covers 2/6  not touched: get-the-tools, publish-and-hand-out-link, read-feedback-back, revoke-the-share` / `c: covers 3/6  not touched: get-the-tools, publish-and-hand-out-link, leave-feedback`. The 10 releaseless stories (verified against the draft YAML: exactly 10 stories with no `release:` key) are all under two activities — 8 under `publish-and-hand-out-link`, 2 under `open-and-read` — matching why those two activities show 0 releases touching them anywhere above. `lib/storymap.mjs:163` puts every releaseless story into a synthetic `UNASSIGNED` band (`goal: 'No release decided yet.'`), rendered as the last horizontal band on the Story map page (release-line at y=4778, confirmed by reading the written room's own doc snapshot). Checked the fontSizeAdjustment hazard the FO named: all 58 note shapes in the rendered room carry `fontSizeAdjustment: 1`, none at 0 — no blank-sticky risk in this render. `journey.example.yaml`: `git diff --quiet ba9625ce -- kc-team-ops/skills/kc-journey-map/references/journey.example.yaml` reports identical. `draw-a-journey` room: never connected to (no agent-browser call made against 3737/5858 this session); the shared server's own room list, read twice, never lists it and its `clock`/session count for `draw-a-journey` (1 active session, clock 18 both times) is consistent with only its own owner touching it.

### Summary

Install and render both work; PNG export does not, for a structural reason and not a fixable mistake in this session: the tldraw client's sync URL is a hard-coded `localhost:5858` with no override, so a browser can only ever see the shared canvas, never a privately-ported one. Two ways out, no implementation done by this session: (a) the FO lifts "do not reuse 5858" and this session writes `linear-reverse` there instead — rooms are isolated by id, `draw-a-journey` is unaffected, export would work today with zero code changes; (b) a small code change makes `SERVER_URL` and the export target configurable. Data survives either way: `linear-reverse` is fully rendered (137 shapes, 10 releaseless stories correctly banded, no blank stickies) on the isolated private server and re-renders identically once run against whichever server the FO picks.

## Stage Report: implementation (cycle 3)

- DONE: Render `linear-reverse` into the shared canvas (5858/3737) once the FO lifted "do not reuse 5858"; capture the renderer's own coverage lines; confirm `draw-a-journey` untouched.
  `node lib/journey-render.mjs <draft> linear-reverse` against the shared, already-running server: `200, 137 shapes`. Coverage verbatim: `a1: covers 4/6 activities  not touched: leave-feedback, revoke-the-share` / `a2: covers 2/6  not touched: get-the-tools, open-and-read, leave-feedback, revoke-the-share` / `d: covers 1/6  not touched: get-the-tools, publish-and-hand-out-link, leave-feedback, read-feedback-back, revoke-the-share` / `b: covers 2/6  not touched: get-the-tools, publish-and-hand-out-link, read-feedback-back, revoke-the-share` / `c: covers 3/6  not touched: get-the-tools, publish-and-hand-out-link, leave-feedback`. `draw-a-journey` checked via `/health` before and after my render: `sessions: 1, clock: 18` both times, unchanged. The FO independently verified afterward that `linear-reverse` exists with six pages and `draw-a-journey` is untouched, and accepted this half of the work.
- FAILED: Export the Story map page and one release board as PNG via `lib/journey-export.mjs`, open them, and judge whether the six invented activities read as a journey or a feature list.
  Multiple attempts (default daemon, then an isolated `AGENT_BROWSER_NAMESPACE`, with progressively longer timeouts) hit intermittent `agent-browser` failures — `open` timeouts and `Resource temporarily unavailable (os error 35) (after 5 retries)` on `eval` — under a verified severe host load (`uptime`: load averages 53/178/152 on a 3-user box, 26 concurrent Chrome-for-Testing processes). The FO subsequently identified the root cause directly: both of us were driving the same shared `agent-browser` instance at once and the CDP channel died from that contention — their scheduling error, not a defect in my approach. Per the FO's instruction I stood down, killed my own isolated-namespace daemon, and did not touch the browser again. The FO is completing the export themselves. No PNG was produced or opened by this session; the visual "journey vs. feature-list" judgment was not attempted and is not claimed.

### Three findings carried forward so they are not lost when this task closes

1. **`npm install` rewrites `package-lock.json` on a clean checkout.** Exact diff (`git diff` on `kc-team-ops/package-lock.json`):
   ```
   @@ -27,6 +27,9 @@
            "tsx": "^4.19.2",
            "typescript": "^5.8.3",
            "vite": "^8.0.16"
   +      },
   +      "engines": {
   +        "node": ">=22.13.0"
          }
        }
   ```
   npm is normalizing the root package entry to carry the `engines` field already declared in `package.json` but never recorded in the committed lock. Left uncommitted in the CODE worktree; not reverted, not committed by this session.

2. **`server/client/App.tsx`'s `SERVER_URL` is a hard-coded literal (`http://localhost:5858`) with no env, query-param, or build-time override anywhere in that 43-line file.** A browser can write to a privately-ported doc-API server (`JOURNEY_API_PORT`) but can never see the result, because every browser client syncs only to 5858. A configurable version would need to reach six places, all fixed to the same two ports today: `SERVER_URL` itself (the `useSync` uri in `App.tsx`), `pageLink` in `lib/records.mjs` (bakes `localhost:3737` into every release-label link), the `open` URL in `lib/journey-export.mjs`, the startup log line in `server/canvas-server.ts`, the `[5858, 3737]` probe list in `lib/doctor.mjs`, and `server.port` in `vite.config.mts`. No code changed.

3. **`lib/doctor.mjs` probes only the fixed ports 5858/3737**, so it fails closed with `FAIL port 5858/3737 in use` whenever *any* other canvas is already running — which, per this task, is now the normal case rather than the exception the doctor's message implies. It does not read `JOURNEY_API_PORT`, so the FO's own port-isolation instruction can only be carried out by hand-invoking `tsx server/canvas-server.ts`, never through `npm run canvas` (whose `precanvas` hook runs this same doctor and aborts on the same FAIL).

### Summary

The render is done, verified, and accepted by the FO: `linear-reverse` exists as its own room on the shared canvas with the six-activity backbone and 137 shapes, `draw-a-journey` and `journey.example.yaml` are byte-identical to before this task. The PNG export did not complete in this session — root cause was two agents driving one shared browser at once, not a defect in the render or in this session's approach — and the FO is finishing that step directly. This session made no further browser, render, or server calls after being told to stand down.
