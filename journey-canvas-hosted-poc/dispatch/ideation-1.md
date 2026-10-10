# journey-canvas-hosted-poc — ideation, cycle 1

Dispatched: 2026-10-10 from state commit 35135584bd396b3c45f826c5c85cf87f6a8f9332; base origin/main 03045a47ea850266b46dad557229343bd56e1d04
Model: sonnet (the build default; no override)

## Checklist

Design for a proof of concept that hosts a kc-journey-map canvas room, read against the canvas's actual sync stack at origin/main 03045a47ea850266b46dad557229343bd56e1d04 (kc-journey-map/server/canvas-server.ts, rooms.ts, save.ts, @tldraw/sync 5.4.0, the share front end vite.share.config.mts): the hosting options compared (including tldraw's own hosted-sync templates and why Netlify, where subspace-relay runs, does or does not hold the WebSocket sync), each checked against its own documentation or source, not assumed
What the POC must prove, as acceptance criteria with reproducible Verified-by clauses: a room reachable by a shared link with this machine off, persistence across a server restart, edit access limited to people the Captain allows, and the existing local render and read paths still able to write and read the hosted room
Captain decisions one per line with a recommendation, including the provider and its cost (stated only where measured or quoted from the provider's published pricing with the date read) and how access is granted

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.14.0
kc-journey-map package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-journey-map/1.5.1
Repository: kc-claude-plugins (public); package kc-journey-map. The outcome is a decision with evidence; no production move.
Never git stash. Ideation writes no repository file, branch or commit; create no cloud account or resource.
