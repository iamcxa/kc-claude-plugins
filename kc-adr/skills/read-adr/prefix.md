# Optional prefix

A repo opts in. The default is no prefix: cite as `<repo> ADR NNNN` plus a reference block (repo, path, full commit, digest).

**Cross-repo short name.** A prefix is shorthand for a repo in a citation, such as `ME#0003`. It changes no file, path or number. Form: `[A-Z][A-Z0-9]{1,7}#[0-9]{4}`. The prefix-to-repo map is one line in the opting repo's instruction file (`ME = <owner>/<repo>`), a location and not a copy of a ruling. A short name alone is not a pinned citation: resolve it to that repo's `docs/adr/NNNN-*.md`, read it at the clone's current head and tell the person it was unpinned. Only a reference block pins.

**Namespaces inside a monorepo are deferred.** They change paths and numbering, which the ADR linter and number reserver must support first. If a repo asks, stop and route it to the coordinator.
