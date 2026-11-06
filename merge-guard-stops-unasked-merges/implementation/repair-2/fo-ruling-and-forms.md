# FO ruling, 2026-11-06

Source: Paseo message 77ad909e-ff5e-41f8-b1fb-3f401590869f from FO agent 2e87a82e-a8a9-4e41-973a-7483aa46e39d.

FO declined a live gh metadata query in the hook because it adds a failure mode to every merge. FO reported checking GraphQL repository.mergeQueue(branch:) on 2026-11-06: main had no merge queue in iamcxa/kc-claude-plugins, spacedock-dev/subspace-relay, spacedock-dev/subspace-web and iamcxa/qnow. This is FO-reported evidence; the implementation worker did not independently repeat those four queries.

FO directed this repair to stop explicit --auto, REST and GraphQL auto-merge/enqueue routes, and document the assumption that a target branch has no merge queue. Any repository enabling a queue must revisit the guard before relying on it. No live lookup or automatic --admin bypass was authorized. No new native host runs are needed for this unit-level repair.

Plain gh pr merge on a queue-required branch remains an explicit limit under this ruling. --disable-auto cancels auto-merge and does not request a deferred merge; a matching-record cancellation is retained. --auto=false and other equals forms stop conservatively as explicit --auto syntax. gh repo edit --enable-auto-merge changes repository configuration; it does not enable a particular PR or enqueue it. Unknown merge flags, aliases and extension exec stop conservatively.

Primary sources read on 2026-11-06:
- https://cli.github.com/manual/gh_pr_merge
- https://raw.githubusercontent.com/cli/cli/v2.103.0/pkg/cmd/pr/merge/merge.go
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request-with-a-merge-queue
- https://docs.github.com/en/graphql/reference/pulls
- https://docs.github.com/en/enterprise-cloud@latest/rest/pulls/pulls?apiVersion=2026-03-10

The documented REST /pulls/N/merge-async route supports default, direct_merge and merge_queue actions. All stop, including encoded endpoints; older plain endpoint text already stopped through the raw fallback, while percent-encoded merge-async passed at ebac86a56. GraphQL enablePullRequestAutoMerge and enqueuePullRequest already stopped at ebac86a56; the repair retains that behavior and supplies the FO policy reason. The matrix records old/current verdicts without executing a merge.
