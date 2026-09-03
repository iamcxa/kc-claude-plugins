# UAT: Ship-flow glue closes its four POC defects

Plan receipt `08c6798ba0223cf1` · Project `923b6c74-1176-413f-8e99-3f0ec73c0cde` · dispatch order DEV-66 -> DEV-65 -> DEV-64

Each layer is one Draft PR at one pinned candidate, linked as GitHub native stack #350 (#347 -> #348 -> #349). Merge the whole stack with `gh stack merge 350` after UAT; do not merge a layer alone. Known noise: layer 3 (#349) was dispatched on layer 2's round-0 candidate 353795c, so its stack diff carries layer 2's fix-round delta; Codex round 3 flagged this and the commission rule is now 'verify a layer fully before dispatching the next'. All Linear state is untouched by the FO.


## Layer 1: DEV-66 — Dispatch carrier and e2e evidence rules for cloud workers

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/347 · candidate `b5adfba85b34` · base `bda45e6bb271` · branch `feature/dev-66-dispatch-carrier-and-e2e-evidence-rules-for-cloud-workers`
- Without-it (worker's line, FO ran verbatim): retained exit 0, removed exit 1
  - `python3 scripts/kc-dev-flow-contract-test.py`
- Contract test exit 0 · merge-tree preflight vs main `bda45e6bb271` exit 0
- How to verify: check out the candidate, run the without-it line (expect 0), apply the removed variant, run it again (expect non-zero). ACs and their evidence are in the PR body.

## Layer 2: DEV-65 — WITHOUT_IT_COMMAND is one verbatim shell line the FO runs unchanged

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/348 · candidate `09f1f72c70be` · base `b5adfba85b34` · branch `feature/dev-65-without_it_command-is-one-verbatim-shell-line-the-fo-runs`
- Without-it (worker's line, FO ran verbatim): retained exit 0, removed exit 1
  - `python3 scripts/kc-dev-flow-contract-test.py`
- Contract test exit 0 · merge-tree preflight vs main `a6172ac786f7` exit 0
- How to verify: check out the candidate, run the without-it line (expect 0), apply the removed variant, run it again (expect non-zero). ACs and their evidence are in the PR body.

## Layer 3: DEV-64 — Transcript reads go through conductor sql, not session message --after

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/349 · candidate `13484f73f4fa` · base `353795cda1af` · branch `feature/dev-64-transcript-reads-go-through-conductor-sql-not-session`
- Without-it (worker's line, FO ran verbatim): retained exit 0, removed exit 1
  - `python3 scripts/kc-dev-flow-contract-test.py`
- Contract test exit 0 · merge-tree preflight vs main `56e3095d8226` exit 0
- How to verify: check out the candidate, run the without-it line (expect 0), apply the removed variant, run it again (expect non-zero). ACs and their evidence are in the PR body.
