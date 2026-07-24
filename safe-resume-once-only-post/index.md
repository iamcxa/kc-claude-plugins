---
title: "Safe resume and once-only post"
source: superseded ship-flow pitch 2.3-safe-resume-once-only-post (agent-native PR review kit PR3); builds on ship-flow 2.1 (PR #48) + 2.2 (PR #50)
id: 50n4g9vyzdd12h03r6wskfkq
status: backlog
---

Appetite: 2 working days.

### Vertical Slice

An interrupted exact-head review resumes and posts an approved payload at most once.

### Boundary

Replay only compatible state, retry only incomplete work, persist an exact pending payload under restrictive permissions, and reconcile a durable marker or remote receipt before retrying an ambiguous GitHub mutation.

### Done Signal

Head or payload changes invalidate authorization; successful or stale payloads are removed; failed pending payloads expire after a bounded retention window. Daemon integration is default-deny and requires explicit preauthorization plus typed state, current head, coverage, and idempotency gates.

### Rollback

The legacy path remains available while the new posting path is disabled; rollback never deletes evidence needed to reconcile an uncertain remote result.
