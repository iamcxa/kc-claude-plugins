---
id: tgta74m7bxs4jypvs2mvwwnt
title: "Close kc-dev-flow S2 through Release PR #221"
status: validation
source: "Captain-approved S2 release closeout after all four implementation tasks exited, 2026-08-14"
product: kc-dev-flow
sprint: S2
started: 2026-08-14T14:59:28Z
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/worktrees/kc-dev-flow-s2-release-221-aad7
issue:
pr: pr-merge:221
mod-block:
design: required
lane: main
---

## Problem

All four Captain-approved kc-dev-flow/S2 implementation tasks have exact-revision validation and merged delivery evidence, so the Roadmap release hold is clear. Release PR #221 now owns the generated version, changelog, manifest, and marketplace bytes, but no active task binds its exact candidate, pre-publication compatibility receipt, Captain merge authority, published tag identity, or final S2 closeout. Releasing without that task would make the irreversible tag boundary depend on session memory.

## Proposed approach

Treat the existing release-please PR as one validation-and-delivery artifact. Bind its exact head and intended kc-dev-flow version, run the existing candidate smoke once through isolated installed Claude and Codex hosts, reconcile complete GitHub-native feedback and required checks, obtain Captain merge authority, then reuse the closed candidate receipt in published mode without another model call. Terminalize only after the tag, version, package tree, installed trees, and Roadmap S2 exit all agree.

## Design determination

Validation-only release closeout. Release-please owns version and tag generation; this task introduces no product design, implementation branch, second release PR, retry loop, provider matrix, or alternate publication mechanism.

## Acceptance criteria

**AC-1 — The release candidate is one closed exact-revision artifact.**
Verified by: PR #221 has one exact head, one intended kc-dev-flow version, manifest/marketplace/plugin parity, an attributable diff, and a candidate receipt whose revision and package tree match that checkout.
Falsified by: head drift, mixed versions, extra release scope, malformed receipt, or receipt identity that differs from the checkout.

**AC-2 — Publication is not the first host-compatibility observation.**
Verified by: one bounded candidate smoke installs and invokes the exact checkout through isolated Claude and Codex state and both closed reports pass.
Falsified by: either host is skipped, uses ambient installed state, returns an invalid report, or requires an unapproved retry.

**AC-3 — Merge remains Captain-owned and externally reviewable.**
Verified by: exact-head required checks and complete GitHub-native feedback are green, every retained item has an evidenced disposition, and Captain explicitly authorizes merge.
Falsified by: silence, provider evidence, stale feedback, pending or failed required checks, or a changed head being treated as authority.

**AC-4 — The published artifact is the validated candidate.**
Verified by: the containing kc-dev-flow tag, declared version, source package tree, Claude installed tree, and Codex installed tree all match the preserved candidate receipt; published mode makes no model call.
Falsified by: any tag/version/tree mismatch, missing publication, or published-mode provider invocation.

**AC-5 — S2 closes only after authenticated release evidence.**
Verified by: the release PR is merged, the published receipt passes, the task terminalizes through Spacedock, and Roadmap S2 has no remaining implementation or release-closeout work.
Falsified by: closing on PR creation, candidate smoke alone, a tag without published smoke, or an active S2 task remaining.

## Test plan

- Re-run repository version parity, relevant contract checks, diff validation, and complete GitHub feedback observation at the exact Release PR head.
- Run exactly one candidate-mode dual-host smoke, bounded to 20 minutes with no automatic retry.
- After Captain-authorized merge and tag publication, run published mode against the preserved receipt without invoking a model.
- Re-read GitHub, tag, installed trees, state branch, and Roadmap before terminalization.

## Measurement

Record exact PR head, target version, candidate and published receipt identities, host verdicts, package-tree hashes, CI duration, feedback fingerprint, merge commit, tag, and elapsed live-smoke time. Provider cost remains unknown unless the provider reports it; zero reported cost is not a zero-cost claim.

## Doc diff

No product doc edit is planned. The already-merged Roadmap declares the S2 release hold and exit; this task supplies the missing release evidence and state closeout.

## Stage Report: validation — 2026-08-14

### Result

- **DONE — candidate receipt record preserved.** Release PR #221 is bound to exact head `aad7f59f29267f7654383e8be377adf79617bf0b`, base `387be484ae353ebe4603720cc7cc3f8c633d25a1`, kc-dev-flow `2.5.0`, receipt SHA-256 `2723e4f60e7ade48c07c9b9d3a1c9f2e5d5aefdff47b1ea6919bbf10100f7513`, and its recorded worktree digest `a4a270194800a263523aacdea18ce27ce79f1da090860d80bca80e71ffe45eaf`. No candidate smoke was rerun.
- **DONE — feedback and Candidate-line disposition.** The Captain-approved body correction now contains exactly one full `Candidate: aad7f59f29267f7654383e8be377adf79617bf0b` line. Final exact-head GitHub feedback remains clean at fingerprint `sha256:349b6dc8e16915980bc38b0a36ad74abb291ce66d7bdbf479a501d422592ecf4`, and the repository-explicit required check passes.
- **DONE — merge delivery.** PR #221 squash-merged the exact candidate as `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`; tag `kc-dev-flow-v2.5.0` points exactly to that merge commit, and the release published at `2026-08-14T15:50:05Z`.
- **FAILED — published smoke and AC-4.** The single published-mode attempt stopped with `published source tree differs from candidate receipt`: the preserved receipt records `a4a27019...45eaf`, while a clean exact-tag clone computes `deefb01a...3c83f`. No automatic retry ran.
- **DONE — Captain-approved bounded recovery.** One separate no-model clean-tag recovery bound the original candidate, published commit, tag, identical Git subtree, preserved failed receipt digest, and clean published digest; isolated Claude and Codex both passed at `2.5.0` / `deefb01a...3c83f` with `model_invocations=0`. It does not supersede or relabel the original FAIL.
- **DONE — next-release blocker and local sync.** Backlog item `release-smoke-tracked-package-identity` (`8hyzngaw0frz3f0rzp2fvpxm`) is committed for kc-dev-flow/S3 and must merge before the next release candidate. After recovery passed, the repo-owned sync installed exact clean tree `deefb01a...3c83f` into both local sources and the active Codex cache; the enabled Claude install reports `2.5.0` and differs from its local source only by `.in_use` runtime markers.
- **READY — AC-5 terminalization.** State inventory has no other active kc-dev-flow/S2 item. The Captain explicitly accepted the recorded AC-4 residual and authorized S2 closeout as `released with recorded verification incident`; S3 work does not block S2.

Failure summary: the original published smoke remains FAILED because ignored worktree contamination made its preserved receipt digest differ from the tracked artifact. The Captain accepted that explicit residual only with bounded clean-tag recovery, a mandatory next-release blocker, verified local sync, and a qualified incident verdict; no receipt was rewritten or superseded.

### Summary

The exact candidate merged and `kc-dev-flow-v2.5.0` published, but the original single published-mode closeout remains failed under the accepted strict receipt contract. The Captain retained v2.5.0 and accepted that recorded residual after one bounded no-model recovery proved the clean tag through isolated Claude and Codex, a next-release blocker was committed, and local sync installed the clean tracked tree. AC-4 remains unmet under the original contract; AC-5 is ready only for the qualified verdict `released with recorded verification incident`.

### Exact artifact and acceptance criteria

- **AC-1 pre-publication record preserved.** The exact diff is five release-please files, `+17/-4`: marketplace, release manifest, Claude manifest, Codex manifest, and changelog. All four version surfaces agree on `2.5.0`. Receipt `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/release-receipts/kc-dev-flow-v2.5.0-aad7f59f.json` remains byte-identical at SHA-256 `2723e4f60e7ade48c07c9b9d3a1c9f2e5d5aefdff47b1ea6919bbf10100f7513`; its `a4a27019...45eaf` digest is now proven to describe the contaminated candidate worktree, not only the tracked exact-revision artifact.
- **AC-2 DONE.** The candidate smoke ran exactly once against isolated installed Claude and Codex hosts; both closed reports passed in 135 seconds against a 240-second timeout, with no retry. Host OAuth was used with Anthropic token variables removed. Provider cost is unknown, not zero.
- **AC-3 DONE.** The corrected body contains the exact Candidate line, the repository-explicit required check and complete feedback observation passed at that head, and PR #221 squash-merged it as `004444c5501fc1ef32c9fe61ea616e8fdc3bc426` through the separate Captain gate.
- **AC-4 UNMET under the original strict receipt contract; Captain-accepted with bounded recovery evidence.** Release `kc-dev-flow-v2.5.0` exists and its tag points to `004444c5...c426`, but the original published-mode attempt rejected clean-tag digest `deefb01a253e8527c770ddb9d52cf3d86c5805ee05283e51ed4f781f4de3c83f` against preserved receipt digest `a4a270194800a263523aacdea18ce27ce79f1da090860d80bca80e71ffe45eaf`. The separate recovery receipt proves the identical tracked subtree and isolated Claude/Codex installs at the clean digest with zero model calls; it does not make the original published smoke pass or supersede its receipt.
- **AC-5 READY for qualified terminalization.** The Captain explicitly accepted the AC-4 evidence residual, the recovery passed, the mandatory S3 blocker is committed, and local sync completed from exact published `origin/main`. No other active kc-dev-flow/S2 item remains, so this closeout may terminalize only as `released with recorded verification incident`, not as an unqualified published-smoke pass.

The already-run exact-head deterministic evidence is green: version parity, skill-frontmatter lint, marketplace L0/L1/L2, kc-dev-flow contract, and `git diff --check`. The read-only sanitize fallback over 17 public files recorded `REJECT=0`, `BLOCK=0`, and four nonblocking ticket-shape-only warnings.

### GitHub-native feedback and delivery metadata

The final pre-merge observation returned PR #221 as `OPEN`, non-Draft, `MERGEABLE`, and still at `aad7f59f29267f7654383e8be377adf79617bf0b`; the base remained `387be484ae353ebe4603720cc7cc3f8c633d25a1`. Complete GraphQL pagination retained zero external threads, complete REST review pagination retained zero external reviews, and `gh pr checks 221 --repo iamcxa/kc-claude-plugins --required` reported version parity pass. The PR subsequently squash-merged that exact head as `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`.

PR feedback: {"scheme":"github-pr-feedback/v1","repository":"iamcxa/kc-claude-plugins","pr":221,"layer":"single","head":"aad7f59f29267f7654383e8be377adf79617bf0b","fingerprint":"sha256:349b6dc8e16915980bc38b0a36ad74abb291ce66d7bdbf479a501d422592ecf4","dispositions":[]}

- **Candidate metadata correction — DONE.** The live body changed from SHA-256 `b16ab9c3acf99fd61538265e31bc08f401218f2d9927efff60e0ac6dbc5e376f` with zero full Candidate lines to SHA-256 `725585f1395470fe00088bec9ca0afe5d72170246511a62bc72bf4d1c49b202a` with exactly one full line: `Candidate: aad7f59f29267f7654383e8be377adf79617bf0b`. It changed no release byte or candidate head. This closes the metadata seam but does not authorize merge.

### Evidence block

Lenses: Pre-merge contract/schema, docs/policy, security/privacy, and delivery evidence remain PASS with 0 open pre-merge findings. Original post-publication runtime/platform and delivery identity remain FAIL with one deterministic Material root cause: the receipt digest included ignored candidate-worktree files absent from the clean tag. The separately authorized recovery and local-sync lenses PASS for exact clean-tag, dual-host, zero-model, and installed-tree identity, but do not erase the strict-contract failure. Inputs include both receipts, exact base/head/merge/tag identities, candidate and clean-tag digests, identical Git subtree object, complete pre-merge feedback, the two-file filesystem difference, blocker identity, and installed destinations.

Diff coverage: 100% — all 5/5 changed files and 21/21 changed lines (`17` added, `4` deleted) map to AC-1 and were directly checked for exact generated scope and version consistency; there is no executable behavior delta in the five release-please files.

Adversarial: FAIL at original published identity — the exact accepted falsifier fired: clean published source digest `deefb01a...3c83f` differs from receipt digest `a4a27019...45eaf`. Direct Git comparison rules out tracked release drift because both candidate and published `kc-dev-flow` paths resolve to subtree object `626bc72aad85540791712d96a04f56cce05b0c2c`; the only filesystem-list difference is the two ignored `.pyc` files recorded below. The bounded recovery then proved the clean tracked tree through both isolated hosts with zero model calls; that additional evidence supports the Captain's residual decision without changing the FAIL.

Cross-model: not_needed — historical pre-publication record only. The single fresh Claude Opus 5 High EM, session `3138cfa8-cc27-4fcb-aa2d-d57ab1bb66e8`, returned route `narrow`, confidence `medium`, and `multi-model: not_needed`. It did not observe or adjudicate this later published-mode failure; no model was rerun.

E2E: FAILED for the original published-mode contract; bounded recovery PASS recorded separately — the exact-once candidate smoke remains PASS, the single original no-model published-mode attempt remains FAIL at source-tree identity, and no automatic retry ran. After explicit Captain approval, one separate clean-tag recovery produced isolated Claude/Codex PASS with zero model calls; only then did local sync complete. This is a qualified incident closeout, not an unqualified E2E PASS.

Origin re-observation: N/A — no accepted claim originated in consumer or external runtime behavior; this is a generated release-artifact closeout, not an originating runtime incident.

### Historical pre-publication engineering judgment

This Opus record predates publication and is preserved as the advice that governed the pre-merge correction. It did not see or adjudicate the published-mode failure below.

- **Question/revision:** Is the exact PR #221 candidate sufficient to approach the Captain merge gate without changing release bytes, and what remains outside validation authority? Revision `aad7f59f29267f7654383e8be377adf79617bf0b` over `387be484ae353ebe4603720cc7cc3f8c633d25a1`.
- **Evidence synthesis:** The five-file diff is version-consistent; deterministic gates pass; receipt `2723e4f6...f7513` binds exact revision/tree and isolated Claude/Codex PASS; the live body now binds that head at SHA-256 `725585f1...b202a`; final GitHub feedback is empty at fingerprint `349b6dc8...2ecf4`; publication and local-sync evidence do not yet exist.
- **Adjudications:** AC-1 and AC-2 are supported. The Candidate-line seam is closed by the exact Captain-approved correction. AC-3 is supported through the final pre-merge re-observation, with only explicit Captain merge authorization unresolved. AC-4 remains unresolved until publication. AC-5 remains unresolved until authenticated release closeout.
- **Risk trade-off:** Pre-publication dual-host proof and the corrected body binding reduce irreversible tag risk without changing release bytes or invalidating CI and the preserved receipt. The remaining irreversible decision is merge itself, so evidence completion must not be treated as Captain authorization.
- **Recommendation/route/confidence:** The EM's exact append-and-reobserve correction is satisfied; return to a separate Captain merge gate without changing files, head, body, or receipt, then run published mode plus local sync before terminalization / `narrow` / `medium`.
- **Dissent:** A stricter reading could have amended the release-please contract, but the applied append-only metadata correction was the smaller reversible fix and the hook now has its required exact-head binding.
- **Disproof condition:** Candidate/head/tree drift; a non-green required check; non-empty or changed feedback; any different body mutation; publication/tag/install mismatch; or any published-mode model invocation changes the route.
- **Authority boundary:** This record is advisory. The Captain-approved PR-body correction and final pre-merge observation are complete; the Captain still owns explicit merge authorization and merge. The receipt must remain unchanged. Published smoke, local sync, task terminalization, and Roadmap S2 closeout remain unclaimed.

### Post-publication incident assessment — original failure, no retry

- **Publication identity:** PR #221 squash-merged exact head `aad7f59f29267f7654383e8be377adf79617bf0b` as `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`. Release `kc-dev-flow-v2.5.0` published at `2026-08-14T15:50:05Z`, and its tag points exactly to that merge commit.
- **Observed failure:** The single published-mode attempt returned `published source tree differs from candidate receipt`. Receipt SHA-256 remains `2723e4f60e7ade48c07c9b9d3a1c9f2e5d5aefdff47b1ea6919bbf10100f7513`; it records tree `a4a270194800a263523aacdea18ce27ce79f1da090860d80bca80e71ffe45eaf`. A clean tag clone computes `deefb01a253e8527c770ddb9d52cf3d86c5805ee05283e51ed4f781f4de3c83f`.
- **Tracked-tree disproof:** Candidate and published `kc-dev-flow` subtrees are identical Git object `626bc72aad85540791712d96a04f56cce05b0c2c`. The failure is not candidate/head/tag/release-byte drift.
- **Root cause:** The candidate worktree contained exactly two extra ignored files before receipt creation: `skills/setup-github-project-projection/assets/__pycache__/install-projection.cpython-314.pyc` and `skills/setup-github-project-projection/assets/__pycache__/project-spacedock-state.cpython-314.pyc`. Both were created at `2026-08-14T23:02:19+0800`; the receipt was created at `2026-08-14T23:05:06+0800`; `.gitignore:23` excludes `__pycache__/`. The candidate digest therefore measured ignored filesystem contamination rather than only the tracked release artifact.
- **Contract impact at incident capture:** AC-4 was not satisfied under the accepted preserved-receipt contract, so AC-5 stopped. The tag, release, receipt, product, and local installs remained untouched; no automatic retry, local sync, terminalization, or Roadmap closeout ran at that point.
- **Recommendation at incident capture:** Keep the failure explicit and ask the Captain to choose a bounded remediation or to leave v2.5.0 closeout failed. Do not silently waive the digest mismatch, rewrite the receipt, retry automatically, or republish the existing tag. The Captain's subsequent decision is recorded below.
- **Authority boundary at incident capture:** Only the Captain could accept the red residual or authorize a new remediation/release path. This assessment granted no product edit, receipt supersession, retry, republish, sync, terminalization, or task-closeout authority.

### Captain-approved bounded recovery and local sync — 2026-08-15

- **Captain decision:** Keep v2.5.0, accept the recorded strict-contract residual, run exactly one bounded no-model clean-tag recovery, file a next-release blocker, sync only after recovery passes, and close S2 as `released with recorded verification incident`. This does not relabel the original published smoke PASS.
- **Recovery receipt:** `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/release-receipts/kc-dev-flow-v2.5.0-recovery.json`, SHA-256 `b5921c0d694a037ec071cb2ccc65e6993db767145dbae149b183b54d2094d838`. It binds candidate `aad7f59f29267f7654383e8be377adf79617bf0b`, published commit `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`, tag `kc-dev-flow-v2.5.0`, version `2.5.0`, Git subtree `626bc72aad85540791712d96a04f56cce05b0c2c`, preserved failed-receipt tree `a4a270194800a263523aacdea18ce27ce79f1da090860d80bca80e71ffe45eaf`, and clean published tree `deefb01a253e8527c770ddb9d52cf3d86c5805ee05283e51ed4f781f4de3c83f`.
- **Recovery result:** Isolated Claude PASS and Codex PASS at version `2.5.0` and clean tree `deefb01a...3c83f`; `model_invocations=0`. The original receipt remains preserved and is not superseded.
- **Next-release blocker:** `release-smoke-tracked-package-identity` (`8hyzngaw0frz3f0rzp2fvpxm`) is committed in the kc-dev-flow/S3 backlog and must merge before the next kc-dev-flow release candidate. S3 work does not block the current S2 closeout.
- **Local source sync:** Repo-owned `post-release-sync.sh` ran from a clean temporary `main` exactly equal to `origin/main` at `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`. `/Users/kent/.claude/plugins/local/kc-dev-flow` and `/Users/kent/.codex/local-plugins/kc-dev-flow` both report version `2.5.0` and exact tree `deefb01a253e8527c770ddb9d52cf3d86c5805ee05283e51ed4f781f4de3c83f`.
- **Active Codex cache:** `codex plugin add kc-dev-flow@kent-local` updated `/Users/kent/.codex/plugins/cache/kent-local/kc-dev-flow/2.5.0`; it reports version `2.5.0` and exact tree `deefb01a253e8527c770ddb9d52cf3d86c5805ee05283e51ed4f781f4de3c83f`.
- **Enabled Claude install:** The enabled marketplace install reports version `2.5.0` and differs from its local source only by `.in_use` runtime markers.
- **S2 inventory and terminal boundary:** No other active kc-dev-flow/S2 item remains besides this closeout. The recovery, blocker, and sync satisfy the Captain-approved incident path; terminalization is ready only with verdict `released with recorded verification incident`.
