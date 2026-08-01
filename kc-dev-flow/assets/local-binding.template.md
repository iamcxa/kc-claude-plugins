# Local Dev Flow Binding

```yaml
kernel_source: iamcxa/kc-claude-plugins/kc-dev-flow
kernel_version: <installed kc-dev-flow package version>

authority:
  project_context: <existing product and architecture sources>
  work_items: <canonical task or issue tracker>
  iteration: <canonical sprint membership and order>
  execution_state: <workflow runtime or state store>
  delivery: <authenticated delivery plus terminalization rule>
  observation: <optional ledger or metrics source, or none>
  gate_verdicts: <fresh reviewer or EM>
  scope_and_irreversibility: <captain or named authority>

adopted_controls: []

local_routes:
  normal: <repository lifecycle>
  bounded_defect: <short route or none>

local_exceptions: []
```

Keep this binding in the repository's existing workflow entrypoint or local mod.
Do not create another top-level document solely to hold the same truth.
