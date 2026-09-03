## Evidence
CANDIDATE_SHA: 13484f73f4fa579baf79ef3617517e2ed2cdca6f
BRANCH: feature/dev-64-transcript-reads-go-through-conductor-sql-not-session
BASE_SHA: 353795cda1af04207a755796e669a00e08b063ee
FILES: docs/dev/README.md, scripts/kc-dev-flow-contract-test.py, scripts/ship-flow/worker-transcript.sh
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
WITHOUT_IT_COMMAND: python3 scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_REMOVED_VARIANT: git checkout 353795cda1af04207a755796e669a00e08b063ee -- docs/dev/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: scripts/ship-flow/worker-transcript.sh 3c6a1d84-b7f0-474c-9e34-ec133b1a1326 (session with an Evidence block) -> prints the last fenced `## Evidence` block, exit 0. scripts/ship-flow/worker-transcript.sh e66bc8bb-3112-4dc4-b6d1-d56b19b3c69c (session with no Evidence block) -> prints "no evidence block" to stderr, exit 1. Both runs recorded with session ids in .context/dev-64-evidence/ac1-positive.log and ac1-negative.log (gitignored, not part of the committed tree).
AC-2: docs/dev/README.md "## Ship-flow runtime" section now states the First Officer reads worker transcripts through `conductor sql` against `session_transcripts_view`, not `conductor session message --after`, and names both CLI failure modes: the 64 KB JSON truncation and the `--after` cursor rejecting a sent message's id.
AC-3: scripts/kc-dev-flow-contract-test.py pins three phrases from the new README paragraph. Mutation run: paragraph removed -> python3 scripts/kc-dev-flow-contract-test.py exits 1 ("Ship-flow runtime omits the conductor-sql transcript-read rule: ..."); README restored -> exit 0. Logs recorded in .context/dev-64-evidence/ac3-mutation.log and ac3-restored.log (gitignored, not part of the committed tree).
BLOCKER: none
