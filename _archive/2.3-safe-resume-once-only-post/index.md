---
id: "2.3"
title: "Safe resume and once-only post"
pattern: shaped-child
parent_pitch: "2"
harvest_required: true
layout: folder
appetite: "2 working days"
depends_on:
    - "2.2"
status: done
stage_outputs: {}
completed: 2026-07-24T09:38:49Z
archived: 2026-07-24T09:38:49Z
---

### Vertical Slice

An interrupted exact-head review resumes and posts an approved payload at most once.

### Boundary

Replay only compatible state, retry only incomplete work, persist an exact pending payload under restrictive permissions, and reconcile a durable marker or remote receipt before retrying an ambiguous GitHub mutation.

### Done Signal

Head or payload changes invalidate authorization; successful or stale payloads are removed; failed pending payloads expire after a bounded retention window. Daemon integration is default-deny and requires explicit preauthorization plus typed state, current head, coverage, and idempotency gates.

### Rollback

The legacy path remains available while the new posting path is disabled; rollback never deletes evidence needed to reconcile an uncertain remote result.

### Superseded

Superseded — the agent-native PR review kit moved from ship-flow to the `docs/dev` workflow. This pitch is now built as the `docs/dev` task `safe-resume-once-only-post` (id `50n4g9vyzdd12h03r6wskfkq`), seeded from this body. No further work happens on this ship-flow entity.
