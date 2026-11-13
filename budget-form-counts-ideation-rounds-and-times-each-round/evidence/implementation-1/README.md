# Implementation evidence

Candidate: 2661da44a77c2b2f93991a3968fb1515bb4e7132. Base: bfc53d82510006b52baf41569c1e25176e99d87a. Frozen state: c1993d8dc30ec22aeac688a3d4a116a8402acabf.
All product files remained byte-identical to this candidate after commit; hashes are in provenance.json. No private-repository data is archived.

acceptance.json maps every criterion to the actual command, exit and output path. commands.jsonl preserves all runs, including initial unsuccessful attempts. The four suites use the same direct unittest entry points as CI, by FO's explicit instruction replacing the design worker's pytest convenience commands. SPACEDOCK_BIN is /Users/kent/.local/bin/spacedock (0.27.2, the repository CI pin); temporary fixture checkouts are under this dispatch's TMPDIR. The real builder's synthetic roots under /tmp/dev2 and /tmp/spacedock-dispatch are the allowed package behavior.

The all-task comparison is now 249 tasks rather than ideation's 247, because it uses the newer frozen state above. It reports 24 text changes and zero exit changes. The archived census now has 170 tasks and 192 ideation rounds. These are refreshed observations, not copied probe totals.

## Reproduction

The archived run_check.py, setup_evidence.py, replays.py, mutations.py and replay_mutations.py are the actual harnesses. Their scratch path is the dispatched implementation-1 root, removed at close. To reproduce, use a fresh permitted scratch root, copy these harnesses into it, adapt only that root in their paths, and pin the state clone to the recorded state SHA. The candidate's four test commands are recorded verbatim in commands.jsonl; each runs as `python3 -B kc-dev-flow-2/scripts/test_<suite>.py`, with TMPDIR under scratch, PYTHONDONTWRITEBYTECODE=1 and the declared SPACEDOCK_BIN. replay.sh takes the scripts directory, scratch root, slug, budget and pending round; compare_budgets.py takes base scripts, candidate scripts and the frozen state; rounds_census.py takes candidate scripts and state. setup_evidence.py creates the isolated state/replay clones and base script archive. Its initial version command was corrected to --version before saving provenance. No shared repository Git config was written.

## Controls and preserved first attempts

The first role suite failed two assertions: one expected the wrong ideation count, and one retained the old prefix. suite-role-final.txt is the corrected 63-test pass; the failed run is preserved. Four test methods had stale budget text, including multiple assertions in one method. No tests were added for unwritten budget wordings.

Initial mutation copies under /tmp could not pass the package's own scope-notes rule, because their Package root was outside each synthetic fixture's derived scratch root. Those initial dispatch mutation failures are invalid evidence. The corrected copied harness points only its Package root note at the real candidate, keeps the mutated executable under scratch, and passes the three positive controls in mutation-harness-control.txt. The verified-* runs then fail on the expected budget/role behavior. The initial AC-6 mutation changed only its diagnostic, so it did not alter exit codes; the corrected return-value mutation changes 15 real tasks' exits and the comparator fails. The first AC-8 copy lacked a repository lint helper; after copying the existing helper, mutation-lint-control.txt passes and final-mutation-ac8-prose-hold.txt fails solely at 6101 versus 6097. The ADR positive control passes before removing the pointer. Ten accepted mutations are in mutations.json; each used -B with copied caches removed. Two additional replay code mutations wrongly allow the third dispatch (exit 0 versus candidate exit 1).

The first number guard omitted --workflow-dir and its sandbox fetch failed, so it read its own reservation as another holder. number-guards-configured.txt reruns with the actual workflow/state configuration and its permitted narrow state fetch, and passes. No reservation was changed. A scratch-only pytest installation attempt failed DNS before FO directed unittest; pytest was not installed and is unnecessary.

## Reading and documents

The lint budget counts whitespace words: 6099 to 6097, delta -2. The project's normalized-word measure is a different count: 6155 to 6153, also -2. word-counts-final.txt labels both, the design-definition cut (-4), the Pilot budget output growth (+6 for implementation/validation and +23 for ideation), and on-demand timeline growth. Retain the -2 delta when merging the sibling workflow change; do not replace its budget step. Eighteen document dispositions are in document-dispositions.json; old Accepted ADRs remain immutable and ADR 0085 extends them. Adopted 0.41.0 READMEs are outside this task.

## Not provable now

A released live third-dispatch hold, delivery speed, RoboRev and hosted CI were not run or measured here. Four optional historical-corpus design-check tests skip without their existing corpus environment variables; no new tests skip. Product push and Draft PR creation belong to FO. CI cost per PR: not measured; no CI files changed.
