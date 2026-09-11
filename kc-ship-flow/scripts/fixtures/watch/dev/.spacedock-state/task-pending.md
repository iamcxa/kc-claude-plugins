---
title: "fixture: workspace still initializing"
status: implementation
sprint: ship-cloud-wrapper
sprint-readiness: ready
id: fixpending000000000000000
---

Fixture entity: the workspace has not finished provisioning yet, so there is no session
to poll. Must read as `pending`, not `stopped`.
