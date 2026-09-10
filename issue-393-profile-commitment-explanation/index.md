---
title: "fix(kc-dev-flow): explain the next commitment during profile selection"
status: backlog
product: kc-dev-flow
sprint: S7
sprint-readiness: ready
issue: iamcxa/kc-claude-plugins#393
provenance: https://github.com/iamcxa/kc-claude-plugins/issues/393
id: td0yhsww2jnwnrzh5c6wc6er
started: 2026-09-10T09:09:39Z
gates:
    version: 1
    records:
        - id: gate:td0yhsww2jnwnrzh5c6wc6er:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:td0yhsww2jnwnrzh5c6wc6er-backlog-1
              briefing:
                id: briefing:td0yhsww2jnwnrzh5c6wc6er:backlog:attempt-1:revision-1
                digest: sha256:68a25b098d6ffe011b12240fa4392e022eda7c5dbe98d22b3c51707a37c2872f
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:td0yhsww2jnwnrzh5c6wc6er:backlog:1
                briefing: briefing:td0yhsww2jnwnrzh5c6wc6er:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T09:12:02.999076Z"
                decision: approve
                reason: Captain Kent approved these issue repairs with "確認，就這樣交付" and selected Pilot for both with "Pilot可以". This initial admission records that existing scope/profile decision after publishing its administrative brief; it grants shape only and does not claim approval of a later implementation or future evidence.
              application:
                target-stage: ideation
                state: pending
---

The existing selection conversation explains this item's next commitment, unresolved assumption, observable result, and included operational duties before the Captain chooses. Its existing profile receipt preserves that accepted scope.

## Development Brief

### Problem

Profile selection can be understood as project scaffolding while the operator accepts hosted operations and recovery. The existing question about negative evidence is too abstract when the first real journey is unproved.

### Accepted outcome

The existing selection conversation explains this item's next commitment, unresolved assumption, observable result, and included operational duties before the Captain chooses. Its existing profile receipt preserves that accepted scope.

### Non-goals

- No new profile, receipt schema, workflow stage, approval gate, standing audit, or mandatory sequence of profiles.
- No operational deployment, credential use, data migration, rewrite of existing records, or retrospective relabeling of completed work.
- No self-improvement collector or new POC experiment; no change to the originating product.

### Route-back conditions

Return to the Captain if the correction requires new operational responsibility, a consumer migration, a new receipt/schema or gate, broader product work, or a behavioral proof method requiring unapproved external spend.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: "A bounded retained plugin-guidance repair for existing users, with no new operational duties or migration. Consumers can take the new version without rewriting their state."
  route: [shape, build, verify-deliver]
  obligations:
    architecture: ["Preserve the existing selection conversation and profile receipt as the authority; distinguish future product ambition from the accepted next commitment."]
    implementation: ["Revise the smallest necessary selection wording, examples, and existing receipt handoff; consumers upgrade by taking the new version without a migration."]
    testing: ["Exercise unproved integration, scaffolding, explicit operated release, and existing-consumer cases with falsifiable evidence; retain instruction and contract checks."]
  scope_boundary: "Only the accepted issue correction and its necessary evidence; no new operating commitment, workflow machinery, consumer migration, or new experiment."
  promote_when:
    - "A consumer must migrate, reconfigure, or rewrite records to upgrade."
    - "The scope accepts production data, destructive mutation, unattended operations, or new recovery/support responsibilities."
  decision:
    authority: "Captain Kent"
    at: "2026-09-10T09:06:26.340161Z"
```

The decision timestamp is capture time. In this Kathmandu session the Captain approved the maintenance delivery sequence with "確認，就這樣交付", then explicitly selected Pilot for both issue #393 and issue #396 with "Pilot可以". This records those scope and profile decisions, not review of a later implementation. The GitHub issue is provenance; this standalone brief has no Planning Receipt or provider scheduling claim.

## Acceptance criteria

- **AC-1**: The recommendation states the next commitment, unresolved assumption, observable result, and concrete included work; it distinguishes scaffolding, a disposable integrated experiment, limited real use, and an operated release.
- **AC-2**: When the first user journey is unproved and Production is recommended, the explanation offers the smallest lower-commitment alternative and identifies the evidence or explicit operational duty that makes it insufficient.
- **AC-3**: Existing valued state and consumers are distinguished from state an experiment might create; a new repository neither forces POC nor justifies Production by itself.
- **AC-4**: The Captain's accepted scope carries into the existing profile receipt, and a misunderstood or unanswered scope stays unresolved instead of becoming an automatic selection or retrospective success claim.
- **AC-5**: Representative scenario evidence tests both lower-commitment and valid Production cases; affected existing contract and instruction-budget checks pass, with no additional standing process or consumer migration.
