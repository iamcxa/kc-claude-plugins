# Adopt the SD workflow

Use this reference from `kc-dev-flow-2:dev` when adoption is absent or incompatible.
Invoke `spacedock:commission` for a new workflow, or `spacedock:refit` to review an
existing one. This reference supplies design inputs, not an alternate setup CLI.
Reuse the user's established selection; obtain approval for concrete configuration
changes before activating dispatch. Do not run commission's pilot automatically
as part of installing this package.

## Resolve and propose

Resolve the absolute code root, target workflow directory, installed dev2 package,
activated SD plugin root and executable version. Read project conventions, live
workflows, task ownership and delivery authority. Existing work remains on its
recorded workflow/variant/profile. A profile change requires a reviewed route
and migration decision; do not move tasks or overwrite custom mods implicitly.

Use the [workflow source](workflow.md) as the commission input. SD advances along
ordered stage definitions; a profile field does not branch that graph. Adopt only
the route currently needed:

| Selected profile | Workflow directory example | Source adaptation |
| --- | --- | --- |
| `poc` | `docs/dev2-poc` | Generated, never hand-edited: `scripts/poc_readme.py derive` removes the ideation state entry and the `### ideation` section; backlog, implementation, validation and done stay byte-identical |
| `pilot` or `prod` | `docs/dev2` | Keep the source's five stages; profile selects skill references per task |

Maintain one README by hand. When both routes are adopted, commission or refit the
five-stage README first, then regenerate the POC README from it:
`python3 {package}/scripts/poc_readme.py derive docs/dev2/README.md > docs/dev2-poc/README.md`.
When only POC is adopted, derive from this package's [workflow source](workflow.md)
and resolve its template values the same way. After any change to the five-stage
README, regenerate; `poc_readme.py check docs/dev2-poc/README.md docs/dev2/README.md`
exits 1 with the drift as a diff.

Both routes preserve backlog/validation gates, implementation/validation
`worktree: true`, fresh validation and `feedback-to: implementation`. Copy the
source into the approved workflow's `README.md`, resolve template values and
project trunk and ID policy, and stamp commissioning metadata through SD's existing
procedure. The source uses slug IDs; commission may propose its collaborative
SD-B32 ID policy. Preserve an existing workflow's approved ID style.
Stage prose calls exact `kc-dev-flow-2:` skills; `context-sections` carries shared
disposition/delivery rules. Do not introduce unsupported `stage.skill` fields or
profile-conditioned transitions. Check profile/graph compatibility before new
work or resume dispatch; a mismatch holds the affected action for the user.

## State and delivery setup

Use commission's split-root journey for a shipping code repository: state stays
in the workflow's ignored `.spacedock-state` linked checkout, code changes in the
task worktree, and the workflow README/mods on the code branch. Choose distinct
workflow basenames and state branches (`spacedock-state/dev2-poc` versus
`spacedock-state/dev2` above); inspect existing branches before creating anything.
Keep both state paths and `.worktrees/` ignored. Preserve existing state layout
unless an explicit migration is approved. Pass the absolute workflow directory
to `spacedock state init`/`ready`, status, gate, dispatch and merge operations.

For PR delivery, have commission install `{active-sd-root}/mods/pr-merge.md` into
`{workflow-dir}/_mods/pr-merge.md`. Copy the activated source unchanged, not a
vendored dev2 copy or an arbitrary cache version. Record/check its own metadata
and bytes; mod version and plugin version need not match (the inspected SD 0.27.3
package ships pr-merge 0.27.0). Refit compares existing customizations for approval.
The workflow's Delivery authority constrains the upstream mod's local fallback,
trunk push and non-Draft defaults. Preserve project Draft/CI/manual merge rules;
installing the mod does not grant those actions or mechanically enforce them.

## Before activation

Review the concrete README, state mapping, exact stage-skill availability and
copied mod with the user. Run SD state readiness and status validation using the
explicit directory. Run `spacedock status --workflow-dir <absolute-dir> --boot` and confirm
`merge: pr-merge` in its MODS report; file existence alone is insufficient. A model-free
synthetic copy can exercise `merge guard` to confirm `armed` / `invoke-hook` /
`pr-merge`; do not run a guard against a real task as an installation probe.
Missing hook, incompatible graph, missing skill or unresolved authority holds
activation. Once approved, hand the same project/workflow/task binding to FO;
normal SD dispatch and gate lifecycle take over.

The source-repository `test_sd_dispatch.py --sd-plugin-root <active-sd-root>`
checks both adapted graphs, copied canonical mod registration and split-root
worktree handoff in disposable repositories. Synthetic gate decisions are test
inputs, not user approval. It does not execute models, hook bodies or remote PR
operations. A real adopting project still needs its own reviewed configuration;
passing this test does not activate it or prove the project's remote delivery.
