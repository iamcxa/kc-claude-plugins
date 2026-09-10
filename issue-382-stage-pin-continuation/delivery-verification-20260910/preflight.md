# Maintenance delivery preflight

Initial preflight 2026-09-10 08:40 UTC; canonical feedback refreshed 2026-09-10T08:44:47.082672+00:00. Advisory packaging only; First Officer retains delivery orchestration.

**PR #390 has no newly identified in-scope source defect. Its body needs correction. The two maintenance repairs need one small integration edit before combined delivery.**

## PR #390

Current Candidate: `f18c697db6751c473f2ff7618be6b87b671e72bf`; main: `6b408ac102978d4bbf3614a7109934191520aa9b`. GitHub reports OPEN, non-Draft, MERGEABLE/CLEAN. All three advertised checks complete successfully. The portable contract, frontmatter, release metadata and version checks ran; GitGuardian passed. The release-only route job intentionally skipped native runtime and ablation steps. Those skips are not missing ordinary-PR checks or fresh native evidence.

Reviewed the exact seven-file GitHub diff, retained independent acceptance report, and prior integration report. Six candidate files—including loader and loader tests—are byte-identical to accepted source `1d5139568122a3af97cbc28333171df3bc2e27be`; only the shared full contract entrypoint also gained main changes. Existing source acceptance remains 5/5, with both historical findings closed. Current hosted portable coverage checks the merged entrypoint. No redundant validation round is indicated by this documentary drift.

The exact-head [canonical feedback record](feedback-observation.json) has an empty retained population and empty dispositions. A repository-explicit PR view, complete typed GraphQL thread pagination, complete paginated REST reviews, and matching after-view all identify the same head and author. The [full canonical input](feedback-canonical-input.json) is retained as the exact UTF-8 bytes hashed below; the raw before/after and page reads are preserved. Conversation comments are outside this canonical population. This is an advisory observation, not a state-stage report or boundary mutation.

PR feedback: {"complete":true,"dispositions":[],"fingerprint":"sha256:d0d171e7c5133b1da19c351ccc1ac81fb096c10bc49833fbf97c747e870a7377","head_sha":"f18c697db6751c473f2ff7618be6b87b671e72bf","items":[],"pr_number":390,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1","stack_layer":"single"}

The old body names the earlier Candidate and says current-main hosted checks are unverified. [Updated body](pr390-body.md) corrects both observations with the required headings, immutable audit link, and skipped-runtime boundary. Issue #382 stays OPEN for deferred legacy-task recovery. PR #321 remains OPEN at `abbe926929af915c2bbb8bb243eca0f6e3ac11f2`, shares five paths, and is not absorbed; historical conflicts are not a current combined-landing result.

## Separate POC close repair

Candidate `1eae2f5a5467b4600783eaedc671cf5cd57d1969`, based on current main, changes exactly the approved three paths. Its clean working tree and committed bytes match every fingerprint in the retained `poc-close-repair-report.md`. Existing real-Spacedock regression, full contract and whitespace-check passes are reused. [Draft body](poc-close-repair-draft-body.md) states the repair and evidence limits. The original POC is archived at state commit `b1e54319daa3d64ec82045cce69fb3b32f58b108`, `_archive/skills-mcp-dev-flow-feedback-poc/index.md`, with accepted direction `change`; task completion does not turn the experiment into a positive improvement result.

## Integration order and remaining evidence

Land #390 first, then integrate the close repair. Only `kc-dev-flow/skills/continue-dev-flow/SKILL.md` overlaps, in disjoint hunks. Read-only in-memory accounting of the exact combined text confirms:

| Selected work | Combined bytes | Existing ceiling |
| --- | ---: | ---: |
| Direct POC implementation | 40,028 | 40,000 |
| Pilot ideation | 40,065 | 40,000 |

Each candidate passes individually. Landing order does not eliminate this combined limit failure: the repair integration needs at least 65 bytes removed from the shared skill while preserving both behaviors. Run the existing affected contract check on that changed combined candidate; individual green evidence does not cover it. Native release-route proof belongs at release, and installation/adoption evidence belongs after publication. No new workflow, permanent gate, CI change, or model experiment is proposed. CI cost was not measured.

The [evidence record](evidence.json) contains exact file counts, fingerprints, all eight static measurements, and accounting method. No candidate, branch, workflow state, installed cache, PR, issue, or external message was changed. The foreign worktree remains at the accepted earlier source and was read only.

**Next concrete delivery step:** First Officer publishes `pr390-body.md` to #390 and reads back the exact Candidate and non-closing issue reference, using the approved delivery sequence.
