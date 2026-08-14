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
Project text field `SD Identity` and in the hidden Issue receipt. Add the
repository label `spacedock:managed` to projector-owned Issues without replacing
any existing label. Store optional entity ID only as a secondary key.

Render projector-owned Issues for people first:

- title: `[{short-id}] {entity title}`; use the Spacedock short-ID rule for the
  workflow ID style, including shortest-unique `sd-b32` prefixes across active
  and archived entities;
- body: the entity Markdown after frontmatter, followed only by the hidden
  receipt; never expose frontmatter, worktree paths, or a visible metadata
  summary;
- Project fields and the managed label: lifecycle and machine identity metadata.

The receipt records the normalized body digest in addition to pinned commits,
entity digest, projector version and byte digest, ownership, and archive state.
Normalize CRLF and CR to LF and use exactly one terminal newline before hashing.

- `projector`: the projector may manage Issue open/closed state.
- `linked`: require a reviewed full `owner/repo#number` binding; preserve every
  human Issue byte and manage only projector-owned Project fields.
- receipt-less and field-less: foreign unless it carries `spacedock:managed`;
  a label-only managed candidate is a conflict that blocks duplicate creation.

Discover managed candidates from the union of `SD Identity`, receipt, and
`spacedock:managed`. A missing field or missing receipt is repairable when the
remaining anchor identifies exactly one Issue and the body is safe. If field and
receipt disagree, or either anchor is duplicated, report a conflict. Deleting
one signal must never cause `CREATE`.

## Classification

- `CREATE`: no matching managed Issue/item exists.
- `UPDATE`: managed values differ from desired values.
- `NO_CHANGE`: desired and managed values are identical.
- `PARTIAL`: identity remains projectable but optional profile inputs are absent.
- `BODY_DRIFT`: a projector-owned body differs from its recorded normalized
  digest; preserve the Issue bytes and continue planning other entities.
- `CONFLICT`: applying would require guessing identity, lifecycle, or authority.

For projector-owned Issues, identical managed inputs and observed target state
produce zero mutations. For linked Issues, equality covers Project membership
and managed Project fields; human Issue title, body, and state are not desired
values and are never PATCHed.
Human-owned Project fields and repository labels outside the desired managed set
do not participate in the equality check and remain untouched.

Legacy visible-summary Issues may migrate in place only when their body matches
the recognized projector-summary shape. A legacy receipt attached to any other
body is `BODY_DRIFT`, because the old receipt has no digest proving ownership of
those bytes.

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
