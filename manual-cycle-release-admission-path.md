---
id: w8z5xrcexs9k1qq7xrwzx5bk
title: Add a manual Cycle-Release admission path
status: backlog
source: https://github.com/iamcxa/kc-claude-plugins/issues/305
product: kc-dev-flow
planning-window: Iteration 2
planning-outcome: kc-dev-flow Cycle-Release Admission Pilot
sprint: S6
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: "#305"
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:w8z5xrcexs9k1qq7xrwzx5bk:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:w8z5xrcexs9k1qq7xrwzx5bk-backlog-1
              briefing:
                id: briefing:w8z5xrcexs9k1qq7xrwzx5bk:backlog:attempt-1:revision-1
                digest: sha256:090dcffcf46754187a66e77c0d0b88390545c113bbb5e5522feb26d87a9e6fca
                request-digest: sha256:9ed5cf164977e3553f12d76b4bc304e7d22083ab853405caff94b34c1a0a550e
                room-ref: ./manual-cycle-release-admission-path/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:w8z5xrcexs9k1qq7xrwzx5bk:backlog:1
                briefing: briefing:w8z5xrcexs9k1qq7xrwzx5bk:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-28T00:04:38.624069Z"
                decision: approve
                reason: Captain approved the admitted direction and instructed future issues to omit the redundant Human-readable release brief wrapper, start directly with The problem, and retain the agent execution contract.
              application:
                target-stage: ideation
                state: pending
---

## Problem

kc-dev-flow separates planning authority from execution authority in its kernel, but the everyday handoff still depends on a long interactive session. Product shaping, profile selection, implementation, and verification can happen together, making progress difficult to read and forcing repeated Captain steering after execution starts.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: "One maintainer-visible repository change creates persistent process value for limited real use. It changes kc-dev-flow documentation and contracts but adds no production credentials, data migration, unattended operation, consumer-action compatibility break, SLO, or release and rollback ownership."
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - "Keep GitHub as the replaceable planning authority and Spacedock as the execution authority."
      - "Preserve one Issue to one Spacedock task to one isolated workspace or worktree."
    implementation:
      - "Change only existing kc-dev-flow product documentation, contracts, and deterministic coverage required for manual admission and route-back."
      - "Do not add automatic dispatch, a new stored schema, status synchronization, a new Spacedock stage, or a sprint-field rename."
    testing:
      - "Keep the kc-dev-flow contract, profile-route, comparator, and minimal-stack ablation suites green at the exact candidate revision."
      - "Add targeted negative coverage that rejects hidden one-to-many task execution or silent execution-time goal reshaping."
  scope_boundary: "One manual GitHub admission and fresh-context dogfood run only; excludes automatic Conductor Cloud dispatch, multi-Issue or multi-agent packages, new stored planning state, provider writes, stage changes, and release automation."
  promote_when:
    - "An accepted scope adds unattended dispatch, multi-Issue integration, provider writes, a consumer-action compatibility migration, SLO duty, or release and rollback ownership."
  decision:
    authority: "Captain via GitHub Issue #305 admission"
    at: "2026-08-27T23:48:54Z"
```

## Admission snapshot: accepted outcome and non-goals (copied from `source`)

Accepted outcome: A maintainer can fully shape one bounded change in GitHub, admit it into a Cycle, and hand it to a fresh workspace that reaches a reviewable candidate or explicitly returns to planning without reopening product direction.

Non-goals:

- No automatic Conductor Cloud dispatch.
- No multi-Issue or multi-agent package.
- No new hand-maintained JSON manifest.
- No GitHub/Spacedock status synchronization.
- No new SD stage or serialized `sprint` field rename.
- No change to POC, Pilot, or Production lifecycle depth.
- Admission grants no commit, pull-request, merge, release, or publication authority.

## Acceptance evidence

- Existing kc-dev-flow contract, profile-route, comparator, and minimal-stack ablation suites pass at the exact candidate revision.
- Targeted negative coverage rejects hidden one-Issue-to-many-task execution or silent execution-time reshaping.
- One Spacedock task and one fresh workspace or worktree are recorded for Issue #305.
- The fresh executor receives no planning transcript.
- The executor produces one reviewable candidate or one structured planning delta within one working day.
- Closeout records elapsed span, Captain decision count, and `proceed`, `change`, or `stop` for a later multi-Issue pilot.

## Measurement

Record the admission time, workspace or worktree identity, exact candidate revision, Captain decisions after admission, route-back events, and final `proceed`, `change`, or `stop` result.
