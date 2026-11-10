# Running the acceptance script

There is no graphical surface in this change. The five steps are comments and commands in acceptance.sh; run the whole file unchanged in a fresh Bash shell.

Prerequisites: the assigned local repository contains candidate 39a76c68836f471fc0c42c18eab12641196860ed; Python 3, Git, tar, wc and tr are on PATH; /Users/kent/.local/bin/spacedock is the real 0.27.2 CLI. No login or credentials are needed by the script. It creates an export and disposable fixture repositories under /tmp and does not write the product checkout or send prompts to live reviewers.

Expected observations: candidate SHA/export path; 2 tests OK for commit and recovery; 4 tests OK for refusals/routing/model/arguments; 5 tests OK for raw bytes/compatibility; lint says 5939 of 5939 words, followed by PASS. Logs are in evidence/acceptance.log from the validator's unchanged fresh-shell run.

Limits: this small script does not cover all package tests, every mutation, native reviewer execution, adoption, hosted CI or the user's delivery decision. Those have separate evidence or remain explicitly unverified in validation.md.
