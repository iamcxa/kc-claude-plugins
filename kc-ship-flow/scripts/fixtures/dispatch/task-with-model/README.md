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
      model: sonnet
    - name: done
      terminal: true
---

# DEV-156 fixture workflow: model-declaring stage

## Stages

### `implementation`

Synthetic stage body for the DEV-156 dispatch-station fixture.

### `done`

Terminal.
