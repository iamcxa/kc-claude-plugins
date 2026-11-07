# Independent validation of PR #802

Candidate: `37b1c0b7a9561ee48165cefbc9424a4390fe9d0a`.
Base: `ba055b8a7a55a787ac989c4cef52d07dd75661ad` (`origin/main` and GitHub PR base when read).
Profile: Pilot. Read date: 2026-11-07, Asia/Taipei; fresh GitHub capture started at 2026-11-07T01:36:11Z.

## Method and authority

The assigned product worktree was clean on `spacedock-ensign/codex-security-only-prompts-code-review`, at the candidate above. Both revisions were read with `git archive` into `/tmp/csopc-validation-37b1c0b7/{base,candidate}`. All candidate execution used those exports; mutations used a separate disposable export. All 1,574 candidate tracked blobs were subsequently compared to their Git object hashes, with no differences. No product edit, new Git worktree, Git config write, PR write, review request, push, ready action or merge was performed.

The loaded validation skill selects `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0` as the helper package. The dispatch's `.claude` ADR lint path was also run, with `--require 0039`; both checked 61 records and exited 0. For helpers needing Git metadata, `GIT_DIR` pointed read-only to the assigned repository metadata and `GIT_WORK_TREE` to the candidate export. This fixed the initial version-parity invocation's exit 128 (`not a git repository`); the corrected invocation exited 0. No candidate repair was needed.

The existing implementation proof scripts were read, checked, and adapted only to new export/output paths; all GitHub inputs were freshly collected into an initially empty directory. Base and candidate consume identical recorded API responses and the same clock. An additional independent raw-comment parser checked each changed output against the bot identity, summary marker, completed security SHA and off-head code-review SHA. Corpus entries cover 80 recent PRs; the separate #727 replay adds one further changed case, so that raw-marker check covers 29 changes in total.

## Acceptance evidence

| Criterion | Observed proof | Falsifier run |
| --- | --- | --- |
| AC-1: #727 requests code review | Base and candidate CLI both exit 4. Base prints the original no-evidence line for `5dee91fb7`; candidate prints `security-only=summary:6434584622` and the `@codex review` next line, with no `evidence=`. | Removing the branch or substituting `evidence=` fails three subtests. |
| AC-2: other heads unchanged | Fresh `gh pr list --state all --limit 40` for each named repository: 52 identical byte/exit pairs, 28 differences; all 28 are security-completed/current-head plus no code row on that head, and both readers exit 4. kc-paseo-plugins #71 and #73 remain byte-identical clean. | Dropping the code-row condition fails two subtests; dropping the security-head condition fails one. |
| AC-3: reader conditions | `python3 -B -m unittest test_codex_review`: 36 tests pass. Candidate tests against the base reader fail three subtests. | Five named reader mutations rejected with failures 2 / 1 / 1 / 3 / 3. |
| AC-4: once per head and idle route | Candidate watcher suite passes. `TasksTests` sends a security-only fact to `wait`, which returns the request with zero sleeps; a second tasks call adds none. Live candidate CLI `add --codex iamcxa/kc-paseo-plugins#42` followed by `wait` prints the request and persists `codex-asked=8d9a68b92`, with evidence `-`. | Candidate watcher test against base fails once; removing wait wiring errors, removing the asked mark fails once, and removing mapping fails once. The test also proves a new head asks again and the same head waits for a real outcome. |
| AC-5: words | `wc -w`: workflow 5939 -> 5939, identical bytes; extension 310 -> 325. Reader has two lines / 26 words; wait has two lines / 21 words. Routing lint passes with no budget change. | Adding one unapproved workflow word makes routing lint exit 1. Request wording and line limits are asserted in the mutation-tested tests. |
| AC-6: scope and required checks | Exactly the five design-listed paths changed. GitHub unit-test and parity jobs pass on the exact candidate; the latter's skill-frontmatter step is explicitly successful. Local routing, frontmatter and corrected version parity checks pass. | A sixth README path is rejected by the exact-path allowlist; changing the plugin version to 999.0.0 makes the parity check exit 1 with STALE. |

Commands and output for each check are in `checks-final.json`, `unit-tests.json`, `corpus.json`, `mutations.json`, `additional-falsifiers.json` and the primary evidence bundle. No network command requested or posted a code review.

At the final local read, `origin/main` had advanced to `ee6ca16fa6c2259fc8d040aaec23a0caba5ab080`; its seven new paths do not overlap this candidate. The merge base stays `ba055b8a7a55a787ac989c4cef52d07dd75661ad`, and `git diff --name-only origin/main...HEAD` still contains only the five approved files. GitHub still reports the candidate Draft/open with `mergeable: UNKNOWN`. This verdict covers the dispatched candidate and pinned base; it does not establish the later integrated revision or merge readiness.

## Complete local suite

All 23 CI-listed unit scripts exited 0: 1158 tests reported, including 11 optional skips. Skip counts by script are preserved in `summary.json`; the implementation report's skip categories match the actual skipped cases. Native Spacedock dispatch and observer recovery were additionally run to completion and exited 0. See `unit-tests.json` and the full logs in the evidence bundle.

## Other obligations and minimal necessity

`adr_lint.py docs/adr --since ba055b8a7a55a787ac989c4cef52d07dd75661ad --require 0039`, number guards, comment ratio, design-surface checks, dispatch-record validation and `git diff --check` all exit 0. Number guards have no declared migration path to check. Comment ratio is 0 added comment lines / 80 added code lines, within 5%; the added docstrings describe the current exit/output contract. Three dispatch records are complete.

`doc_impact.py <base> <candidate> --json` identifies ADR 0039 only: unaffected, because the finding-before-clean and same-head persistence rules remain intact and their tests pass. EXTENSION.md is updated with the accepted 15-word instruction. The shared workflow, its word budget, CI and version files are unchanged. No new ADR or number reservation is required by the accepted design.

Goal sufficiency is demonstrated by the historical real input, the 80-PR compatibility comparison, actual GitHub-to-reader-to-watcher CLI execution, and idle/wait persistence tests. Minimal necessity is supported by the base failures and eight reverse mutations: removing reader classification, consumer mapping, wait wiring or per-head persistence breaks the promised behavior. The two test files pin those boundaries, and the documentation addition supplies the accepted operator action. No retained change is unrelated to the goal.

## Limits and review-finding disposition

- F1 Deferred risk: the Codex summary marker is undocumented and can change. Released user/workflow: FO reading GitHub Codex results. Observable harm: none on the current 80-PR capture and #727 replay. Boundary: `value-ac[AC-1]` and `value-ac[AC-2]`, correct request classification without review-round evidence. Trigger: an unobserved future provider layout change; a supported live example producing a missed/false request or round miscount would make it Material. This carries the accepted design limit; it is not a new blocker or repair request.

No new Material, Needs decision or Polish finding was found. The implementation's stated limits were assessed individually:

- Failed code review on the current head plus completed security still gets the old exit-4 line. Confirmed by the reader subtests; explicitly excluded from this accepted slice.
- Security still running does not request code review. Confirmed by subtests; preserves the stated no-race boundary.
- No second escalation after the per-head request. Confirmed by watcher persistence/new-head tests. The accepted design leaves subsequent handling with FO and the Captain.
- Historical merged security-only heads remain read-only evidence, without a judgment about whether those merges were appropriate. The current corpus is a dated snapshot, not a census or future guarantee.
- Provider-marker drift remains F1 above; current captured inputs pass. Actual FO compliance with printed instructions and a future Codex review response were not simulated or requested.
- Implementation's hosted-CI limit is now resolved for this exact candidate: unit tests, version parity and skill frontmatter succeeded. The docs deploy job is skipped on the PR as designed; no deployment is claimed.
- Local Spacedock 0.27.3 dispatch/recovery checks pass; hosted CI independently passes its pinned 0.27.2 checks. The local optional skips are documented in the test summary; skipped historical/host-dependent scenarios are not represented as executed.
- RoboRev remains FO-owned and was not run by this validator. No new local review result, publication, adoption or merge approval is claimed. CI cost per PR was not measured; CI files and triggers are unchanged.

## Captain acceptance script

Run the sibling `acceptance.sh` from a fresh bash shell. It has four labeled steps: export exact revisions and check scope; run reader/watcher tests; read #727 from GitHub; check words, routing and ADRs. Prerequisites are the explicitly named local repository with both commit objects, Python 3, Git, tar, the named installed package and authenticated `gh` with network access.

Executed exactly as written with `bash --noprofile --norc /tmp/csopc-validation-37b1c0b7/acceptance.sh`; exit 0. Observed output is preserved in `acceptance.log`: 36 reader tests and 135 watcher tests pass, both live readers exit 4, the candidate prints the request, and the final line begins `ACCEPTANCE PASS`. The log's creation-to-last-write interval was 181.6 seconds, below five minutes. This command surface has no GUI screen.

The short script does not repeat the full 80-PR comparison, every mutation, the whole package suite or remote CI inspection. Those independently executed proofs are retained separately. A pass does not post a review request or authorize delivery.
