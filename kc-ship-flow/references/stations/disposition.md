# disposition station

**Enforcing script:** `${CLAUDE_PLUGIN_ROOT}/scripts/disposition.py <findings.json>` or
`${CLAUDE_PLUGIN_ROOT}/scripts/disposition.py <bundle-dir>`

**Input:** the findings file the FO's own session wrote to disk after running the `kc-pr-review`
skill on a PR (schema `kc-dev-flow-pr-review-findings/v1`). When the diff touches a dependency
manifest or lockfile, pass a bundle directory instead of the bare findings file:
`<dir>/findings.json` (same schema), `<dir>/changed-files.txt` (the changed paths; this script has no
other way to learn the diff), and `<dir>/review/findings-<pr>-supply.json` (the
`tob-supply-chain-checker` lane's output, `<pr>` from `findings.json`'s `pr` field). A bundle
directory without `changed-files.txt` is refused (exit 2, `changed-files.txt required`), never read
as an empty diff, because an empty diff would silently skip the dependency check below.

**Output:** a JSON disposition on stdout — `block`, `listed`, or `reviewer-absent` — printed once per
call.

**Refusal:** exit 2 on a `findings` list with a non-dict entry, or an entry whose `category` is not a
string — a malformed writer output must not silently read as a normal `listed` finding. In bundle
form only, exit 2 with `changed-files.txt required` when that file is absent, and exit 2 with
`supply-chain findings required` when a changed path is a dependency manifest
or lockfile (`package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `requirements*.txt`,
`pyproject.toml`, `poetry.lock`, `go.mod`, `go.sum`, `Cargo.toml`, `Cargo.lock`) and
`review/findings-<pr>-supply.json` is absent — a dependency diff must not reach disposition on
code/security/delta review alone. A diff without such a path, or one with the supply-chain file
present, is unaffected.

Security, data-loss, and compatibility findings outside the Brief block the candidate; general
improvements are scoped out. This is `kc-plan-approval/v1`'s `defaults.findings_outside_brief` rule,
enforced here by `BLOCKING_CATEGORIES = {security, data-loss, compatibility}`. An empty or missing
findings file is `reviewer-absent` with the `fallback_to_fo_diff_read` marker, never read as "no
findings", because the two are indistinguishable from a findings file alone.

Placed segments (`references/placement.tsv`): `f7d9f3314010`, `94f809381215`.
