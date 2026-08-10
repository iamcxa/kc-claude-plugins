# KC Dev Flow

A small, versioned development-flow kernel for Claude Code and Codex. It lets a
repository keep its own tracker, sprint model, workflow runtime, and delivery
provider while sharing the same authority and evidence discipline.

## Skills

- `adopt-dev-flow` — audit, adopt, or upgrade the kernel without rebuilding an
  existing workflow.
- `continue-dev-flow` — resume an approved sprint and keep advancing committed
  work without unnecessary captain pauses.
- `promote-dev-flow` — review sanitized adopter field evidence at the canonical
  source without granting it task or policy authority.
- `science-officer-em` — provide independent engineering judgment through the
  canonical replacement for the former Ship-Flow skill, preserving its legacy
  report envelope while carrying the complete portable advisory record.

## Optional policy mods

- `engineering-judgment` — adjudicate reviewer conflict against governing
  contracts and primary behavior, synthesize risk and durable cost, and return
  an advisory `proceed | narrow | return | block | costly_no` recommendation
  without replacing gate or captain authority.
- `project-context-maintenance` — what a retained document may contain, and
  keeping approved product and architecture context aligned with delivered
  behavior. Two independently adoptable parts.
- `reverse-recovery-audit` — recover existing brownfield seams before proposing
  greenfield work.
- `work-control-profile` — bind optional mechanical controls to local adapters
  and four-state receipts.

## Distribution

The plugin is not a tracker, scheduler, daemon, or merge bot. The kernel defines
portable semantics; each repository binds its existing authorities in a README
`Local Profile` and vendors the accepted kernel plus selected policy mods under
its workflow `_mods/` directory. Stage `Policy mods` lists decide which local
policies apply. There is no binding YAML, digest registry, or runtime package
fallback.

`adopt-dev-flow` owns initial vendoring and explicit upgrades. It replaces an
accepted canonical file byte-for-byte while local mechanisms and exceptions stay
in the workflow README. `continue-dev-flow` reads the vendored policy and never
installs or rewrites it. Optional controls remain off until individually declared.

At launch, unseen immutable debriefs may yield at most one repository-local or
reusable kernel improvement candidate. A derived `_improvements/state.yaml`
cursor prevents repeat analysis. Detection never includes task creation, sprint
admission, scheduling, merging, or permission to pause product work.

`reusable-kernel` is the version-1 transport label for a sanitized source
handoff, not a placement verdict. `promote-dev-flow` rechecks duplicates and
classifies rule, enforcement, local-instance, and no-change dispositions at the
canonical source. Its deterministic intake helper preserves distinct recurrence
and renders a captain-review-only proposal without writing repository or provider
state.

`science-officer-em` loads a stage-selected repository-local
`_mods/engineering-judgment.md` when active. An explicit direct invocation may
use the plugin-shipped reference for that answer only; it does not adopt the mod,
activate stage policy, satisfy a gate, or gain provider and workflow authority.
The skill returns `science_officer_em_upward_report` for compatibility and nests
the complete `engineering_judgment` advisory record inside it.

Install the plugin through the `kc-claude-plugins` marketplace in Claude Code.
Codex uses the co-shipped `.codex-plugin` manifest and the same skill files.
