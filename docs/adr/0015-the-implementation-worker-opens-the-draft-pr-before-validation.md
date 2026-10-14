# 0015. The implementation worker opens the Draft PR before validation

Date: 2026-10-14

## Status

Accepted

## Context

In this workflow the implementation worker opens the Draft PR, so external review (Codex, Copilot, RoboRev) runs on the PR head before the delivery gate. Spacedock's `pr-merge` merge hook instead creates the PR at delivery, and its text has no branch for a PR that already exists. `merge guard` arms that hook only while `pr` is empty: in Spacedock 0.27.0 `internal/status/merge.go` the classifier's `pr != ""` case returns `blocked` before the arm case. Probe 2026-10-14, spacedock 0.27.2, scratch copy of the `merge-pr-workflow` fixture holding only `pr-merge.md`: `merge guard 020 --verdict passed` with `pr` empty printed `armed: mod-block set to merge:pr-merge`; the same entity with `pr: "#42"` printed `blocked: PR #42 is pending`. The worker-opened PR left `pr` empty (task `followup-dispatch-records-checked`, PR #642 open at validation with `pr` unset), so nothing scanned it, and in a relay run the FO learned of a merge only when the Captain said so.

## Decision

**Words:** 「1」 — Captain, 2026-10-14, chat, answering FO's two options: 「1. 把早開 PR 變成正式規則（我建議這個）：刪掉 mod 的 merge hook，在 idle 步驟加一條「PR 開了就記下編號」。這保留合併前的審查，也補上合併後自動偵測的漏洞。代價是和套件原本的說明不一致，那句說明要跟著改，這個決定也應該寫成一份 ADR。 2. 改回套件原本的路：實作只做到 commit，PR 交給 merge hook 開。」

**Words:** 「准」 — Captain, 2026-10-14, at the redone ideation gate, accepting FO's recommendation on who may open the Draft PR. The gate question stated: "this approval is that grant for this task: the implementation worker may push the task branch and open a Draft PR in iamcxa/kc-claude-plugins".

The implementation worker opens the task branch's Draft PR before validation where its dispatch scope notes quote the Captain's push grant, and names it in its report; without a quoted grant it opens nothing and reports `no PR opened: no push grant`. The grant covers a Draft only: ready and merge still need the Captain's word. FO records the PR in the task's `pr` field as `<owner/repo>#<N>` from the `next:` lines of `python3 <package>/scripts/pr_watch.py tasks` at startup and idle, and the kc-dev-flow-2 mod carries no merge hook. With `pr` set, `merge guard` arms no hook and the `pr-merge` startup and idle hooks wait for the merge, then record the sentinel. The `references/sd/workflow.md` sentence "Use SD's pending terminal approval and existing merge hook; do not invent another PR stage" is replaced by this rule.

**Options considered:**
- the worker opens the Draft PR under a quoted push grant and `pr` is recorded from `tasks` output (chosen)
- FO presents the candidate and PR body after implementation and opens the PR on the Captain's go — not chosen: one more message and approval from him per task
- implementation stops at the commit and `pr-merge`'s merge hook opens the PR — not chosen by the Captain; it gives up the review before merge that the first option keeps, and the hook has no branch for a PR opened earlier

**Recommended:** the first option, as the Captain accepted.

## Consequences

The package's usage differs from `pr-merge`'s own text, which still says its merge hook creates the PR; that hook never runs here while `pr` is set, and it would try to create a second PR if `pr` were empty at the guard. The recording is enforced by output, not prose: `tasks` lists the branch's PRs in any state except CLOSED, so a PR merged between two FO passes is still recorded by the next one and `pr-merge` then finds it MERGED. A gate question that forgets the grant leaves the worker opening nothing, and the PR then opens at delivery. `pr_watch.py` state is a machine-local file, so each session re-adds its PRs. Reopen if Spacedock's `pr-merge` gains an existing-PR branch.
