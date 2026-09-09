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

# DEV-156 fixture workflow: build-failure probe

## Stages

### `implementation`

Synthetic stage body; the fixture entity requests an undeclared stage name
against this workflow so `dispatch build` refuses.

### `done`

Terminal.
