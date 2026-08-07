# KC Dev Flow

A small, versioned development-flow kernel for Claude Code and Codex. It lets a
repository keep its own tracker, sprint model, workflow runtime, and delivery
provider while sharing the same authority and evidence discipline.

## Skills

- `adopt-dev-flow` — audit, adopt, or upgrade the kernel without rebuilding an
  existing workflow.
- `continue-dev-flow` — resume an approved sprint and keep advancing committed
  work without unnecessary captain pauses.

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

Install the plugin through the `kc-claude-plugins` marketplace in Claude Code.
Codex uses the co-shipped `.codex-plugin` manifest and the same skill files.
