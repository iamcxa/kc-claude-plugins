# 0056. The idle look prompts unclaimed release walks from versioned progress

Date: 2026-11-03

## Status

Accepted

## Context

The release-walk-due-trigger task records that two finished releases were walked
only after the Captain asked. ADR 0031 distinguishes finished development from
delivery acceptance, but the progress producer's pending label had no idle-look
consumer. ADR 0012 requires the producer to own and version a shared shape.
The approved design found every current map under `docs/journey/`; existing
journey extensions and the adoption probe already use that directory.

## Decision

**Words:** 「可以」 — Captain, chat, 2026-11-03, the task's ideation gate and
Captain amendment 1.

**Asked:** 「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成『在 kc-journey-map 登記 journey-progress/v1，預算放寬為兩個 PR，kc-journey-map 那個先合併』，可以嗎？」

**Options considered:**
- Discover every `.yaml` under the code checkout's `docs/journey/`, register
  `journey-progress/v1` with its producer first, and prompt unclaimed pending
  walks from the existing idle look (chosen).
- Add a README `journeys:` key; an adopter omitting it would receive no reminder.
- Require FO to invoke `due` by hand; the missed-walk cause would remain.
- Consume an unregistered progress shape; rejected by the Captain's amendment.
- Also prompt re-walks after complaint fixes; deferred outside this task.

**Recommended:** Directory discovery and no re-walk trigger, with the design's
unregistered-shape recommendation replaced by the Captain's producer-first
registration and two-PR budget.

**Protects:**
- `kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py` — `cmd_due` reads only the named progress major and silences a walk only when a task claims it.

When the workflow lists `release-acceptance`, `pr_watch.py tasks` reads each map
under `docs/journey/` through the sibling progress producer and prints one
`next:` line for each release whose acceptance is `pending delivery acceptance`
and which no live or archived task claims with
`release-acceptance: <journey>/<release>`. Flat and folder-form task claims count.
The read is skipped when the map has no unclaimed release with a done task.
A missing producer or failed read prints `release-acceptance not run:`.
Unlisted workflows run none of this.

`journey-progress/v1` is a third meeting point alongside ADR 0031's walk and
acceptance schemas. kc-journey-map owns its field table and version hash; its
registration PR merges before this consumer. No plugin imports the other's code.

## Consequences

FO sees the walk prompt at its normal idle look without remembering a second
command. Each candidate map adds one progress read; the task report records its
measured cost. A claim remains effective after archive, including a declined walk.
Maps elsewhere are not discovered, and a cached sibling version need not be the
enabled version. No cache, map acceptance field or re-walk reminder is added.
Revisit when repeated progress reads become costly, a map lives elsewhere, or a
missed re-walk demonstrates the deferred trigger is needed.
