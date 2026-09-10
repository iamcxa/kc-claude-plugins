---
title: "fix(kc-dev-flow): make retained architecture explanations discoverable"
status: backlog
product: kc-dev-flow
sprint: S7
sprint-readiness: ready
issue: iamcxa/kc-claude-plugins#396
provenance: https://github.com/iamcxa/kc-claude-plugins/issues/396
id: m0e43swm7wrs71xy98ea43gp
started: 2026-09-10T09:09:43Z
gates:
    version: 1
    records:
        - id: gate:m0e43swm7wrs71xy98ea43gp:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:m0e43swm7wrs71xy98ea43gp-backlog-1
              briefing:
                id: briefing:m0e43swm7wrs71xy98ea43gp:backlog:attempt-1:revision-1
                digest: sha256:31e8caf4368d8f332b6fadbdecd3dbdac9c63b80def6e5cf14105656a540336b
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:m0e43swm7wrs71xy98ea43gp:backlog:1
                briefing: briefing:m0e43swm7wrs71xy98ea43gp:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T09:13:27.58782Z"
                decision: approve
                reason: Captain Kent approved these issue repairs with "確認，就這樣交付" and selected Pilot for both with "Pilot可以". This initial admission records that existing scope/profile decision after publishing its administrative brief; it grants shape only and does not claim approval of a later implementation or future evidence.
              application:
                target-stage: ideation
                state: pending
---

The selected route identifies one discoverable home for the architecture explanation before implementation, and retained documentation describes implemented behavior at the existing exit boundary.

## Development Brief

### Problem

A retained implementation can pass reviews while its architecture is discoverable only by reading code and a long work history. Current context-maintenance guidance does not clearly cover the initial, proportional architecture explanation.

### Accepted outcome

The selected route identifies one discoverable home for the architecture explanation before implementation, and retained documentation describes implemented behavior at the existing exit boundary.

### Non-goals

- No new stage, gate, architecture reviewer, documentation generator, mandatory diagram tool, second context authority, roadmap, or status file.
- No mandatory completed architecture before an experiment answers its question; no speculative designs or mutable progress in retained architecture documentation.
- No reopening completed work, forced ARCHITECTURE.md when an existing authoritative section suffices, or boilerplate edits to unchanged accurate documentation.
- No implementation changes in the originating product, new operating guarantees, consumer migration, or self-improvement experiment.

### Route-back conditions

Return to the Captain if the correction requires a new authority, gate, mandatory tool, schema, consumer migration, retrospective work, or a broader operating commitment; ask separately before unapproved external proof spend.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: "A bounded retained plugin-guidance repair for existing users, with no new operational duties or migration. Consumers can take the new version without rewriting their state."
  route: [shape, build, verify-deliver]
  obligations:
    architecture: ["Use the existing bound project-context authority and its linked architecture home; reuse project-context maintenance and retained-document policy."]
    implementation: ["Update the smallest necessary adoption, brief, and selected-stage guidance; allow existing accurate linked explanations without duplicate files or retrospective work."]
    testing: ["Exercise disposable and retained POCs, existing linked architecture, changed persistence/API boundaries, and unchanged documentation, with code or command evidence appropriate to the claim."]
  scope_boundary: "Only the accepted issue correction and its necessary evidence; no new operating commitment, workflow machinery, consumer migration, or new experiment."
  promote_when:
    - "A consumer must migrate, reconfigure, or rewrite records to upgrade."
    - "The scope accepts production data, destructive mutation, unattended operations, or new recovery/support responsibilities."
  decision:
    authority: "Captain Kent"
    at: "2026-09-10T09:06:31.121677Z"
```

The decision timestamp is capture time. In this Kathmandu session the Captain approved the maintenance delivery sequence with "確認，就這樣交付", then explicitly selected Pilot for both issue #393 and issue #396 with "Pilot可以". This records those scope and profile decisions, not review of a later implementation. The GitHub issue is provenance; this standalone brief has no Planning Receipt or provider scheduling claim.

## Acceptance criteria

- **AC-1**: A disposable POC can use a small Exploration Brief outline covering components, data flow, external boundaries, and tentative assumptions, without a permanent documentation set.
- **AC-2**: A retained POC has a repository entry point linked from its bound context or README, explaining retained components and responsibilities, inputs/outputs, persistence/source-of-truth boundaries, important package roles, and relevant code or commands.
- **AC-3**: Pilot and Production extend that explanation only for applicable authorization, deployment, failure, recovery, and compatibility boundaries; an existing accurate linked section satisfies the requirement without a duplicate file.
- **AC-4**: The explanation's home is identified before implementation, in build for a POC without shape, and changed implemented claims are aligned before the existing implementation/validation boundary using the existing maintenance policies.
- **AC-5**: Scenario evidence covers the issue's five acceptance examples, traces retained claims to implementation, and proves unchanged accurate documentation needs no extra edit or review loop; affected existing contract and instruction-budget checks pass.
