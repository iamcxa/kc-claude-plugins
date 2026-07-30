---
title: Make agy the whole-diff review seat before Claude EM landing
status: backlog
source: captain direction 2026-07-30 after reconcile-list-element-shape closeout
started:
completed:
verdict:
worktree:
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design:
lane:
id: 4a255s3z87s7x09vn2fnscep
product: kc-pr-flow
sprint: S6
---

Define a repo-wide dev-flow policy that assigns agy/Gemini the single whole-diff code-review seat regardless of whether Claude or Codex is first officer, followed by Claude EM landing synthesis. Require a real agy attempt before fallback and record the model, tool, and fallback evidence; cap the review-and-repair loop at three rounds by default and five only when explicitly justified; constrain every finding and repair to the PR diff, directly related code, and observed human or AI review comments; preserve inline review and keep Mermaid diagrams opt-in. The Carlove adoption must degrade safely when the review kit is unavailable instead of assuming this repository's plugin surface exists.
