# Cycle 2 phase 2: authorized F3 repair

`candidate.txt` and `artifact.json` bind the one local repair commit. `boundaries.json` proves this phase changes only `design_surfaces.py` and `test_laws_check.py` and matches the concrete phase-1 proposal. `function-boundaries.json` hashes the 55 other functions and verifies the module bytes outside `move_defects` are unchanged from the prior candidate. The shared `unfenced`, `unmarked`, amendment parser, public check/seed entry points and `laws_check.py` remain unchanged. F2 exception handling is outside this repair.

The promoted five tests cover the tilde-fenced false marker, its backtick control, real marked replacements, no-replacement waivers and record-only amendments. `red-before-fix.log` observes one assertion failure and four passing methods before the runtime repair. `l4-green.log` runs all 19 L4 methods after the repair. `reverted-f3.json` and its log independently show the promoted F3 test failing after only the temporary design helper is restored to the prior candidate. `reverted-f1.json` retains the three Cycle 1 negative controls; `mutations.json` retains the nine existing injected-regression rejections. The temporary copies exclude bytecode and run `python3 -B`; neither negative probe reverts the product checkout.

`tests.json` records every package test-file command; `tests-summary.json` supplies case/skip counts and local tool versions. `run-tests.py` checks coverage against the CI workflow, asserts no bytecode at startup, executes each command with `-B`, verifies source digests and removes bytecode created by child processes at exit. The local CLI is Spacedock 0.27.2 with plugin root 0.27.3; CI pins both to 0.27.2. This is local evidence, not hosted CI or real model/worker execution.

`check-comparison.json` compares check/seed error verdicts against the task's pinned base on the three archived state tips. `check-comparison-summary.json` binds its candidate and inputs. The raw byte boundary separately proves compatibility with the immediately preceding candidate; inherited gate behavior on fenced examples is retained. The new fence filter is confined to the L4-only input helper.

`corpus-inputs.json` freezes the same three full-history ranges as validation-2. `corpus-reconciliation.json` separates the seven expected L4 events from existing L3 cannot-judge history debt; `corpus-comparison.json` requires every L4 headline and diagnostic to equal the prior candidate at those ranges. `current-tail.json` additionally pins the local tips observed after those snapshots and records their L4 outputs. No remote-tip fetch or hosted activation is claimed.

`checks.json`, `adr-explicit.json`, the named logs, `doc-impact.log` and `doc-verdicts.json` record required checks and each affected-document disposition. The law document retains +242 words within its approved +250 bound; no version, workflow, CI trigger/job or adoption pin changes. CI cost per PR/state push is unmeasured. Product push, PR edits, RoboRev, independent validation and D2/AC-7 hosted activation remain FO/Captain work.

To reproduce without overwriting the durable records, copy this directory to scratch and use the exact candidate checkout as `<worktree>`. Python 3, Git, the installed 0.37.0 package used by `checks.py`, declared local Spacedock executable/plugin root, task/workflow paths and state inputs are required. The source/test drivers and fixture copies declare those local paths; substitute equivalent available checkouts explicitly on another machine. Clear package bytecode before the suite; the mutation drivers create fresh temporary packages without caches.

```sh
python3 -B run-tests.py <worktree>
python3 -B reverted-f3.py <worktree>
python3 -B reverted-f1.py <worktree>
python3 -B mutations.py <worktree>
python3 -B compare-checks.py <worktree>
python3 -B run-corpus.py <worktree> corpus-inputs.json dev2
python3 -B run-corpus.py <worktree> corpus-inputs.json qnow
python3 -B run-corpus.py <worktree> corpus-inputs.json relay
python3 -B verify-corpus.py
python3 -B compare-corpus.py <prior-cycle-1-phase-2-evidence-directory>
python3 -B run-tail.py <worktree>
python3 -B checks.py <worktree>
```

For the explicitly named accepted records, from the candidate checkout run the recorded installed-package command in `adr-explicit.json`: `python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0/scripts/adr_lint.py docs/adr --since 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1 --require 0016 0017 0041 0057`.

Test/check drivers and rejection controls must exit 0; the rejection drivers require their expected assertion failures internally. Each full corpus CLI still exits 2 for pre-existing L3 ambiguity, while reconciliation must prove exactly 3/3/1 L4 events and no change from the prior candidate. No overall-history green or task closure is claimed.
