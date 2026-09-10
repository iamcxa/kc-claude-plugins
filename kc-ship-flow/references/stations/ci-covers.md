# ci-covers station

**Enforcing script:** `${CLAUDE_PLUGIN_ROOT}/scripts/ci-covers.sh <repo-root> <package-path> <check-name>`

**Input:** a repo root, the path of the monorepo package the merge verdict is about to trust CI for,
and the name of the CI check that verdict cites as the gate.

**Output:** exit 0 when a workflow under `.github/workflows/` both (a) names `<check-name>` as a job
id, a job `name:`, or a step `name:`, and (b) that same workflow enters `<package-path>` (a
`working-directory: <package-path>` line, a `cd <package-path>` line, a `--filter <manifest-name>`
line using `<package-path>/package.json`'s `name`, or a `paths:` filter entry matching
`<package-path>/**`); prints `<package-path> run by <check-name>`.

**Refusal:** exit 1 when no workflow satisfies both (a) and (b) — prints `<package-path> not run by
<check-name>` and names which of (a)/(b) failed; exit 2 on a usage error.

DEV-149: batch ab2fb2635f0c's FO wrote "CI's pr-test is the aggregate gate" in iamcxa/qnow#1181 and
#1182 for an npm island inside a pnpm monorepo that `pr-test` never entered — a green check had run
none of the island's tests. Run this script before a merge verdict cites a CI check as the gate for a
monorepo package; on exit 1 the verdict names the FO's own local run as the gate instead, not the CI
check.

This is text/grep match against `.github/workflows/*.yml`/`*.yaml` only, with no YAML parser — it
proves job/step naming and directory entry, not full workflow semantics.
