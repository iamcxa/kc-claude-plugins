# Migrating from 2.x

The profile-native contract is a breaking upgrade. The installed skills and an
adopter's vendored workflow must move in one coordinated cutover. A new
`continue-dev-flow` correctly fails closed when the local profile loader,
profile contracts, or v2 work-item receipt are absent; it does not fall back to
the installed package or silently run the 2.x workflow.

## Core differences

| 2.x adopter | Profile-native adopter |
|---|---|
| A workflow README and its stage-selected mods carry most policy. | `## Local Profile` locates a repository loader; it emits only the shared core, selected profile base, and current stage. |
| Normal and defect routes share one lifecycle. | Each work item selects POC, Pilot, or Production and may coexist with other profiles in the same repository. |
| A v1 or prose profile choice may inform work without driving a loader. | A hash-bound `kc-dev-flow-work-profile/v2` receipt is required before the first working stage. |
| Fresh EM or cross-model review may act as a general gate. | Named owners and deterministic checks hold scoped gates; Chief Engineer and Science Officer load only on their triggers. |
| Work-control prose may combine review and delivery controls. | Build emits one proportional typed observation; delivery and local controls remain with their providers. |
| Production release may share the normal terminal path. | Production has an explicit `release` stage; POC and Pilot skip it without placeholder work. |

## Safe cutover

1. Prepare the adopter refit before updating the installed plugin. Do not run
   ordinary continuation while one side is new and the other is still 2.x.
2. Audit existing project, work-item, iteration, execution-state, delivery,
   scope, gate, and observation authorities. Preserve their working owners.
3. Add the loader and contracts root to a concise `## Local Profile`. Vendor the
   shared core, profile tree, loader, and conditional references byte-for-byte.
4. Map POC, Pilot, and Production onto the existing runtime. Prove inactive
   stages can be skipped and the Production release boundary is representable.
5. Migrate work-item receipts at a stage boundary:
   - leave completed and archived items unchanged;
   - select a profile when a backlog item first enters work;
   - mechanically convert v1 when its basis is unchanged;
   - mechanically encode an older explicit Captain choice only when the exact
     item records the selected profile, its authority, and an unchanged basis;
     otherwise ask for a new selection.
6. Preserve extra local terminal states only through an explicit mapping. A
   state such as a finding-only terminal does not automatically join every
   profile route; an unrepresentable transition is a refit requirement.
7. Retire old source mods by disposition. Keep provider mods and unmatched
   repository controls local instead of deleting them or copying them into the
   shared core. Preserve `retained-document-policy.md` and
   `project-context-maintenance.md` as conditional references; bind their
   retained-document and project-context triggers instead of loading either as
   standing policy.
8. Run every profile-stage loader combination, prove unselected contracts are
   absent, exercise runtime skips, and run the repository's normal gates. Merge
   the adopter refit before updating the installed plugin used for continuation.

## Decisions that remain local

The upgrade does not decide whether an adopter keeps a mandatory EM or
cross-model gate, how a custom terminal state closes, whether RoboRev is
available, or how its PR and state-holder providers operate. Present changes to
those authority and proof semantics explicitly; do not hide them inside a
mechanical re-vendor.
