---
status: implementation
---
# DEV-156 fixture: dispatch build fails

Synthetic dev task dispatched against a stage its sibling
`task-build-fails/README.md` workflow does not define, so
`spacedock dispatch build` exits non-zero.
