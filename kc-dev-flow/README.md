# KC Dev Flow

A small, versioned development-flow kernel for repositories running Spacedock,
under Claude Code or Codex. It exists to carry a lesson one repository paid for
into the others before they pay for it again: repositories keep their own
tracker, sprint model, and delivery provider, and share the authority and
evidence discipline that cost someone a cycle to learn.

## Skills

- `adopt-dev-flow` — audit, adopt, or upgrade the kernel without rebuilding an
  existing workflow.
- `continue-dev-flow` — resume an approved sprint and keep advancing committed
  work without unnecessary captain pauses.

## Design boundary

The plugin is not a tracker, scheduler, daemon, or merge bot. The kernel defines
portable semantics; each repository owns a short local binding and any provider
adapters. Optional controls are off until individually declared.

At a sprint boundary, repeated friction is classified as repository-local or a
reusable kernel improvement. The default is proposal-only; an adopter may
explicitly allow a sanitized, duplicate-checked upstream pull request. That
permission never includes scheduling or merging the improvement.

Install the plugin through the `kc-claude-plugins` marketplace in Claude Code.
Codex uses the co-shipped `.codex-plugin` manifest and the same skill files.
