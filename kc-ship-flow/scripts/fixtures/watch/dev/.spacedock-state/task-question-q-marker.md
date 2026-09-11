---
title: "fixture: question tail using a 'Q:' marker line, not a trailing '?'"
status: implementation
sprint: ship-cloud-wrapper
sprint-readiness: ready
id: fixqmarker0000000000000
---

Fixture entity: the worker's last assistant turn ends with a plain statement, but an
earlier line in that same turn opens with `Q:` -- one of the batch's real question shapes
that a bare "ends in ?" heuristic missed.
