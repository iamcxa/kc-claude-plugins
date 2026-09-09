# batch-c5a7274dd07c — ship-flow repair after batch ab2fb263

Plan receipt c5a7274dd07c4ee1 (session plan-flow-session-2026-09-09-shipflow-repair); approval go · 12 workspaces · concurrency 1 · repair 2 · Pilot (Captain 「approve」 2026-09-09).
Order: DEV-134 → DEV-147 + DEV-135 (one worker, one PR) → DEV-148 → DEV-149. Repo iamcxa/kc-claude-plugins, base main. Captain merges each PR by hand.
Stations per docs/ship/README.md; every FO decision and every worker Evidence block is recorded here.

## Decision log

- 2026-09-09T03:55:26Z — batch opened.
- 2026-09-09T04:13Z — **DEV-134 accepted by the installed station itself** (first acceptance in four batches without an FO override; the block's without-it paths are .md). FO verified at 686f86fb: AC-1 exit 0, AC-2 refuses naming the untracked path, contract-test exit 0, without-it removed exit 1 (worker reported 2 — both non-zero, different refusal branch), 0 comment lines added. PR #395 Draft. Review station: code-reviewer dispatched. Brief error: kc-ship-flow/README.md does not exist (worker read references/stations/accept-evidence.md).
- 2026-09-09 — #395 review: F1 (tracked check uses the checkout's index, not the candidate tree) confirmed; repair round 1 dispatched (cat-file -e at CANDIDATE_SHA + a CANDIDATE_SHA≠HEAD contract case). Everything else clean: refusals byte-identical, fixtures synthetic, revert flips both cases, no extension remnants, 0 comments.
