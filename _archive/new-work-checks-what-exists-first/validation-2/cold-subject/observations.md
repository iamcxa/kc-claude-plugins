# Ideation observations

## Assignment and boundary

- Recorded route: kc-dev-flow-2 / pilot / ideation. Scope is the named directory collision in design_surfaces.py, not a replacement checker.
- The supplied candidate is an exported source tree without Git metadata. Read-only task state is the sole entity in the supplied state snapshot; no other live entity or prior stage report is present there. No sibling sessions were queried.
- Harness authority supersedes generated commit/state-write instructions. All artifacts and scratch inputs are under subject-output; no state, product, repository metadata or external write is authorized.

## Before new work — checked before drafting the proposal

- Own repository: read design_surfaces.py main(), check_task(), scope_hold(), task_folder(), worth_stage(), and the workflow's File Naming and check-command passages. main() passes Path(args.task) unchanged to both validators. check_task() catches OSError; default mode then calls scope_hold(), which reads the same path without that catch. This explains why default mode crashes and seed mode does not.
- Existing adjacent mechanisms: dispatch_records.py extension_errors() selects existing index.md or sibling .md files; pr_watch.py entities() enumerates folder/index.md and flat .md entities. These demonstrate existing layouts, not a generic command-argument resolver. The repair should change the existing CLI entrance, preserving its content checks and explicit file inputs.
- Upstream contract: the installed Spacedock CLI's own status --help documents --resolve REF as slug/id/prefix resolution. Its read-only --resolve call on this supplied workflow returned the task's flat .md path. Native resolution exists; using it for this bounded path collision would introduce workflow discovery and slug/id/prefix semantics beyond the local path seam. Keep explicit Spacedock resolution available to callers; do not duplicate those broader semantics.
- Standard library contract: inspected the running Python pathlib source for Path.read_text(), Path.is_file() and Path.with_suffix(). read_text opens the supplied path; is_file distinguishes a regular file; with_suffix replaces an existing suffix. Any basename fallback must append .md rather than accidentally replace a dotted directory name's suffix.
- Relevant sibling/adopter: counted filesystem layouts under the single authorized real adopter root, read-only and without reading task contents. The root was accessible but no .spacedock-state directory was exposed by the bounded traversal. adopter-counts.json contains counts only. This is not evidence that the adopter has no workflow or no collision; no private task corpus was available at that probed location, and no outside-root state was followed.
- Third-party tool choice: none added or needed. The existing Python standard library and checker are sufficient. No package install, network call, server, browser or database is needed for this proposal.
- In-force ADRs read: 0083 requires this existing-chain check; 0041 preserves seed-only required bounds; 0027 preserves scope checks at the existing write/gate entrance. No ADR found in the title inventory requires a new path resolver abstraction. No Override line exists in the supplied entity.
- Relevant adopted learning: no new check-output line parser or newly refusing content rule is proposed. Preserve explicit-file verdicts; if implementation adds a refusal rule or printed line, re-evaluate the corresponding learning.md practices before broadening this scope.
- Existing-code capability check: inapplicable by its explicit named-broken-seam exception. This observation is not a missing-capability or no-consumer claim.

## Working probe

The unmodified candidate checker was executed as a real subprocess from subject-output/reproduction with a complete synthetic task.md beside a task/ directory. PYTHONDONTWRITEBYTECODE=1 and Python -B kept candidate imports read-only.

- check task: exit 1, traceback with IsADirectoryError from scope_hold().
- check task.md: exit 0, design surfaces presentable.
- check --seed task: exit 1, existing cannot-read diagnostic, no traceback.
- check --seed task.md: exit 0, seed fields and FO alignment recorded.
- check absent: exit 1 with FileNotFoundError traceback; check --seed absent: exit 1 without traceback. This adjacent result informs error handling but does not authorize unrelated filesystem hardening.

Exact subprocess arguments, stdout, stderr and exit codes are in reproduction.json and reproduction.log. source-identity.json records the checker bytes. No repaired candidate or application suite was run.

## Conclusion before proposal

Repair the current checker entrance: use an explicit regular file unchanged, otherwise accept its sibling .md only for a basename or directory argument, then ensure an unresolved/unreadable target returns the existing failure class without running a second unguarded read. Use one resolved path for both content checks and scope history. Do not add a dependency, shared resolver, workflow migration or new task-layout policy.
