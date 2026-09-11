---
commissioned-by: spacedock@0.25.0
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
    - name: backlog
      initial: true
    - name: implementation
    - name: validation
      gate: true
    - name: done
      terminal: true
---

# fixture workflow for watch.sh tests
