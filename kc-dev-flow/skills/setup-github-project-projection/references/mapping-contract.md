# Spacedock to GitHub mapping contract

## Authority

Spacedock owns entity identity and lifecycle. GitHub Issues, Project items, and
projector-created fields are derived views. GitHub-owned Priority, Size,
Estimate, and Iteration never flow back or become projection inputs.

## Generic source

Read stages from the selected commissioned workflow README. Require exactly one
initial and one terminal stage. The stable entity baseline is slug, optional
non-empty ID, title, status, and source. Treat score, dates, Issue/PR references,
and workflow-specific fields as optional. Never publish worktree paths.

One installed configuration selects one workflow and one Project. Therefore the
generic Project schema creates only `SD Stage`; it does not need `SD Workflow`.
Map the initial stage to GitHub Status `Backlog`, the terminal stage to `Done`,
and other stages to `In progress` only when those options exist. Exact `SD Stage`
remains the lossless lifecycle view.

`SD Stage` and `SD Product` are single-select fields so Project views can group
and chart them. Installation creates missing fields from observed source values.
When a later source value needs a new option, the runtime reports
`UPDATE_FIELD_OPTIONS` and refuses apply. Updating an existing option set remains
a separately reviewed operator action because replacing the set may invalidate
existing option identities.

## kc-dev-flow profile

When selected explicitly:

- map non-empty `product` to `SD Product`;
- keep `sprint` and Milestone writes deferred until separately enabled;
- allow absent product or sprint and report `PARTIAL`;
- never map sprint to GitHub Project Iteration.

## Identity and ownership

Primary identity is `<repository>:<workflow-dir>:<slug>`. Store optional entity
ID only as a secondary key. Every receipt records pinned commits, entity digest,
projector version and byte digest, ownership, and archive state.

- `projector`: the projector may manage Issue open/closed state.
- `linked`: preserve the human Issue title and open/closed state; manage only the
  receipt block and projector-owned Project fields.
- receipt-less: foreign; report and leave unchanged unless the SD entity carries
  the exact Issue reference selected in the reviewed plan.

## Classification

- `CREATE`: no matching managed Issue/item exists.
- `UPDATE`: managed values differ from desired values.
- `NO_CHANGE`: desired and managed values are identical.
- `PARTIAL`: identity remains projectable but optional profile inputs are absent.
- `CONFLICT`: applying would require guessing identity, lifecycle, or authority.

Identical inputs and observed target state must produce zero mutations.
Human-owned Project fields outside the desired `SD *` set do not participate in
the equality check and remain untouched.

## Freshness and archive

Compare per-entity content digest for item freshness. An unrelated state commit
does not make every item stale. The POC exposes deterministic current/stale clock
decisions but does not yet persist or display a timestamped last-successful
reconcile receipt. That liveness integration remains production-readiness work;
never substitute a frozen per-item `Current` field.

An `_archive/` tombstone may close a projector-owned Issue and must preserve a
linked Issue. Retain the Project item with explicit terminal/archive receipt
state. A managed item whose source disappears without a tombstone is a conflict,
not implicit completion.

## Credential boundary

Use the repository token only for same-repository Issues and a separately named
Project token only for Project observation and mutation. The current REST
2026-03-10 user-Project [item](https://docs.github.com/en/rest/projects/items)
and [field](https://docs.github.com/en/rest/projects/fields?apiVersion=2026-03-10)
endpoints do not accept fine-grained PATs or GitHub App tokens; the user-owned
adapter therefore remains unarmed until a classic PAT's expiry, rotation owner,
and fallback blast radius are explicitly accepted.
Never copy the operator's ambient `gh` authentication into a repository secret.
