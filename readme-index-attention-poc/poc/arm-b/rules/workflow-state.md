## Workflow State

The README and `_mods` stay in the code repository; mutable task state lives in
`.spacedock-state`, an ignored linked checkout of this workflow's distinct orphan
state branch. Commission/refit owns setup; a fresh clone uses SD state init.
POC uses independent validation in this variant, and special Production recovery
routes are not implemented.

FO commits task state only through SD commands (`gate record`, `state commit
<slug>`, each with `--workflow-dir <dir>`), never by staging the state checkout with
`git add -A` or `git add .`: a broad add sweeps a worker's uncommitted report into
another task's commit.

