# 0015. The implementation worker opens the Draft PR before validation

Date: 2026-10-14

## Status

Accepted

## Context

In this workflow the implementation worker opens the Draft PR, so external review (Codex, Copilot, RoboRev) runs on the PR head before the delivery gate. Spacedock's `pr-merge` merge hook instead creates the PR at delivery, and its text has no branch for a PR that already exists. `merge guard` arms that hook only while `pr` is empty: in Spacedock 0.27.0 `internal/status/merge.go` the classifier's `pr != ""` case returns `blocked` before the arm case. Probe 2026-10-14, spacedock 0.27.2, scratch copy of the `merge-pr-workflow` fixture holding only `pr-merge.md`: `merge guard 020 --verdict passed` with `pr` empty printed `armed: mod-block set to merge:pr-merge`; the same entity with `pr: "#42"` printed `blocked: PR #42 is pending`. The worker-opened PR left `pr` empty (task `followup-dispatch-records-checked`, PR #642 open at validation with `pr` unset), so nothing scanned it, and in a relay run the FO learned of a merge only when the Captain said so.

## Decision

**Words:** 「1」 — Captain, 2026-10-14, chat, answering FO's two options: 「1. 把早開 PR 變成正式規則（我建議這個）：刪掉 mod 的 merge hook，在 idle 步驟加一條「PR 開了就記下編號」。這保留合併前的審查，也補上合併後自動偵測的漏洞。代價是和套件原本的說明不一致，那句說明要跟著改，這個決定也應該寫成一份 ADR。 2. 改回套件原本的路：實作只做到 commit，PR 交給 merge hook 開。」

The implementation stage opens the Draft PR before validation. FO records it in the task's `pr` field as `<owner/repo>#<N>` at startup and idle (`watch-and-learn` step 1), and the kc-dev-flow-2 mods carry no merge hook. With `pr` set, `merge guard` arms no hook and the `pr-merge` startup and idle hooks wait for the merge, then record the sentinel. The `references/sd/workflow.md` sentence "Use SD's pending terminal approval and existing merge hook; do not invent another PR stage" is replaced by this rule.

**Options considered:**
- open the Draft PR at implementation and record `pr` at idle (chosen)
- implementation stops at the commit and `pr-merge`'s merge hook opens the PR — not chosen by the Captain; it gives up the review before merge that the first option keeps (FO's question), and the hook has no branch for a PR opened earlier

**Recommended:** the first option, as the Captain accepted.

## Consequences

The package's usage differs from `pr-merge`'s own text, which still says its merge hook creates the PR; that hook never runs here while `pr` is set, and it would try to create a second PR if `pr` were empty at the guard. The recording is prose-enforced at FO's startup and idle: a PR merged between two FO passes is still recorded by the next one, because the record step lists PRs in any state, and `pr-merge` then finds it MERGED. `pr_watch.py` state is a machine-local file, so each session re-adds its PRs. Reopen if Spacedock's `pr-merge` gains an existing-PR branch.
