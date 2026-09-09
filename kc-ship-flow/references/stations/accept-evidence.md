# accept-evidence station

**Enforcing script:** `kc-ship-flow/scripts/accept-evidence.sh <evidence-file> [--repo <repo-path>]`

**Input:** a worker's `## Evidence` block file: `CANDIDATE_SHA`, `BASE_SHA`, `BRANCH`,
`WITHOUT_IT_COMMAND`, and `WITHOUT_IT_REMOVED_VARIANT` are required fields.

**Output:** re-runs `WITHOUT_IT_COMMAND` against a temporary worktree at `BASE_SHA` and checks it
against the block's own claims, without re-running the worker; prints `accept-evidence: ACCEPT` on
its last line when every check passes. When `WITHOUT_IT_COMMAND` exits 126/127 at `BASE_SHA`
(command not found) and a path it names is tracked at `CANDIDATE_SHA` but absent at `BASE_SHA` — the
candidate added it, e.g. a new test file — that leg is satisfied by the absence itself; stdout
records `at BASE_SHA: absent (added by candidate): <path>` instead of an exit code.

**Refusal:** exit 2 on usage errors, a missing evidence file, an incomplete block, or an unreachable
`BASE_SHA`; exit 1 (`REFUSE:` on the last stdout line) on an unreachable `CANDIDATE_SHA`, a `BRANCH`
remote head that does not match `CANDIDATE_SHA`, an out-of-tree path in either without-it line, a
masked exit (trailing `|| ` or `; true`) in either without-it line, no path extractable from
`WITHOUT_IT_COMMAND`, `WITHOUT_IT_REMOVED_VARIANT` altering none of the changed paths
`WITHOUT_IT_COMMAND` reads, `WITHOUT_IT_COMMAND` already exiting 0 at `BASE_SHA`, or
`WITHOUT_IT_COMMAND` exiting 126/127 at `BASE_SHA` with no named path tracked at `CANDIDATE_SHA` and
absent at `BASE_SHA` (command not found, and not a path the candidate added).
