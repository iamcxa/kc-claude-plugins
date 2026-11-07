---
title: Worker browser checks use Paseo's browser tools where the workflow lists paseo, with the known limits written down
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:worker-browser-checks-use-paseo-browser:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:worker-browser-checks-use-paseo-browser-backlog-1
              briefing:
                id: briefing:worker-browser-checks-use-paseo-browser:backlog:attempt-1:revision-1
                digest: sha256:795a868b345083afe6adce54d8fd23185373d0d6ecd882cde50b2b0049005736
                room-ref: ./worker-browser-checks-use-paseo-browser/review/backlog/briefing-1
---

Where the workflow README lists the paseo extension, a worker's local browser verification uses Paseo's browser tools (mcp__paseo__browser_*) by default instead of Chrome for Testing (agent-browser), and the paseo extension states the known limits and their workarounds.

## Scope

- Source: the Captain 「開，然後再給我看一次主題與項目。」 then 「現在不用再強制用 agent-browser，可以叫」 (chat, 2026-11-06, message cut off), answering 「要開這張待辦嗎？」 about this task. His request as relayed earlier by the qnow dev2 FO (Paseo 519ab4c8, 2026-11-06, relayed, confirmed here by his 「開」): 「本輪結束後給 dev2 fo 一個訊息，讓他針對 paseo ext 最佳化，在合適時機不要再用 chrome for testing」.
- Bite (qnow dev2 FO's first-hand report, 2026-11-06, not re-run here): on qnow staging and production, headed agent-browser stayed stuck on Clerk's Cloudflare Turnstile twice and the Captain's manual pass in that window failed too; the Paseo browser passed it and covered a full walk the Captain watched live.
- Known limits to write down (same report): the Captain's IME input can reach a field browser_type is filling (use browser_evaluate with the native value setter plus an input event); some React Native web buttons respond only to browser_click on a snapshot ref; browser_evaluate times out at 15 s (start, park the result on window, poll); signature-canvas drawing untested.
- Facts FO read on 2026-11-06: kc-dev-flow-2 0.35.0 names no agent-browser or Chrome for Testing rule; the paseo extension already routes attended human pages to Paseo; the agent-browser mandates live in adopter AGENTS.md files (qnow: "Run browser work headed") and in the e2e-pipeline plugin.
- Non-goals: CI browser runs (no Paseo; they stay headless); the e2e-pipeline plugin; editing any adopter's AGENTS.md (each adopter's FO changes its own after release).

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- The paseo extension states the default and the four limits with their workarounds, and one worker browser check on an adopter that lists paseo runs on Paseo's browser tools end to end.

## FO alignment

Alignment: needed at ideation; how the default is stated and which adopter proves it are his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
