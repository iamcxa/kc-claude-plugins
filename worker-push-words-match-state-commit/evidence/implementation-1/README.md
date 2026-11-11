# Implementation evidence

Candidate: 2c499dab75eb7ca644637d9018c93e91986ba29d
Base: e8664a72b0f904e5dda3c391d52ab3abaca876b4
Branch: spacedock-ensign/worker-push-words-match-state-commit

## Result

AC-3 and amended AC-5/6 pass. AC-4 behavior passes, but its literal real-QNow-origin unchanged assertion is not met. Overall replay checker exits 1; do not treat this as an all-green implementation handoff.

Both released-package arms also completed their state sync normally: this experiment measured no behavioral improvement. It proves neither product acceptance for the replayed QNow work nor general improvement on other hosts.

## Runs

| Run | Model / effort | State commit | Interpretation |
| --- | --- | --- | --- |
| replay-implementation-release | gpt-6.1-sol / xhigh | 0cf440bc300955048d60ae79ef3118957774b46b | done; no deviation or publication-approval request |
| replay-implementation-candidate-1 | gpt-6.1-sol / xhigh | cd9fea336a90e951e71680a5f91bce58eba6bd99 | done; no deviation or publication-approval request |
| replay-implementation-candidate-2 | gpt-6.1-sol / xhigh | 6c6164ada9c4e0e5864021480efdbb5975121d81 | done; no deviation or publication-approval request |
| replay-validation-release | gpt-6-astra / xhigh | 88d69b9707579dc1933f67607ab190c7381c3829 | done; no deviation or publication-approval request |
| replay-validation-candidate-1 | gpt-6-astra / xhigh | 6cd752e078cb6f6b8ed0b6df6a606f1979c386f9 | done; no deviation or publication-approval request |
| replay-validation-candidate-2 | gpt-6-astra / xhigh | b6e56362c3e0b3f32f20b1f5523be6e5a1eda649 | done; no deviation or publication-approval request |

All six disposable state origins changed only refs/heads/spacedock-state/wf; all six disposable product origins stayed unchanged. Exact endpoints and clean final worktree states are in replay-final-endpoints.json. Models and final idle states are in replay-agent-final-status.json; all six were then archived. replay_dispatch cleanup succeeded for all six.

## Input and measurement limits

- Implementation state d0270c05af744bc7055fbbef7992bcc7269387e2 and code a8793b938deb12ff4d599a427998c28b4fe080f1; validation state 17ff37c875ab3a1a33bf0462bd6d815b7d616fae and code 32901fe5f34fb17ae9a5741cff88471d55e81288, base 706b01fdb04b5d0b17b213562296dc95eaa60368.
- Native implementation README merge conflicted on extensions and second-reviewer. The recorded FO follow-up authorizes retaining the historical adopter configuration and taking the package merge elsewhere, identically for both arms. Each implementation directory holds unresolved/resolved README files and its resolution diff. Validation merged cleanly. Neither resolution touched Dispatch facts; the two arm READMEs differ only by the new Pushes bullet.
- The scratch replay helper differs from repository replay_dispatch.py only in the approved HARNESS remote sentence. prepare_replays.py transparently resumes the refused native helper after the authorized manual README resolution; it does not modify the product helper.
- A first preflight cohort used a wrongly named code branch. It was canceled, excluded, archived and cleaned. The valid cohort uses fresh replicas and workers. Direct scratch-workspace launch failed with Operation not permitted; valid workers started in the approved FO workspace and moved into their isolated code roots.
- Host context, installed ensign guidance and ordinary memory remain available to the fresh workers. No causal improvement is claimed, especially since both release arms also passed.
- git ls-remote snapshots span setup as well as the valid runs. QNow refs changed on its real origin during that interval; qnow-changed-refs.json records the differences, including concurrent docs/browser-acceptance-rule and spacedock-state/dev2 commits. No unchanged-origin claim is made.

## Checks and falsifiers

- acceptance-tests.json: actual native context loading and exact two-file scope; baseline absence, missing/duplicate/misplaced bullet, extra file, wrong gate quote, missing budget raise/quote/loading moment are rejected. python3 -B was used; mutation fixture bytecode caches were cleared.
- state-push.json: actual Spacedock 0.27.2 pushes only the disposable state branch; without origin it prints local-only. Added-ref and no-push mutations fail its ref check.
- replay-results.json: four candidate behavior runs pass; injecting either a deviation or a publication-approval request into one candidate produces checker exit 1. Interpretation fields are the author audit of preserved reports/replies/activity summaries; reference boundaries are checked mechanically.
- static-results.json and lint-tests.json: repository lint and 47 existing mutations, ADR lint, number guards and comment ratio pass. Number guard reported a state-fetch warning; this candidate reserves/adds no number. comment ratio is 0.0%, with the default 5% maximum not enforced below 20 added code lines.
- Full workflow word count: 5939 to 5977. Dispatch facts including its heading: 300 to 338, correcting the design table's count by -3 on both sides. All three worker stages load the extra 38 words. Recorded implementation context totals are 1362 to 1400 and validation 1516 to 1554.

## Captain closure

Captain amendment 2 closes without delivery because neither release replay reproduced the bite. No product push or PR; preserve the local candidate. Reopen only with a recorded real dispatch showing the misclassification.

## Handoff

Product branch push, Draft PR, RoboRev and hosted CI are FO-owned and were not run. No version or CI configuration changed; CI cost per PR was not measured. Prepared PR text is /tmp/impl-worker-push-words-match-state-commit-pr.md. The existing Captain approval covers the +38 budget step; it does not erase the unresolved AC-4 origin assertion.
