# Dev-flow 2

An optional experimental alternative to kc-dev-flow. It provides a thin
start/resume entry, profile principles, stage skills, retained advisory roles,
read-only routing lint, and a standalone Pilot fixture for Spacedock CLI tests.
Existing kc-dev-flow projects stay on their selected variant; this package does
not migrate them automatically or claim full safeguard parity or a one-third
size reduction. There is no runtime loader, hook or learning worker.

## Controlled trial

This candidate includes Claude Code and Codex manifests. Its 0.1.0 metadata
bootstraps the repository's new-component policy; no released tag exists yet.
Use a reviewed checkout for a controlled local trial. For Claude Code, launch
from the intended project with the checkout's absolute package path:

```sh
claude --plugin-dir /absolute/path/to/kc-claude-plugins/kc-dev-flow-2
```

Then invoke `/kc-dev-flow-2:dev`. This is a local package trial, not a published
marketplace release. Codex includes a native manifest with `skills: "./skills/"`;
native installation and discovery found all seven skills in this candidate.
Its shorthand invocation and the new entry's model behavior remain unproven.
See [validation scope](VALIDATION.md) for the historical evidence and its limits.

Spacedock's plugin and CLI are required for orchestration. A project must have an
explicitly selected experimental variant/profile and an approved workflow before
stage work; invoking the entry does not adopt or rewrite a project workflow.

## Entry

Use [`kc-dev-flow-2:dev`](skills/dev/SKILL.md) to start or resume work. It resolves
the explicit project/workflow/task and approved selection, then hands orchestration
to `spacedock:first-officer`. Stage skills keep their own profile routes; the entry
does not migrate existing work or duplicate SD's control loop. Claude plugin skills
use `/kc-dev-flow-2:dev`, not a bare `/dev`; Codex shorthand resolution remains
unverified. Historical loading evidence predates this seventh skill and does not
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

Backlog is initial and gated; ideation is gated; validation is gated, normally
fresh, with feedback to implementation; done is terminal. Backlog and done are
state boundaries, not worker stages. POC skips ideation without a placeholder
review. Its two working-stage positions do not imply two workers: an eligible
direct POC records proof in implementation and uses the validation terminal
gate; fresh POC uses independent review. Approved recovery and reuse exceptions
remain intended behavior. Their eligibility mapping after loader removal,
including direct POC and Production recovery, is **not implemented or proven**.

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

SO (Science Officer) provides independent technical assurance; CE (Chief Engineer)
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
returns repairs through the supported feedback route. Direct POC must not gain
an ideation stage or extra design gate through this convention.

When work changes retained documents or behavior they describe, stage skills load
one [document reference](references/retained-documents.md) for affected claims,
unique content and rendered diagram agreement. Validation also checks whether
its decisive checks can catch relevant errors, reusing existing counterexamples.
These conditional practices add no mandatory architecture file or global audit.

The [Pilot workflow](references/sd/pilot/workflow.md) defines limited FO design
corrections and nonblocking dispositions. Template adoption grants no editing
permission; approved decisions and worker evidence remain protected.

Continuous stage-pin sealing and its kernel loader are intentionally omitted.
Git history and SD records do not prove which content was used at a historical
stage entry. This package does not fix the baseline's skipped-pin bug or
claim equivalent tamper detection.

## Planned learning — not implemented

Thin host hooks will check authoritative closed-and-landed tasks and deduplicate;
a Stop event itself is not task closure. A bounded independent background worker
will propose additions/removals to project learning.md through an isolated Draft
PR. No-change records a result without an empty PR; rules become active after
observed merge, never automatic merge. SessionStart will expose unannounced
pending/adopted/failed results to FO. Background lifetime, durable results,
concurrent proposals and exclusion of the learner's own PR require proof.

Entries contain Applicability, Practice and Evidence. One supported task is one
case; benefit on a later matching task is repetition under that condition.
Reading a rule or green tests alone do not show benefit; unknown attribution
stays unknown, and no applicable case is not grounds for deletion. Applicable
counterevidence can justify revision/removal. No scores or maturity system.
AGENTS.md promotion requires approval as a project convention, with duplicate
learning removed after adoption. Scoped, reproducible dev-flow bugs will use one
configured issue target and standing deduplication policy; no external actions
are implemented by this package.

## Maintenance and evidence

These are source-repository maintenance commands, not standalone installed-plugin
commands. They depend on the repository-level `scripts/skill-frontmatter-lint.sh`
and its dependencies. Run from a complete checkout's repository root:

```sh
python3 kc-dev-flow-2/scripts/lint-skills.py
python3 kc-dev-flow-2/scripts/test_lint_skills.py
python3 kc-dev-flow-2/scripts/test_sd_dispatch.py
```

Lint reuses `scripts/skill-frontmatter-lint.sh` scoped to this tree and checks
declared route coverage, applicability values, exact paths, required principles
and skill namespaces. It does not parse rule prose or prove route-following,
unknown-profile refusal, gate execution or cross-host parity.
The [Agent Skills specification](https://agentskills.io/specification) defines
frontmatter and directory conventions; complete format validation is a separate
authoring check, not a claim made by this CLI.

The [Pilot fixture](references/sd/pilot/workflow.md) is copied to README.md only
inside disposable repositories, so it does not become a source-tree workflow.
Its CLI test uses the installed `${SPACEDOCK_BIN:-spacedock}`, labels seeded stage
states synthetic, and emits six handoffs across three stages and Claude/Codex
host shapes. It reads each generated dispatch artifact and runs its exact
stage-definition fetch command, including ideation's PRFAQ/Mermaid Gate content.
Negative controls exercise wrong-stage stamped entry and a removed stage.
They also compare bold AC declarations with plain unrecognized declarations
through SD's real AC scanner, and mixed host markers with cleaned child-process
markers through automatic dispatch-host detection. A synthetic report header is
scanner input only; no worker evidence or approval is invented.
`--keep` retains successful fixture repos and raw CLI evidence outside this tree;
failure evidence is retained by default. Fixture seed commits are local synthetic
state, not real work-item transitions or user approvals.

These checks prove CLI transport and refusal boundaries, not skill discovery,
reference reading, model behavior, independent review, actual gate presentation
or successful closure. No emitted prompt is executed. The fixture has no local
delivery hook: future live closure stays on hold until its authority and SD
merge-finalize path are concretely bound; terminal gate approval alone is not done.

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
