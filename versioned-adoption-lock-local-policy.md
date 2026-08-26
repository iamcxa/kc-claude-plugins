---
title: Version kc-dev-flow adoption while preserving local policy
status: backlog
product: kc-dev-flow
sprint:
sprint-readiness: defer
source: Captain discussion after PR #299; marketplace installation and repository adoption currently have no client-version lock
design: required
worktree:
id: ac5kp9y828d2zqts0x5pq5cc
---

Marketplace installation versions the plugin in the client cache, while `adopt-dev-flow` mechanically vendors canonical files into the repository and compares file contents only during an explicit upgrade. The adopter does not record or verify the installed plugin version or canonical bundle digest on each load.

Explore the smallest versioned adoption contract that:

- records plugin slug, version, canonical bundle digest, and vendored file set;
- overwrites canonical loader, kernel, profile, and reference files mechanically after accepted upgrade semantics;
- preserves one host-neutral repository-local policy layer outside canonical files;
- uses `AGENTS.md` and `CLAUDE.md` only as short pointers to that local policy;
- permits local bindings and stricter rules but fails closed when local policy weakens kernel authority or route semantics;
- keeps repository-contained, offline-reproducible execution instead of resolving mutable client cache paths at runtime.

## Boundary

This is an unscheduled design item. It does not change PR #299, the current adoption layout, marketplace installation, plugin versioning, or any adopter repository.

## Decision to shape

Compare manifest-based vendoring, a single signed/digested contract bundle, and direct runtime plugin resolution. Prefer the smallest option that detects client/adopter drift while keeping local policy durable and host-neutral.
