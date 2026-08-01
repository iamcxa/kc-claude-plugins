# KC Dev Flow

A small, versioned development-flow kernel for Claude Code and Codex. It lets a
repository keep its own tracker, sprint model, workflow runtime, and delivery
provider while sharing the same authority and evidence discipline.

## Skills

- `adopt-dev-flow` — audit, adopt, or upgrade the kernel without rebuilding an
  existing workflow.
- `continue-dev-flow` — resume an approved sprint and keep advancing committed
  work without unnecessary captain pauses.

## Design boundary

The plugin is not a tracker, scheduler, daemon, or merge bot. The kernel defines
portable semantics; each repository owns a short local binding and any provider
adapters. Optional controls are off until individually declared.

Install the plugin through the `kc-claude-plugins` marketplace in Claude Code.
Codex uses the co-shipped `.codex-plugin` manifest and the same skill files.
