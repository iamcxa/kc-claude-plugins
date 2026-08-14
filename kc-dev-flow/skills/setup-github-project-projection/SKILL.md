---
name: setup-github-project-projection
description: Install, dry-run, audit, or update a deterministic one-way projection from one commissioned Spacedock workflow into GitHub Issues and one GitHub Project. Use when a repository needs SD state visible in GitHub without making GitHub lifecycle authority, when checking an installed projection, or when reviewing the target files and external mutation plan before apply.
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
- **apply** — only after a reviewed dry-run and separate bounded approval for the
  named repository, Project, entities, credential, and mutation subset.

An update is `install` against an existing target: show the byte diff and replace
only accepted files. Do not maintain a second upgrade mode.

## Plan and install

1. Pin the repository, workflow directory, trunk commit, state ref and commit,
   Project owner/number/ID, mapping profile, and freshness window.
2. Run local capability discovery against the pinned workflow README and entity
   bytes. Unknown fields remain unmapped; missing optional profile fields produce
   partial projection rather than suppressing Issue identity.
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

6. Re-run audit from the installed target. Refuse external apply when any pinned
   input or installed byte digest differs from the reviewed plan.

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
`--enable-external-apply`. Secret creation remains a separate host operation;
the installer accepts no token value.

The deterministic projector lives at
[`assets/project-spacedock-state.py`](assets/project-spacedock-state.py). Keep
file installation separate from its GitHub adapter so a local dry-run never
inherits network authority.

## Runtime boundary

The installed default-branch workflow uses one reconcile path:

- `workflow_dispatch` is the explicit fast path after a successful state push;
- `schedule` is the convergence and liveness safety net;
- both check out exact trunk and state commits and invoke the same vendored
  projector;
- overlapping writes serialize with `cancel-in-progress: false`.

The repository `GITHUB_TOKEN` owns same-repository Issue writes. A dedicated,
named secret owns Project writes only after token type, minimum permissions,
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
receipt-bearing repository Issues are rediscovered even when Project item
creation did not finish, and a rerun converges through the same plan.

## Receipts and refusal

Manage only Issue blocks and Project fields carrying this projector's qualified
identity receipt. A title match is not ownership. Never change a receipt-less
Project item unless an entity explicitly links its Issue and the dry-run labels
the resulting ownership `linked`.

Refuse or quarantine:

- duplicate qualified identities or Issue references;
- unknown stages, malformed receipts, or pinned-input drift;
- deletion without an `_archive/` tombstone;
- unsupported Project fields or credentials;
- apply when the reviewed plan digest is stale.

Do not write projection receipts back to the state branch. Do not infer Priority,
Size, Estimate, Cycle, dates, product, or sprint semantics.

## POC boundary

Local deterministic fixtures prove mapping, no-op convergence, freshness
decisions, and archive ownership before any external write. Disabled-schedule,
invalid-token, and live archive procedures remain production-readiness evidence,
not prerequisites for the local POC. This boundary does not remove the installed
schedule or archive contract. The POC does not yet persist the last-successful
timestamp needed for a decaying liveness signal; do not present the configured
schedule alone as liveness evidence.
