---
title: workflow_checkout.py prints a remedy that works for every mismatch it detects and quotes every argument
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from the third external review round (Codex) of iamcxa/kc-claude-plugins PR #631 (head 20c9ec53, review:5500808862), 2026-10-13, task `workflow-checkout-must-match-trunk-readme`. Neither finding is P1 or Material, so neither started a repair cycle there; each is filed here with its decline reason, per `## FO steps: review findings` step 5.

## Scope

- Finding 1 (Codex P2, `scripts/workflow_checkout.py` remedy, around line 50): the `origin/<trunk>` argument is not shell-quoted, so a trunk ref with shell metacharacters (Git accepts `release;next`) prints a remedy that runs a second command when pasted. Decline reason: the trunk comes from the adopter's own README frontmatter (`main` or `next` in every adopter read on 2026-10-13); no observed ref with metacharacters, and the Captain reads the remedy before running it (ADR 0014, D3).
- Finding 2 (Codex P2, same remedy): when the README differs because of an uncommitted edit in a detached checkout already at `origin/<trunk>`, `checkout --detach origin/<trunk>` keeps the edit, so the rerun still exits 1 and the remedy does not resolve that case. Decline reason: the check still holds (fail-safe, never a false pass); the edited-README case is the Captain's to resolve under D3, and no FO has been observed holding on it.
- Related, found by the validators of tasks `workflow-checkout-must-match-trunk-readme` and `observer-before-merge-guard`: package text outside those PRs names a mode-100644 script bare, so it cannot run as written: `references/sd/adoption.md` (the `poc_readme.py derive` table cell). Candidate fix: a package-wide check that every `<package>/scripts/*.py` instruction runs through `python3` unless the file is executable.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the findings and decline reasons above are the scope.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
