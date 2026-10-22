---
id:
title: kc-adr is the source of the ADR template and the ADR linter
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
---

The Captain ruled on 2026-10-22, in this FO's Paseo session (「同意」, to the item 「縮小你 10/22 的裁決並採用上面的同步方式：kc-adr 只當模板和格式檢查的來源，配號留在 dev2。副本由同步腳本產生，必過檢查做逐位元比對。格式照 dev2 現有的採用，只把「FO」改成「推薦者」。」), and confirmed it in the dev2 FO's session (「ADR 工具要改用 kc-adr 那邊轉述的縮小版。」, recorded as amendment 1 of dev2 task `kc-adr-tools-with-dev2-copy`). The dev2 FO split the work: this task lands kc-adr's side, and the dev2 task generates dev2's copies from it and adds the byte compare. A repo that does not run dev2 (a future finance flow) can then get the ADR template and linter by installing kc-adr.

## Scope

- Add `kc-adr/references/adr-template.md` and `kc-adr/scripts/adr_lint.py` (with the `AdrLintTests` from `kc-dev-flow-2/scripts/test_adr_doc_checks.py`) as the source. Content is byte-identical to dev2's current files, except that the template's "the worker or FO" becomes "the recommender".
- In `kc-adr/skills/read-adr/writing.md`, point `## Where the tools are` at kc-adr's own template and linter, keep the number reserver as a kc-dev-flow-2 file, and add the single-writer numbering sentence: one above the highest number on the base branch; under dev2, use `number_guards.py reserve`.
- dev2's copies, the sync script and the byte compare are out of scope; dev2 task `kc-adr-tools-with-dev2-copy` owns them and starts from this task's merged head.

Non-goals: `number_guards.py` or any reservation logic; monorepo namespaces; `kc-adr/skills/read-adr/SKILL.md` (task `read-adr-reporting-rule-followup` edits it); a lighter format for non-dev2 repos.

Budget: half a working day. Stop if the dev2 template wording change would break dev2's own lint or tests.

## Acceptance criteria

**AC-1**: kc-adr carries `references/adr-template.md` and `scripts/adr_lint.py`. The linter is byte-identical to dev2's at the PR's base, and the template differs only in the "recommender" wording.
Verified by: `cmp` on the linter and `diff` on the template against the base commit's dev2 files.

**AC-2**: kc-adr's `AdrLintTests` pass when run from kc-adr, and dev2's own suite still passes unchanged.
Verified by: running both test files at the candidate.

**AC-3**: `writing.md` points at kc-adr's template and linter, keeps the reserver under kc-dev-flow-2, and states the single-writer numbering rule.
Verified by: a text check of `writing.md`, plus a single-writer dry run that numbers a new ADR one above the base branch's highest number and passes the kc-adr linter.

## FO alignment

Not needed before ideation: the Captain stated the narrowed scope and the split was agreed with the dev2 FO. Release review: not needed: the map was skipped for kc-adr by the Captain's authorization.
Surfaces: none
Visible change: none
