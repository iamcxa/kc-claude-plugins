# Local Dev Flow Binding

```yaml
kernel_source: iamcxa/kc-claude-plugins/kc-dev-flow
kernel_version: <installed kc-dev-flow package version>
kernel_entrypoint: references/kernel.md
kernel_digest: <sha256 of that file, at the version above>

authority:
  project_context: <existing product and architecture sources>
  work_items: <canonical task or issue tracker>
  iteration: <canonical sprint membership and order>
  execution_state: <workflow runtime or state store>
  delivery: <authenticated delivery plus terminalization rule>
  observation: <optional ledger or metrics source, or none>
  gate_verdicts: <fresh reviewer or EM>
  scope_and_irreversibility: <captain or named authority>

upstream_contribution:
  repository: <kernel source repository>
  path: <kernel package path>
  mode: propose_only # propose_only | pull_request

adopted_controls: []

local_routes:
  normal: <repository lifecycle>
  bounded_defect: <short route or none>

local_exceptions: []
```

Keep this binding in the repository's existing workflow entrypoint or local mod.
Do not create another top-level document solely to hold the same truth.

`kernel_version` states compatibility intent; `kernel_digest` identifies the
exact bytes agreed to. Neither alone suffices: a version cannot see that the text
moved under a reused number, and a digest cannot see that a newer release exists.

Keep all four fields in **one** fenced block. A binding assembled from fields
scattered across a document is not a binding, and a checker that assembles one
will report success for a repository that has none.

Verify with the kernel-owned checker rather than by reading:

```
python3 <installed kc-dev-flow>/scripts/verify-binding.py <this README>
```

It takes no package path. It resolves `kernel_source` against the installed
releases itself, because a checker told where to look confirms only that the
binding agrees with whatever it was handed — the same internally-consistent
staleness it exists to detect.

It reports one of `PASS`, `STALE_COMPATIBLE`, `REBIND_REQUIRED`, or
`UNRESOLVABLE`, exits non-zero on every outcome except `PASS`, and prints the
entrypoint path the agent is expected to read. Declared-but-unverifiable is
`UNRESOLVABLE`, a different state from undeclared, and the two must not read the
same.
