# Implementation evidence

Candidate: `0a5c37f091daec6909a76d443219c655b17d534e` on
`spacedock-ensign/validation-rerun-survives-repaired-history`, based on
`546a136386c94c58e430c91a6f3457b38bd73880`. `candidate.json` binds the three
changed files by SHA-256. ADR 0045 was Accepted at the base, SHA-256
`98b42893536879b66eb945c8ca5546f142bd89f1b08d68d41a9cb61c7ba7eea0`.
The approved ideation resolution overrides the generic ADR skill's no-edit rule:
one in-place amendment, no new number.

## Decisive checks

- `suite-final.log`: all 136 dispatch-record tests pass, with the optional native
  builder skipped. `native-builder.log` separately exercises that exact test with
  the assigned Spacedock binary and plugin; exit 0.
- `focused-no-cache.log`: all 11 new tests pass after clearing the worktree's
  script cache, with `PYTHONDONTWRITEBYTECODE=1 python3 -B`.
- `mutation-baseline.log`: the final test fixtures against the released 0.38.1
  code produce six assertion failures. This is the canonical before-fix check.
- `mutations.json`: ten independent behavior mutations are all killed by their
  named tests; the additional baseline row also fails as intended. Disposable
  script copies omit all Python caches and run with `python3 -B`.
- `extra-mutations.json`: removing historical error handling holds all five
  recorded repaired qnow commits; suppressing raw identity checks wrongly clears
  the real unruled web task at `fda02ff5`; allowing same-commit rulings fails an
  existing test; omitting the ADR recommendation fails ADR lint, specifically for
  the missing recommendation and with no unrelated pointer error.
- `replay.py` calls the actual `check_validation_rulings` entrance on saved-record
  paths in disposable detached state checkouts. `replay.json` retains unfiltered
  output and exit codes for both the released tag and candidate; `verify_corpus.py`
  independently requires the approved 161-event, 73-task outcome pairs and the
  two named changed tasks. Immutable state SHAs are retained in the JSON.
- `skill-lint.log`, `adr-lint.log`, `number-guards-live.log`, `comment-ratio.log`
  and `design-surfaces.log`: required guards pass. The first number-guard run in
  `number-guards.log` warned that the state fetch was unavailable in the sandbox;
  the network-enabled rerun completed without that warning.

## Document impact and boundaries

`doc-impact.json` lists ADR 0045 (updated), ADR 0048 (unaffected: worker completion
and publication rules are unchanged), and `learning.md` (unaffected: no adopted
practice changes). No new diagnostic grammar, workflow text, CI trigger, version
or number is introduced. Comment ratio is 0.0%, within the 5% maximum.

The raw amendment search and parsed-identity history implement the approved proof
rule. Current and pinned Captain records remain strict. Two historical task paths,
an unclosed fence hiding a report and undecodable historical bytes deliberately
retain their evidence holds; this work adds no recovery for them.

`before.log`, `after.log` and `focused.log` preserve exploratory runs. Two fixture
premises were corrected without changing expected product behavior: the malformed
gate scalar now has both outer quotes and invalid inner quoting (so `unquote`
really raises), and amendment-using fixtures name amendment 1 in their dispatch
checklist. The final baseline and candidate checks above supersede those runs.
The earlier `mutation-adr-lint*.log` probes include setup errors; only
`mutation-adr-lint-only.log` is the decisive ADR falsifier.

`acceptance.sh` provides a fresh-clone replay command taking the source worktree,
output directory, assigned package root and adopted workflow directory as explicit
arguments. Its commands were exercised individually; the wrapper itself received
`bash -n`, not another complete network replay.

Product branch publication, a Draft PR, RoboRev and hosted CI are not run by this
worker and remain First Officer-owned. CI cost per PR was not measured; no CI
configuration changes. The prepared PR title/body is retained at
`/tmp/impl-validation-rerun-survives-repaired-history-pr.md` for First Officer.
