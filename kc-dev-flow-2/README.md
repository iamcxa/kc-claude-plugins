# Dev-flow 2

An optional experimental alternative to kc-dev-flow. It provides a thin
start/resume entry, profile principles, stage skills, retained advisory roles,
read-only routing lint, and an adoptable Spacedock workflow with a POC adaptation.
Existing kc-dev-flow projects stay on their selected variant; this package does
not migrate them automatically or claim full safeguard parity or a one-third
size reduction. Local learning evaluation produces proposals only; there is no
custom runtime loader, installed hook, background launcher or automatic adoption.

## Controlled trial

This candidate includes Claude Code and Codex manifests. Its 0.1.0 metadata
bootstraps the repository's new-component policy; no released tag exists yet.
Use a reviewed checkout for a controlled local trial. For Claude Code, launch
from the intended project with the checkout's absolute package path:

```sh
claude --plugin-dir /absolute/path/to/kc-claude-plugins/kc-dev-flow-2
```

Then invoke `/kc-dev-flow-2:dev`. This is a local package trial, not a published
marketplace release.

For Codex, the marketplace path below is the reviewed **repository root**, not
its `kc-dev-flow-2` subdirectory. Preserve an existing installation; install and
remove only when this trial owns that local plugin change:

```sh
codex -c 'marketplaces.kc-claude-plugins.source_type="local"' \
  -c 'marketplaces.kc-claude-plugins.source="/absolute/path/to/kc-claude-plugins"' \
  plugin add kc-dev-flow-2@kc-claude-plugins

codex -C /absolute/path/to/project \
  -c 'marketplaces.kc-claude-plugins.source_type="local"' \
  -c 'marketplaces.kc-claude-plugins.source="/absolute/path/to/kc-claude-plugins"' \
  -c 'plugins.kc-dev-flow-2@kc-claude-plugins.enabled=true'

# After the trial, remove the plugin installed for this trial.
codex -c 'marketplaces.kc-claude-plugins.source_type="local"' \
  -c 'marketplaces.kc-claude-plugins.source="/absolute/path/to/kc-claude-plugins"' \
  plugin remove kc-dev-flow-2@kc-claude-plugins
```

In the fresh Codex session, request `kc-dev-flow-2:dev` by its exact name. The
commands use per-invocation marketplace overrides; plugin installation itself
persists locally until removed. Bare `/dev`, entry execution and role behavior
remain unproven. Earlier installation/discovery checks found seven skills before
the Engineering Reviewer rename; see [validation scope](VALIDATION.md) for the
historical evidence and its limits.

Spacedock's plugin and CLI are required for orchestration. A project must have an
explicitly selected experimental variant/profile and an approved workflow before
stage work. Follow the [SD adoption reference](references/sd/adoption.md) through
SD commission/refit; invoking the entry does not rewrite a project workflow.

## Entry

Use [`kc-dev-flow-2:dev`](skills/dev/SKILL.md) to start or resume work. It resolves
the explicit project/workflow/task and approved selection, then hands orchestration
to `spacedock:first-officer`. Stage skills keep their own profile routes; the entry
does not migrate existing work or duplicate SD's control loop. Claude plugin skills
use `/kc-dev-flow-2:dev`, not a bare `/dev`; Codex shorthand resolution remains
unverified. Earlier six-skill model reads and later seven-skill discovery do not
prove the new entry executes correctly.

## Framework

The First Officer (FO) recommends a profile, records the user's selection and
variant `kc-dev-flow-2` in the work item, aligns the outcome, and orchestrates.
Spacedock (SD) retains stage state, dispatch, reports, gates, feedback and recovery.
A stage skill defines how its selected profile performs work; it does not
advance state, create authority or substitute for an approval.

| Profile | Intended SD route |
| --- | --- |
| [poc](references/profiles/poc.md) | backlog -> implementation -> validation -> done |
| [pilot](references/profiles/pilot.md) | backlog -> ideation -> implementation -> validation -> done |
| [prod](references/profiles/prod.md) | backlog -> ideation -> implementation -> validation -> done |

Backlog is initial and gated; ideation is gated where present; validation is gated
and fresh, with feedback to implementation; done is terminal. Backlog and done
are state boundaries, not worker stages. SD follows ordered stages, so POC uses
a separate four-stage workflow while Pilot/Prod share the five-stage definition.
Only adopt the needed route. Profile remains a user choice on each task and
selects skill rules, not graph transitions. FO holds a profile/graph mismatch;
that check is an instruction, not a new runtime enforcement mechanism.
POC skips ideation and currently uses independent validation. Direct POC
eligibility and special Production recovery are **not implemented or proven**.

## Authority and loading

User authority, approved project AGENTS.md conventions and SD contracts constrain
this framework. Within those boundaries, selected profile principles take
precedence over stage practices, which take precedence over conditional project
learning. If an approved requirement conflicts with the selected profile, return
the affected decision to the user; do not silently change profiles or scope.

Each stage SKILL.md owns its sole declared profile routing table. The FO resolves
the recorded variant/profile before dispatch. A dispatched or reused worker
invokes that variant's exact skill and reads the matching shared profile first,
then stage principles, its stage-specific profile reference, and applicable
adopted project learning. A short final profile reminder is enough; do not load
all profiles or repeat the entire shared rules. Unknown selections, missing
inputs/references or unresolved authority conflicts require a hold report.
These are skill instructions, not mechanically unskippable runtime gates.

Engineering Reviewer provides independent technical assurance; CE (Chief Engineer)
advises the next smallest integrated delivery step. Their agents and skills retain
the existing role boundaries and Opus/xhigh policy. Neither is a routine gate,
and POC defaults to no consultation. Exact `kc-dev-flow-2:` references prevent
declared links from accidentally selecting the baseline; actual host resolution
still needs a separate behavioral test.

## Design and delivery

FO leads direction and requests research only when it can change a decision;
workers author the bounded deliverable. For a route that includes ideation,
use a PRFAQ with Mermaid whose actors, order, branches and approval boundaries
match the prose. Add a suitable design-skill preview or HTML draft when needed.
Write material corrections back to the same definition before user approval.
Implementation follows approved scope; validation checks the exact result and
returns repairs through the supported feedback route. POC must not gain
an ideation stage or extra design gate through this convention.

When work changes retained documents or behavior they describe, stage skills load
one [document reference](references/retained-documents.md) for affected claims,
unique content and rendered diagram agreement. Validation also checks whether
its decisive checks can catch relevant errors, reusing existing counterexamples.
These conditional practices add no mandatory architecture file or global audit.

The [workflow source](references/sd/workflow.md) defines limited FO design
corrections and nonblocking dispositions. Template adoption grants no editing
permission; approved decisions and worker evidence remain protected.

Continuous stage-pin sealing and its kernel loader are intentionally omitted.
Git history and SD records do not prove which content was used at a historical
stage entry. This package does not fix the baseline's skipped-pin bug or
claim equivalent tamper detection.

## Local learning proposals

Use [`kc-dev-flow-2:evaluate-learning`](skills/evaluate-learning/SKILL.md) for a
bounded independent assessment of explicitly supplied task evidence. Its three
outcomes are add, no-change and remove; a rewrite combines remove/add. Entries
contain Applicability, Practice and Evidence. One task supports one case; reading
a rule or green tests alone does not prove improvement. No applicable case is
not grounds for deletion, and unknown attribution stays unknown. Fixed project
rules require separate user-approved adoption into AGENTS.md; no auto-promotion,
scores or maturity system is introduced.

The skill documents the strict evidence-pack and evaluation JSON formats and
commands for `scripts/learning.py`. This stdlib helper records eligibility from
caller-supplied closure/merge facts; it does **not** verify SD or GitHub truth.
It stores one atomic record under the Git common directory's
`kc-dev-flow-2/learning/`, shared by linked worktrees in the same clone. An opaque
claim token binds completion to its pending attempt. Invalid results leave that
claim repairable; duplicate triggers observe it rather than launch another job.
A completed record contains both evaluation and local proposal; no-change has no
proposal. No command writes project learning.md, AGENTS.md or workflow state.

Pending ownership is not process liveness. Torn/missing records are uncertain;
recovery requires a current record digest and an explicit caller attestation
that the prior owner stopped. It preserves prior bytes and revokes the old token.
Completed results cannot be replaced through this CLI. POSIX file locking and
atomic replacement cover cooperating callers on local filesystems, not separate
clones, distributed locks or protection from a process with the same file access.

A local receipt/proposal is not an active practice. Project learning becomes
usable only through the separately authorized review/merge path; this helper does
not implement or certify it. Real SD/GitHub collection, host hooks, background
launching, Draft PR creation, issue reporting, deduplication across machines and
startup notification remain future work. The independent semantic quality of
learning proposals requires agent evidence beyond recorder tests.

## Maintenance and evidence

These are source-repository maintenance commands, not standalone installed-plugin
commands. They depend on the repository-level `scripts/skill-frontmatter-lint.sh`
and its dependencies. Run from a complete checkout's repository root:

```sh
python3 kc-dev-flow-2/scripts/lint-skills.py
python3 kc-dev-flow-2/scripts/test_lint_skills.py
python3 kc-dev-flow-2/scripts/test_learning.py
python3 kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /absolute/path/to/active-spacedock
```

Lint reuses `scripts/skill-frontmatter-lint.sh` scoped to this tree and checks
declared route coverage, applicability values, exact paths, required principles
and skill namespaces. It does not parse rule prose or prove route-following,
unknown-profile refusal, gate execution or cross-host parity.
The [Agent Skills specification](https://agentskills.io/specification) defines
frontmatter and directory conventions; complete format validation is a separate
authoring check, not a claim made by this CLI.

The [adoption reference](references/sd/adoption.md) uses SD commission/refit,
split-root state, code worktrees and the activated SD package's unmodified
`pr-merge` mod. The mod is installed into the adopting workflow, not vendored here.
The workflow's delivery rules preserve project Draft PR, CI and manual merge
requirements and restrict unapproved fallback; those are FO instructions, not new
mechanical controls. Adoption checks actual `merge: pr-merge` hook discovery before
activation: SD can finalize locally when no hook or blocking record exists.

The CLI test copies the workflow source into disposable code/state repositories.
It checks six stage/host handoffs, stage-definition fetches, PRFAQ/Mermaid gate
context, finding disposition and delivery authority. Both route graphs across
three profiles exercise synthetic gate successors and stamped implementation /
validation worktree reuse. Fresh validation is declared configuration, not an
executed independent worker. Copied canonical hook discovery and merge-guard
arming pass; the missing-hook control demonstrates local finalization's limit.
Existing wrong-stage, removed-stage, AC-scanner and host-marker controls remain.
`--keep` retains successful repos and raw evidence; failure evidence is retained
by default. Synthetic approvals and local archive controls are test inputs,
not real user acceptance, hook execution or remote delivery. No prompt is sent
to a model. A real project still needs approved configuration and observed merge.

For an authorized native Claude trial, remove foreign markers for that process
only: `env -u CODEX_THREAD_ID -u PI_CODING_AGENT_DIR claude <approved arguments>`.
Use the exact isolated repository as cwd, name its workflow explicitly in the FO
assignment, and retain `--workflow-dir` on SD commands. Do not change the parent
environment or add a wrapper. The model-free marker check is not a rerun of the
native trial, and a failed stamped dispatch must not be assumed mutation-free.
Before a future live run, verify the selected SD plugin and executable versions;
an updated skill cache alone does not establish a comparable runtime.
At ideation, retain user gate approval while proposing routine implementation
details within accepted scope; escalate material changes rather than every detail.

Future comparisons must include host behavior, retained route exceptions and
learning/review costs as well as removed files. This slice runs no model
experiment and carries forward none of the earlier experiment's time budget.
