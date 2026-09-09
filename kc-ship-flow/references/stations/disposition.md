# disposition station

**Enforcing script:** `kc-ship-flow/scripts/disposition.py <findings.json>`

**Input:** the findings file the FO's own session wrote to disk after running the `kc-pr-review`
skill on a PR (schema `kc-dev-flow-pr-review-findings/v1`).

**Output:** a JSON disposition on stdout — `block`, `listed`, or `reviewer-absent` — printed once per
call.

**Refusal:** exit 2 on a `findings` list with a non-dict entry, or an entry whose `category` is not a
string — a malformed writer output must not silently read as a normal `listed` finding.

Security, data-loss, and compatibility findings outside the Brief block the candidate; general
improvements are scoped out. This is `kc-plan-approval/v1`'s `defaults.findings_outside_brief` rule,
enforced here by `BLOCKING_CATEGORIES = {security, data-loss, compatibility}`. An empty or missing
findings file is `reviewer-absent` with the `fallback_to_fo_diff_read` marker, never read as "no
findings", because the two are indistinguishable from a findings file alone.

Placed segments (`references/placement.tsv`): `f7d9f3314010`, `94f809381215`.
