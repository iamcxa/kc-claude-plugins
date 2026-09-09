---
commissioned-by: spacedock@0.27.2
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
  states:
    - name: implementation
    - name: done
      terminal: true
---

# DEV-156 fixture workflow: stage with no model

## Stages

### `implementation`

Synthetic stage body for the DEV-156 dispatch-station fixture.

### `done`

Terminal.
