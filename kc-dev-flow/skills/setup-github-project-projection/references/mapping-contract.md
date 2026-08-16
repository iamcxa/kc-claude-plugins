# Spacedock to GitHub mapping contract

## Authority

Spacedock owns entity identity and lifecycle. Project Drafts, explicitly linked
GitHub Issues, and projector-created fields are derived views. GitHub-owned Priority, Size,
Estimate, and Iteration never flow back or become projection inputs.

## Generic source

Read stages from the selected commissioned workflow README. Require exactly one
initial and one terminal stage. The stable entity baseline is slug, optional
non-empty ID, title, status, and source. Treat score, dates, Issue/PR references,
and workflow-specific fields as optional. Never publish worktree paths.

One installed configuration selects one workflow and one Project. Therefore the
generic Project schema creates `SD Stage` and `SD Identity`; it does not need
`SD Workflow`.
Map the initial stage to GitHub Status `Todo` (fall back to `Backlog` only when
that is the available option), the terminal stage to `Done`, and other stages to
`In Progress` only when those options exist. Exact `SD Stage` remains the
lossless lifecycle view.

`SD Stage` and `SD Product` are single-select fields so Project views can group
and chart them. `SD Identity` is a text field containing the full qualified
identity for exact matching and operator inspection; it is not a chart
dimension. Installation creates missing fields from observed source values.
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

Primary identity is `<repository>:<workflow-dir>:<slug>`. Store it in the
Project text field `SD Identity` and in the hidden Draft receipt. Store optional
entity ID only as a secondary key.

Render projector-owned Drafts for people first:

- title: `[{short-id}] {entity title}`; use the Spacedock short-ID rule for the
  workflow ID style, including shortest-unique `sd-b32` prefixes across active
  and archived entities;
- body: the entity Markdown after frontmatter, followed only by the hidden
  receipt; never expose frontmatter, worktree paths, or a visible metadata
  summary;
- Project fields: lifecycle and machine identity metadata.

The v2 receipt records pinned commits, entity digest, projector version and byte
digest, ownership, and archive state. Normalize the rendered entity Markdown to
LF with one terminal newline. Projector-owned title and body are derived bytes,
not a second content authority.

- `projector`: the projector may manage Draft title, body, and Project fields.
- `linked`: require a reviewed full `owner/repo#number` binding; preserve every
  human Issue byte and manage only projector-owned Project fields.
- receipt-less and field-less: foreign.

Discover managed Drafts from `SD Identity` and the receipt. A v2 projector-owned
Draft normally requires receipt and field agreement. One unique trusted
same-scope v2 receipt may restore only a missing `SD Identity` field after an
interrupted cross-API apply. A missing receipt, field-only identity,
disagreement, duplicate, or out-of-scope receipt reports a conflict and cannot
cause `CREATE`.

During Issue-to-Draft migration, a legacy Issue qualifies as a residue only
when its v2 receipt and `SD Identity` agree and the author is
`github-actions[bot]`. Any weaker candidate fails closed. Cleanup is attended,
never scheduled, and requires a durable `Issue number -> slug -> SD Identity`
journal plus immediate ownership and zero-comment rechecks before deletion.

## Classification

- `CREATE`: no matching managed Draft/item exists.
- `UPDATE`: managed values differ from desired values.
- `NO_CHANGE`: desired and managed values are identical.
- `PARTIAL`: identity remains projectable but optional profile inputs are absent.
- `CONFLICT`: applying would require guessing identity, lifecycle, or authority.

For projector-owned Drafts, identical managed inputs and observed target state
produce zero mutations; differing title or body bytes are restored from SD. For
linked Issues, equality covers Project membership and managed Project fields;
human Issue title, body, state, and labels are not desired values and are never
PATCHed.
Human-owned Project fields and repository labels outside the desired managed set
do not participate in the equality check and remain untouched.

## Freshness and archive

Compare per-entity content digest for item freshness. An unrelated state commit
does not make every item stale. The POC exposes deterministic current/stale clock
decisions but does not yet persist or display a timestamped last-successful
reconcile receipt. That liveness integration remains production-readiness work;
never substitute a frozen per-item `Current` field.

An `_archive/` tombstone marks a projector-owned Draft complete and must preserve
a linked Issue. Retain the Project item with explicit terminal/archive receipt
state. A managed item whose source disappears without a tombstone is a conflict,
not implicit completion.

## Credential boundary

Use the repository token only to read same-repository linked or legacy Issues.
Use a separately named Project token for Draft, item, and field observation and
mutation. The current REST
2026-03-10 user-Project [item](https://docs.github.com/en/rest/projects/items)
and [field](https://docs.github.com/en/rest/projects/fields?apiVersion=2026-03-10)
endpoints do not accept fine-grained PATs or GitHub App tokens; the user-owned
adapter therefore remains unarmed until a classic PAT's expiry, rotation owner,
and fallback blast radius are explicitly accepted.
Never copy the operator's ambient `gh` authentication into a repository secret.

## Approval envelope

External apply requires one default-branch envelope. `selected` scope names a
non-empty dogfood subset and suppresses workflow-global orphan conclusions.
`workflow` scope covers every valid entity under the one commissioned workflow.
Both pin repository, workflow, state ref, Project identity, mapping policy,
installed projector digest, linked-Issue bindings, expiry, and a positive
per-run mutation cap. The approval must expire no later than its credential.
State commit and entity lifecycle changes remain projection provenance; they do
not invalidate workflow-scope approval.

All validation and write counting finish before the first mutation. Completed
responses append to the run journal. Transient REST failures use bounded retry
and bounded `Retry-After`; conflicts, stale approval, schema drift, or an
exceeded mutation cap fail closed.
