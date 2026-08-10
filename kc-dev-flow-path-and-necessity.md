---
title: "kc-dev-flow: correct mod adoption path and enforce mechanism necessity"
source: "Captain directive `修 bug + 183`, GitHub issue #183, 2026-08-10"
product: kc-dev-flow
sprint: captain-directed
design:
id: 9f63nm17bntn0ts7k9b1nm9c
---

## Problem

The canonical reverse-recovery mod tells adopters to copy it into
`docs/ship-flow/_mods/`, although kc-dev-flow binds mods under each adopted
workflow's own `_mods/` directory. Separately, kernel's mechanism-necessity rule
has no local rejection predicate, so a new control can pass ideation without
naming the AC it serves, the simpler alternative, or an escaped defect.

The captain authorized this bounded repair together with issue #183. The
published-tag smoke review remains a separate unscheduled follow-up.
