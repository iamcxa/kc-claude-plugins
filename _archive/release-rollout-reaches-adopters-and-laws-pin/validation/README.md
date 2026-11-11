# Independent validation — PR #838

Verdict: PASSED at `61529999eb4184b44328fe2fbad545b1b0b0ed92`.
Base: `e8664a72b0f904e5dda3c391d52ab3abaca876b4`. Date: 2026-11-11.
Validation used a git archive in `/tmp/rollout-validation-838/candidate`, never a newly created worktree. `artifact.json` binds all six changed files to candidate bytes. Product files, branches, adopters and workflow task frontmatter were not changed.

## Captain acceptance — four steps, under five minutes

Run exactly:

```sh
env -u GIT_DIR -u GIT_WORK_TREE bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-rollout-reaches-adopters-and-laws-pin/validation/acceptance.sh
```

Prerequisites: this task's existing repository containing the pinned commit, Git, Python 3, bash and the normal repository lint dependencies. The script exports into a new `/tmp` directory, contains four numbered steps and runs without GitHub access, credentials or the adopter list. No graphical screen changed: the observable surface is command output.

1. Expect `Candidate 61529999eb4184b44328fe2fbad545b1b0b0ed92 exported`.
2. Expect `Ran 23 tests` and `OK` (elapsed time varies).
3. Expect one `fleet/both` fixture row ending `pin owed; sync README, merge, then move pin`, a second `fleet/missing` row quoting `Not Found (HTTP 404)`, and `Expected rollout exit: 1`.
4. Expect lint PASS, `5939 of 5939 words`, no repeated passage, and `Acceptance passed`. Script exit 0.

The validator ran these bytes from a fresh `bash --noprofile --norc` shell; `acceptance.log` and `acceptance.exit` are the observed output and exit. This is a local CLI smoke/regression walk, not proof of live adoption, human merge behavior, discovery completeness, hosted deployment or model obedience. The separate live run is below.

## Acceptance evidence and falsifiers

| Criterion | Executed evidence | Error caught |
| --- | --- | --- |
| AC-1 | `tests.log`, `original/mutation-1.log` | Dropping the last listed row fails exact three-row output. |
| AC-2 | `tests.log`, `original/mutation-2.log` | Turning a README 404 into nothing owed fails the exit/diagnostic assertions. |
| AC-3 | `tests.log`, `original/mutation-3.log` | Including the release marker in workflow comparison creates false debt and fails. |
| AC-4 | `tests.log`, `original/mutation-4.log`, `pin-skew/readme-target-violates-ac4.log` | SHA equality creates false debt for identical laws; targeting the README tag hides released-tag debt; both are rejected. All three laws paths, unknown pins and absent installation are exercised. |
| AC-5 | `original/proof-results.json`, `original/legacy-*.txt`, `word-counts.json` | Eight stdout/exit comparisons match base with `cmp`; altered legacy output fails `cmp` in `original/mutation-legacy.log`. Original six test methods remain byte-identical. |
| AC-6 | `tests.log`, `original/mutation-5.log`, `integrity/proof-results.json` | Silent failed search, ignored incomplete/capped results, first-page-only and short-page returns all fail. Search diagnostic exit remains advisory. |
| AC-8 | `live-summary.json`, `live-hand-checks.json`, `live.log`, `live.py` | Two validator-selected public-state-known repos independently match raw `gh api` reads; altered release and pin are rejected. |
| AC-10 | `lint.log`, `word-counts.json`, `original/mutation-lint.log` | Copied 12-word workflow passage fails lint. Independent Python/wc recount agrees; only release and adoption grow. |
| AC-11 | `tests.log`, `original/mutation-6.log`, `artifact.json`, `local-list-preflight.json` | Missing/unreadable local list cannot succeed; no adopter list in product/state trees. |
| AC-12 | `order/proof-results.json`, `order/before-amendment.log`, `order/missing-order-mutation.log` | The exact both-owed fixture fails on a1a35a714 and without the order suffix; five single-debt/no-debt outputs and exits remain identical to a1a35a714. |

AC-7 and AC-9 are superseded by Captain amendment 1; they were not reimposed. Amendment 2 retains AC-4 and adds AC-12. `dispatch-strict.log`/`.exit` rerun the corrected validation-record criterion wording check.

`tests.log`: 23 tests pass. `original/proof-results.json`: eight controls; `order/proof-results.json`: five byte/exit comparisons plus missing-order and observable-row checks. `integrity/proof-results.json`: five read-integrity mutations and two caller/provider checks. All mutation commands ran with `python3 -B` in disposable copies; original files were preserved. `integrity/tests-before.log` independently reproduces five failures against ba98f3ca9. Provider file size is refreshed in `provider-probes.log`, not assumed from the implementation's older snapshot.

## Live boundary and privacy

The exact candidate ran with the explicitly assigned local list. Its network access was initially rejected by automatic approval review over possible unapproved metadata disclosure. An offline preflight then verified all 11 rows name only the six repositories already named by the task/public state and allowed owners/paths; that same check executes before any request. The retry was approved and completed. No unresolved network or permission block remains.

`live-summary.json` saves counts and exit only, plus date/candidate identity: 11 listed, four unlisted, no unreadable rows, no sync/pin debt, no search failure, exit 0. Raw live output and the list were never saved or committed. Two hand reads deliberately cover an installed pin (`iamcxa/kc-claude-plugins`) and absent installation (`iamcxa/qnow`); qnow's absence agrees with Captain-authorized removal recorded in implementation message 3.

`privacy.json` binds the public-state reference and confirms the two discovered names absent from that branch occur in neither the candidate nor the validation evidence. Evidence retains no discovered private names. No adopter write, product push, PR comment, review request, ready action or merge occurred.

## Independent review dispositions

RoboRev job 1725: its released-tag comparison observation was accurate; treating it as a comparator defect contradicts AC-4. `pin-skew/` reruns the real-checker old-README example (old checker exits 0; newer checker exits 1) and rejects the proposed README-target comparator. Captain amendment 2 settles the decision: keep released-tag debt and print sync, merge, then pin on a both-owed row. Candidate satisfies it. No remaining Material finding from that review.

RoboRev job 1727: the asserted matching-refs pagination defect is unsubstantiated. GitHub's own endpoint documentation declares no page/per_page parameter or threshold (`sources.json`); `refs-probe.json` freshly observes 49 component refs and 165 repository tags without Link, with identical results using `--paginate` and forced page parameters. `Github.releases` is unchanged from ba98f3ca9. The separate survey correctly repaired search completeness and omitted file content; current fixtures, before/after failures and mutations independently detect those gaps. Hypothetical undocumented backend truncation remains a Deferred risk: a supported response silently omitting a published release would make it Material under AC-1/AC-4. No infinite-capacity claim is made.

The FO's chief-engineer decline is justified for this candidate: repeated report headings include assessment, the Captain's order amendment and a wording-only correction, rather than four failed attempts at one mechanism. The two review findings have different causes; each normalized symptom has two dispatches, not the third that would independently owe a call. `role.log` exits 0 with the two advisory step-back reminders. The plain repair-count decline is allowed by ADR 0026. Answers: still the original read-only post-release report; both disputed gaps are testable now; deleting the comparison/order/read-integrity checks loses the named false-current/error/order protections. No new Material, Needs decision or Polish finding is open.

## Required checks, scope and remaining limits

- `adr.log`: exact installed 0.38.1 `adr_lint.py docs/adr --since e8664a72b0f904e5dda3c391d52ab3abaca876b4 --require 0075`, exit 0, 68 records. ADR 0075's Captain quotes and local-list amendment match the task; ADR 0017 explains version-skew harm.
- `number-refreshed.log`: number guards PASS at the exact candidate after remote state refresh. The first sandbox run's stale-fetch warning remains in `number.log`; it is not the final evidence.
- `comments.log`: 408 added code lines, one ADR link comment, 0.2%, below 5%; the comment was read and explains absent-install policy.
- `design.log`: presentable, exit 0; historical Scope check explicitly not run by this helper at validation. Task and amendments were manually read; no UI surface was declared.
- `dispatch.log`: 12 records complete, exit 0; `dispatch-strict.exit`: 0. All implementation follow-ups were read; original list placement is superseded, not silently kept.
- `docs.log`: ADR 0075 and maintain-flow are updated in the overall base/head diff. Later implementation reports correctly call them unaffected by the narrower amendment/read-integrity follow-ups. Adoption and root CLAUDE pointer match installation/merge authority. No altered diagram needs rendering.
- `word-counts.json`: release documents 778 to 897, adoption paragraph 70 to 95, workflow 5939 unchanged; independent `wc -w` agrees, other moments unchanged. No per-dispatch wording growth. New report diagnostics occur only at release time. Off-package prompts remain unmeasured.
- `pr.json`: hosted PR head matches; observed tests/checks succeed and docs deploy is skipped. This does not establish branch-required checks, approval or merge. RoboRev job 1728 clean is the FO's recorded observation, not a daemon rerun by this validator.
- No model replay or actual adopter rollout/pin writes were run. Accepted criteria exercise the read-only report plus the named human approval step; they do not claim automatic execution. Search's access/index/scope limits remain explicitly advisory, so this does not prove all existing adopters were discovered.
- CI configuration, versions, laws and dependency declarations are unchanged. Per-PR billed CI cost was not measured; no new CI job/trigger cost is claimed.

Goal sufficiency: the real list and failure fixtures expose per-workflow debt/unreadability; the release entry point names the command, ownership and Captain merge boundary. Minimal necessity: the script/tests provide the accepted report and falsifiers; the three retained text locations each cover a distinct release/install entry, and ADR 0075 preserves the ruling. No extra delivery authority or generic fleet infrastructure was added. FO retains the gate and any later product publication/adoption actions.
