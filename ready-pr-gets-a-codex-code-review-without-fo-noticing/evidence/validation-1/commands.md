# Validation commands and limits

Start: 2026-11-13 22:05:06 Asia/Taipei. Source: clock tool UTC plus eight hours.
Candidate: 1c8a29faf402ef6d7018c298f59bad58d38cfb1d.
Base: 6a1eaf837bd6087cd0b8b665dc19beaed3c44dff.
Public repository and live Draft PR identity: repository.json and pr.json.
Candidate was exported with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-ready-pr-gets-a-codex-code-review-without-fo-noticing archive 1c8a29faf402ef6d7018c298f59bad58d38cfb1d | tar -x -C /tmp/dev2/kc-claude-plugins-3042bb224e995ded/ready-pr-gets-a-codex-code-review-without-fo-noticing/validation-1/candidate`.
The candidate has one inserted sentence in one file (candidate.diff); no product bytes changed during validation.
The installed package scripts are version 0.41.0, at the dispatch's explicit /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0 path.

## Commands rerun
All exact argument lists, working directories, exit codes and expected codes are in results.json.
- `rg -n -F -- 'when FO marks a PR ready, it comments \`@codex review\` on the PR once.' kc-dev-flow-2/extensions/codex/EXTENSION.md` — ac5.log, exit 0.
- The same `rg -n -F` search on a fresh Python-created copy with only the added sentence removed — falsifier.log, exit 1 (expected); results.json records the exact arguments.
- `python3 -B kc-dev-flow-2/scripts/lint-skills.py` — lint.log, exit 0.
- `python3 -B kc-dev-flow-2/extensions/codex/test_codex_review.py` — codex-tests.log, exit 0, 36 tests.
- `python3 -B <package>/scripts/adr_lint.py docs/adr --since 6a1eaf837bd6087cd0b8b665dc19beaed3c44dff` — adr-lint.log, exit 0, 77 records.
- `python3 -B <package>/scripts/comment_ratio.py 6a1eaf837bd6087cd0b8b665dc19beaed3c44dff 1c8a29faf402ef6d7018c298f59bad58d38cfb1d --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2` — comment-ratio.log, exit 0.
- `python3 -B <package>/scripts/doc_impact.py 6a1eaf837bd6087cd0b8b665dc19beaed3c44dff 1c8a29faf402ef6d7018c298f59bad58d38cfb1d` — doc-impact.log, exit 0.
- `python3 -B <package>/scripts/design_surfaces.py check /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/ready-pr-gets-a-codex-code-review-without-fo-noticing.md` — design-check.log, exit 0.
- `python3 -B <package>/scripts/dispatch_records.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/ready-pr-gets-a-codex-code-review-without-fo-noticing` — dispatch-records.log, exit 0; implementation requirements trace to amendment 1 and existing stage duties.
- `TMPDIR=/tmp/dev2/kc-claude-plugins-3042bb224e995ded/ready-pr-gets-a-codex-code-review-without-fo-noticing/validation-1 bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/ready-pr-gets-a-codex-code-review-without-fo-noticing/evidence/validation-1/acceptance.sh` — acceptance.log, exit 0; only TMPDIR confines disposable files to the assigned scratch, and the script removes them.
- `python3 -B <package>/scripts/role_triggers.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state ready-pr-gets-a-codex-code-review-without-fo-noticing` — exit 0 at entry: budget 1 implementation / 2 validation cycles; spent implementation 1, validation 1.

## Judgment
PASSED, AC-5 only. The English sentence preserves the Captain's actor (FO), occasion (marking ready), action (comment requesting Codex review), and once at that occasion. The established request spelling is already used by the adjacent repair rule. It adds no automation, security-result condition, exactly-once guarantee, or new request machinery.
Its own “When marking ready” entry puts the instruction at that event; “After a repair” remains a distinct occasion and is unchanged. Without the addition, the search fails and the old text has no ready-event instruction. This establishes necessity and sufficiency for the accepted text-only outcome.
No Material, Deferred risk, Polish, or Needs decision findings. AC-1 through AC-4 and the old automation stop condition are withdrawn by amendment 1.
The unchanged extension tests protect the reader's existing review-result interpretation, not agent compliance. Removing the new sentence would not fail those tests, which is why AC-5's distinct removal falsifier was run.
The affected-document check lists zero other documents; the sole changed extension document is updated.
No additional ADR was claimed/reserved/changed, and no Number guards section exists: number_guards was not rerun. The implementation's fetch warning followed by a fresh pass is not promoted into new validation evidence.

## Limits assessed
Implementation's one-file scope, sentence search, lint, unchanged workflow budget and documentation checks are independently confirmed. Its extension word counts are not a claim of lifecycle reading reduction; that withdrawn AC-4 measurement remains not measured.
Local review (RoboRev), hosted CI, live Codex requests/reviews, merge, adoption and publication were not performed by this validator. The live PR check confirms that FO has since opened Draft PR 867; this supersedes the implementation report's then-unverified PR opening only.
CI triggers were not changed; CI cost and duplicate-review cost remain not measured.
No full package suite, unrelated mutants, UI/browser run, or automatic exactly-once replay: none is part of the amended one-sentence outcome.
Lint itself does not establish host/workflow behavior or full Agent Skills conformance; passing local checks must not be represented as delivery.

## Captain acceptance
No user interface changed. Requires network, gh with GitHub access, bash, tar, rg, python3 and PyYAML.
Run the retained script from any directory; it downloads the exact public candidate and does not depend on the product checkout or deleted validation scratch:

```sh
bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/ready-pr-gets-a-codex-code-review-without-fo-noticing/evidence/validation-1/acceptance.sh'
```

Four steps and expected observations are in acceptance.sh: download the pin; show ready/repair text; delete the sentence and observe search exit 1; lint and 36 extension tests pass, ending `ACCEPTANCE PASS: 1c8a29faf402ef6d7018c298f59bad58d38cfb1d`.
Observed output is retained verbatim in acceptance.log. This does not send a review request or demonstrate provider delivery.

