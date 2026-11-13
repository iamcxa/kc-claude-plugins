# Independent validation review

Candidate: `ef9aaffcbc48d6f17dd2e1dd744c4ffb5862d0f8`, PR #860; base `8125e6d516d32abbf79c6772de10cde2c20900a8`. Candidate code was read and executed from Git archives. Only disposable export bytes were mutated; the assigned product worktree and branch were preserved. This validator did not implement the candidate.

## Exit-code consumers

The package-wide Python search found one runtime consumer of this CLI's exit: `kc-dev-flow-2/scripts/pr_watch.py:447`, function `seeds`. It passes explicit task-file paths after reading their alignment section. Exit 0 emits no refusal; exit 1 with stdout emits the existing seed-fields reminder; any other nonzero result uses the existing error-report branch. A missing file before the subprocess is already caught as an OSError. The supported valid-file and invalid-field behavior is unchanged.

`check_consumers.py` runs the real checker subprocess for valid input (0), invalid fields (1), invalid encoding (1), and a file removed after the caller's read (2). The pre-read missing-file case invokes no subprocess and emits an error. Results in `consumers.json` prove five cases, including the newly reachable exit-2 branch. The controlled removal models a race; it proves error forwarding, not general race recovery. Compared with the base's missing-seed exit 1, that race now uses an error-report line rather than a seed-field reminder; this matches the accepted usage-error distinction and never clears a hold or hides the error.

`dispatch_records.py`, `laws_check.py`, `delivery_gate.py`, `validation_security.py` and `dispatch_stage.py` import helper functions/constants rather than consume this CLI exit. The two `script("design_surfaces.py")` calls in `laws_check.py` check script availability before importing helpers; they do not run the CLI. Their full package tests are included in `suite-results.json`. Human workflow references keep explicit-file semantics; this validation makes no model-following claim.

## Criterion evidence and falsifiers

- AC-1: `ac-1.log` covers valid and invalid collisions and dotted names in both modes. Three executed mutations remove fallback, truncate the dotted name, or force success; all are caught.
- AC-2: `ac-2.log` covers suffixless input without a directory and exact-file priority. Requiring a directory and overriding the exact file both fail the check.
- AC-3: `ac-3.log` covers missing names, missing `.md`, orphan directories, dot/root, and invalid UTF-8 seed input. Removing the usage guard or mapping encoding failure to usage both fail the check.
- AC-4: `probe-summary.json` and `adopter-counts.json` contain 54 live collision files, 108 mode comparisons, 108 stable-byte checks, 108 unchanged explicit results, 108 equal aliases, zero unavailable and zero candidate alias tracebacks. The base has 54 default-mode tracebacks. Candidate results are 24 successes and 84 retained refusals. Two corpus mutations remove resolution or add a refusal to existing file checks; both are detected. All nine valid-Python mutations were independently run and restored (`mutation-results.json`, `mutation-summary.json`).

The inherited probe/mutation evidence scripts were reused with one transport adaptation: `--repository` supplies Git objects for `git archive`, separately from `--source`, which is the disposable candidate export. No global Git environment was supplied to corpus subprocesses, so each adopter's normal local history remains its source. Public synthetic diagnostics are retained; all private results remain in-memory and are saved only as counts.

## Documents and change necessity

The four product lines select a regular file or reject unresolved input. Without fallback the baseline crash returns; without the guard unresolved directories reach the old reader. Added subprocess tests cover those promised behaviors; the previous missing-seed expectation is moved to the usage-error test, while the encoding test remains. No rule, dependency, instruction, architecture record, migration or version change is added. No new comments were added; comment-ratio is 0/64 added code lines, 0.0%, below 5% (`comment-ratio.log`).

`doc-impact.log` lists four retained architecture decision records; each implementation disposition is confirmed:

- `docs/adr/0041-seed-admission-enforces-required-fields.md`: unaffected; required seed fields/checks are unchanged.
- `docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md`: unaffected; amendment comparison functions are unchanged.
- `docs/adr/0076-a-journey-workflows-new-seed-records-its-story-or-none.md`: unaffected; selected-file story and extension checks are unchanged.
- `docs/adr/0077-a-task-budget-counts-cycles-and-past-it-the-question-returns-to-the-captain.md`: unaffected; Budget grammar, Worth questions and cycle counting are unchanged.

## Limits assessed

- Current corpus has grown from the implementation's 47 collisions to 54. Current evidence is its own observation, not a reassertion of the earlier count.
- The original report's absent historical-name file is no longer absent in the checked roots: one archived file and companion directory are now present. Its two modes preserve bytes, explicit results and alias equality (`historical-match-counts.json`, `historical-replay-counts.json`). No claim authenticates those bytes as the original event-time task.
- Conditional frozen/historical inputs remain undeclared; skipped tests stay skipped. Live-corpus replay does not fill in those fixtures.
- Lifecycle instruction counts were rerun with the same passage inventory (`reading.json`). Files/counts are unchanged. This is neither total runtime reading nor demonstrated time savings. No rendered Mermaid or agent lifecycle run is claimed; there is no changed UI or diagram.
- Local tests use Spacedock source 0.28.0 with runtime 0.27.2; hosted CI pins its own source. Hosted checks, RoboRev review, merge, publication and released-adopter behavior remain FO-owned and are not certified by this validation. PR metadata confirms a draft, open, unmerged PR at the recorded head (`pr-identity.json`).
- `number-guards.log` exits 0 with no findings but warns that remote state fetch failed and uses local refs. No number reservation, task Number guards section, architecture record or migration changes exist; this is not fresh remote-reservation evidence.
- Installed Codex/Claude helper scripts checked here have identical bytes. Their workflow reference differs by runtime adaptation; loaded Codex hash is recorded in `package-provenance.json`. Candidate test source is pinned separately in `candidate-bytes.json`.
- CI cost per PR was not measured. CI triggers and jobs are unchanged.

No Material, Deferred risk, Polish or Needs decision finding was established. The listed evidence limits do not alter the accepted scope or the supported command behavior. Passing this validation recommends the existing gate; it does not authorize delivery.
