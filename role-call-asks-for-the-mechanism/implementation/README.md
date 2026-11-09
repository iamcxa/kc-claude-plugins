# Implementation evidence

Candidate: ebbac3de0dbf3b9bf9bf4c59611ff06bb5eb4fe9. Base: 82c9e67ae892b80647c3f6a8b6929f993e42dbc2. Product source is in the assigned worktree, branch spacedock-ensign/role-call-asks-for-the-mechanism; no product push or PR was made.

Each test or guard has a .json command/exit record and a .log with complete output. test_role_triggers.json records the host session's direct exit; the other commands used run.py. candidate.json binds the four product files to their SHA-256 hashes; tests ran after the final product edit and before the byte-identical commit.

Reproduce suites from the candidate worktree with python3 -B kc-dev-flow-2/scripts/test_role_triggers.py (and the other three names in tests.json). run.py takes WORKTREE EVIDENCE_DIRECTORY NAME COMMAND... and retains command/exit output. The declared installed package is /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0; guard command records name the exact package scripts and workflow/task inputs. No dependencies were installed.

Reproduce mutations with python3 -B mutations.py WORKTREE NEW_OUTPUT_DIRECTORY, which must already exist. Each run creates a fresh temporary directory, copies the product test file, removes __pycache__, and invokes python3 -B against the modified script. All six intentionally broken variants exit 1 with assertions (no import errors). base-0.36.0 demonstrates the original absence. Expected mutation failures are not product-suite failures.

Reproduce the corpus comparison with python3 -B corpus.py WORKTREE STATE_CHECKOUT OUTPUT_JSON [STATE_REV]. It pins the state HEAD at entry and reads 220 root/archive task files on the recorded state bd507c059bacfd7c27b748ee50bcee39e049924a: 219 byte-identical outputs, one intended question/template change in _archive/paseo-codex-dispatch-practice.md, no exit changes and no unverifiable tasks. The local HEAD can advance; pass bd507c059bacfd7c27b748ee50bcee39e049924a as STATE_REV for exact historical comparison.

Optional checks skipped: HistoricalBoundQuestionTests requires GATE_PRESENTATION_STATE for five saved historical replays; the real dispatch-builder test requires SPACEDOCK_BIN and SD_PLUGIN_ROOT. No new skip was added. These optional integrations were not run, never claimed clean.

replay-author-regrade.md is this implementation worker's re-read of the six saved answers, not independent validation. Independent re-grading, RoboRev, hosted CI and publication remain with FO. CI cost per PR was not measured; CI configuration did not change.
