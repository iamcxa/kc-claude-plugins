---
name: setup-github-project-projection
description: Install, dry-run, audit, or update a deterministic one-way projection from one commissioned Spacedock workflow into GitHub Project Draft items, with optional explicit links to existing Issues. Use when a repository needs SD state visible in GitHub without making GitHub lifecycle authority, when checking an installed projection, or when reviewing the target files and external mutation plan before apply.
---

# Setup GitHub Project Projection

Project one selected Spacedock workflow into one selected GitHub Project. Keep
Spacedock authoritative; treat every GitHub value as derived and receipt-bound.

## Read the contract

Read [`references/mapping-contract.md`](references/mapping-contract.md) before
planning or installing. Read no kc-dev-flow-specific profile assumptions when
the selected workflow is generic.

## Select a mode

- **plan** — default; discover capabilities and render file plus external
  mutations without writing either target.
- **install** — after explicit file authority, vendor the reviewed workflow,
  config, and exact projector bytes. Installation is still dry-run for external
  GitHub mutations.
- **audit** — compare installed byte digests and configuration with the selected
  workflow and Project; report drift without repair.
- **apply** — only through an installed, expiring approval envelope. Dogfood
  approval names a non-empty entity subset; production approval covers the one
  commissioned workflow.

An update is `install` against an existing target: show the byte diff and replace
only accepted files. Do not maintain a second upgrade mode.

## Plan and install

1. Pin the repository, workflow directory, state ref, Project owner/number/ID,
   mapping profile, installed projector digest, approval expiry, credential
   expiry, and per-run mutation cap. State commits are provenance, not a static
   allowlist.
2. Run local capability discovery against the pinned workflow README and entity
   bytes. Unknown fields remain unmapped; missing optional profile fields produce
   partial projection rather than suppressing Project identity.
3. Run the vendored deterministic planner. A local approval is valid only when
   the planner digest equals the bytes proposed for the target repository.
4. Present two plans separately: target file changes and external GitHub
   mutations. Default both to no-write. Never copy an ambient local `gh` token.
5. On approved install, vendor exactly:

   ```text
   .github/workflows/spacedock-project-sync.yml
   .github/spacedock-project.json
   .github/scripts/project-spacedock-state.py
   ```

6. Re-run the local byte audit from the installed target. It proves only that
   the installed files match the proposed package; runtime separately validates
   the envelope, default-branch config, live Project identity, and observations.

Use the packaged installer for the file transaction. Its default `plan` and
`install` modes leave `external_apply_enabled` false and never mutate GitHub:

```bash
python3 assets/install-projection.py plan \
  --target /absolute/target/repository \
  --repository OWNER/REPO \
  --workflow-dir docs/dev \
  --state-ref spacedock-state/dev \
  --profile generic \
  --project-owner-type user \
  --project-owner OWNER \
  --project-number NUMBER \
  --project-id PROJECT_NODE_ID
```

After review, repeat with mode `install`, then repeat with mode `audit`. To arm
external apply, the reviewed install must additionally name token type,
credential expiry, rotation owner, fallback blast radius, and
`--approval-expiry`, `--approval-scope`, `--max-mutations-per-run`, and
`--enable-external-apply`. Selected scope also requires at least one `--entity`.
Workflow scope allows all valid entities under the commissioned workflow.
Approve an explicit human Issue only with a reviewed full binding such as
`--linked-issue task-slug=OWNER/REPO#123`. Secret creation remains a separate
host operation; the installer accepts no token value.

The deterministic projector lives at
[`assets/project-spacedock-state.py`](assets/project-spacedock-state.py). Keep
file installation separate from its GitHub adapter so a local dry-run never
inherits network authority.

## Runtime boundary

The installed default-branch workflow uses one reconcile path:

- `workflow_dispatch` is the explicit fast path after a successful state push;
- `schedule` is the convergence and liveness safety net;
- both check out the exact default-branch event SHA and the configured state ref,
  then invoke the same vendored projector;
- overlapping writes serialize with `cancel-in-progress: false`.

The repository `GITHUB_TOKEN` only reads same-repository Issues for explicit
links. A dedicated, named secret owns Project Draft, item, and field writes only
after token type, minimum permissions,
expiry, and rotation/revocation owner are recorded. The REST 2026-03-10 adapter
for a user-owned Project requires a classic PAT; GitHub documents those user
Project [item](https://docs.github.com/en/rest/projects/items) and
[field](https://docs.github.com/en/rest/projects/fields?apiVersion=2026-03-10)
endpoints as unsupported for fine-grained PATs and GitHub App tokens. Treat that
blast radius as an explicit captain decision, not an installer default.
Organization-owned Projects may select a narrower token only after a live
preflight proves the chosen endpoints. Preflight both authorities before the
first mutation.

The workflow remains a read-only projection dry-run until the reviewed config
sets `external_apply_enabled` true. A successful partial sequence is resumable:
receipt-bearing Draft items are rediscovered when a later field write did not
finish, and a rerun converges through the same plan.

Before arming apply, attended setup must provision `SD Identity` as text plus
`SD Stage` and any profile field as single-select with every required option.
Steady-state reconcile validates that schema and fails before its first write;
it never creates fields or changes option sets.

Before the first write, runtime validates the approval scope and expiry, requires
expiry no later than the credential expiry, compares the installed projector
SHA-256 with the reviewed digest, validates every full linked-Issue binding, and
counts all planned writes against the fail-closed cap. Each completed response
is appended to the run journal so a partial failure remains actionable.

## Receipts and refusal

Discover projector-created Drafts from the `SD Identity` Project text field and
hidden receipt. The two anchors must agree; one unique receipt may restore a
missing field after an interrupted Draft-to-field write. A field without a
receipt, disagreement, or duplicate is a conflict. An explicitly linked human
Issue must match its reviewed `owner/repo#number` binding; never PATCH its title,
body, state, or labels. Only add it to the Project when needed and manage
projector-owned Project fields.

For projector-owned Drafts, render `[{short-id}] {title}` and copy only the
entity Markdown after frontmatter into the visible body. Keep lifecycle and
identity metadata in Project fields. These title and body bytes are a derived
view: an edit on a projector-owned Draft is overwritten from SD on the next
successful reconcile and never becomes SD input. Linked Issue bytes remain
human-owned.

Refuse or quarantine:

- duplicate qualified identities or Issue references;
- missing v2 receipts, disagreeing or duplicate anchors, field-only identities,
  non-Draft identity anchors, or receipt-only candidates outside the selected
  scope;
- unknown stages, malformed receipts, or pinned-input drift;
- source disappearance without an `_archive/` tombstone;
- unsupported Project fields or credentials;
- apply when the approval expired, its projector digest differs, or its mutation
  cap would be exceeded.

Do not write projection receipts back to the state branch. Do not infer Priority,
Size, Estimate, Cycle, dates, product, or sprint semantics.

## POC boundary

Local deterministic fixtures prove mapping, production reconcile convergence,
scope and expiry refusal, no-op reruns, retry bounds, mutation-cap refusal,
receipt trust, and archive ownership before any external write. Disabled-
schedule, invalid-token, and live archive procedures remain production-readiness
evidence, not prerequisites for the local POC. The versioned reconcile result is
the projection runtime artifact; status metrics and prose belong to the sibling
status-update feature. Do not present the configured schedule alone as liveness
evidence.
