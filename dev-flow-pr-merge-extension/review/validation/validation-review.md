# dev-flow-pr-merge-extension — validation gate

Candidate: f4b522e4 (PR #414, CI green, MERGEABLE, includes main).
Stage report: `## Stage Report: validation` — AC-1..AC-4 reproduced in a clean worktree; three must-catch mutations caught by name (block drift, released-body edit, Residuals cap), one harmless edit not flagged; scope confirmed to kc-dev-flow/, docs/dev/_mods/pr-merge.md and two scripts/ tests; no Spacedock file changed.
FO verification: contract test and portable-delivery test PASS at f4b522e4; block equals resource byte-for-byte (markers included); one-character mutation fails closed.
Question for the Captain: approve validation and merge #414?
