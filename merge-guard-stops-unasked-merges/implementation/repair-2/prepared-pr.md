feat(kc-dev-flow-2): stop merges without a saved ask

A `gh pr merge` now checks the newest saved merge ask for its repository-qualified PR and head before execution. An uncarried merge asks on Claude and denies on Codex. The package supplies the guard script, an ancillary approval recorder, user registration instructions and ADR 0063; operators register it after release.

Global repository flags, literal env/command wrappers, executable paths and shell quoting are parsed. REST PR-merge endpoints, GraphQL calls, unknown aliases/extensions and unparseable routing stop. Explicit `--auto` forms and asynchronous REST merges stop even with a matching head: FO never enables auto-merge. Unknown merge flags stop; cancellation with `--disable-auto` remains possible with a matching record.

The guard assumes the target branch has no merge queue. Plain gh merge can queue implicitly on a queue-required branch, so a repository enabling one must revisit this guard before relying on it. FO retained the offline hook after reporting no queue on main in kc-claude-plugins, subspace-relay, subspace-web and qnow on 2026-11-06. No live queue lookup or automatic `--admin` bypass is added. Script bodies, direct HTTP/SDK calls and non-PR branch writes remain outside command-text inspection.

Validation at b82f20de6c8e5b868695d03aa4bbcb97e77dd877: 45 merge-guard tests passed; delivery suite 156 passed/1 existing skip; 17 new, 22 preceding and 6 original executed falsifiers rejected their mutants using python3 -B. The historical replay remains 54 pass/30 stop, then 74 pass/10 stop with synthetic ancillary approvals; #672 stays stopped, while removing the record question-head check lets it pass. ADR, number, skill/design, comment and diff checks pass. Evidence and exact source hashes are in the task's implementation/repair-2 folder.

No new native host runs were requested for this unit-level repair. Prior host evidence belongs to ebac86a56; it is retained without claiming a new-head native or phone run. CI cost per PR is not measured; triggers are unchanged. FO owns publication, independent validation, RoboRev and hosted CI on this head.
