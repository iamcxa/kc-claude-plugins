---
id:
title: kc-adr is the source of the ADR template and the ADR linter
status: implementation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree: .worktrees/spacedock-ensign-kc-adr-format-source
pr:
gates:
    version: 1
    records:
        - id: gate:kc-adr-format-source:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kc-adr-format-source-backlog-1
              briefing:
                id: briefing:kc-adr-format-source:backlog:attempt-1:revision-1
                digest: sha256:0ff592f3b9d7d312d87b0d8e04248b95e257c8ffb0fde8b9f651a4a9e8088212
                room-ref: ./kc-adr-format-source/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kc-adr-format-source:backlog:1
                briefing: briefing:kc-adr-format-source:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-22T04:37:34.563536Z"
                decision: approve
                reason: Captain replied 「照建議」 (2026-10-22) to a two-item batch whose item 2 was this backlog gate; accepts the outcome, scope, non-goals, half-day budget and AC-1..AC-3 as filed, to run after read-adr-reporting-rule-followup.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:kc-adr-format-source:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:kc-adr-format-source-ideation-1
              briefing:
                id: briefing:kc-adr-format-source:ideation:attempt-1:revision-1
                digest: sha256:2a2be4db2113152eb9fbbf8e6c232f5b0ed9ba414e31d37676d5dc9c34f70430
                room-ref: ./kc-adr-format-source/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kc-adr-format-source:ideation:1
                briefing: briefing:kc-adr-format-source:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T03:39:51.329924Z"
                decision: approve
                reason: Captain replied 「准」 (2026-10-23) to the ideation gate after asking what 'the recommender' means; accepts the design and the D1 and D2 scope additions as stated in the gate question.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-23T02:38:26Z
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

## Design

Profile: pilot. No promotion trigger: no production data, no consumer-required migration, no release duty. Base of every claim below: `8bfac961ddb0167acff2005e256493dfc7942bc5` (origin/main, read 2026-10-23).

### PRFAQ

**Headline.** kc-adr carries the ADR template and the ADR linter, so a repo that installs only kc-adr can write an ADR in dev2's format and check it with the same linter.

**Press release.** Today kc-adr's `writing.md` ends at "Neither: stop. A repo without kc-dev-flow-2 has no writing tools." After this task the template and linter are files of kc-adr, byte-identical to dev2's (the template differs in one phrase), and `writing.md` points at them. A repo without dev2 numbers a new ADR one above the highest on its base branch, one writer at a time. dev2 later generates its copies from kc-adr, so a dev2 user still installs one package; that part is dev2 task `kc-adr-tools-with-dev2-copy`, not this one.

**FAQ.**
- *Why copy and not move?* The Captain's narrowed ruling (see Scope): kc-adr is the source, dev2 keeps generated byte copies, `number_guards.py` stays whole in dev2.
- *What does this task change in dev2?* Nothing. `git diff --stat <base>..<candidate> -- kc-dev-flow-2` is empty (AC-2).
- *Existing-code check (bounded).* Exists: dev2's `references/adr-template.md`, `scripts/adr_lint.py`, `scripts/test_adr_doc_checks.py` (`AdrLintTests` plus `DocImpactTests`). Absent: `git ls-tree -r --name-only <base> -- kc-adr` lists six files (plugin and codex manifests, CHANGELOG, `SKILL.md`, `prefix.md`, `writing.md`); no template, no linter. Conclusion: copy what exists, rewrite nothing, edit one phrase.
- *Why can the tests not be copied byte for byte?* `test_adr_doc_checks.py` also loads `scripts/doc_impact.py` and holds `DocImpactTests`; kc-adr has no `doc_impact.py`, so the file would not import. kc-adr gets `scripts/test_adr_lint.py`: the same header, `record()` helper and `AdrLintTests` body, minus the `doc_impact` load and `DocImpactTests`. It lives at the same relative depth, so `ROOT = parents[1]` still resolves `scripts/` and `references/`.
- *Does the one-phrase wording change break dev2?* Rehearsed, no (see Evidence plan, AC-2). Nothing in the package greps the phrase "worker or FO" outside the template itself (`git grep -n 'worker or FO' <base>` hits only `kc-dev-flow-2/references/adr-template.md`); the only test that reads the template bytes is `test_adr_doc_checks.py`, and its `record()` helper replaces only `# NNNN.`, `Date: YYYY-MM-DD` and `## Status\n\nAccepted`.
- *Past rulings.* ADR 0002 binds the boundary: numbers are reserved by `number_guards.py`, which stays in dev2, and it records that `adr_lint.py` sees duplicate numbers inside one tree only. `git -C <state> grep -n 'Override:'` (2026-10-23) hits only archived design prose about unrelated areas; no past ruling went against a similar recommendation.

```mermaid
flowchart LR
    subgraph kcadr["kc-adr (this task)"]
        T["references/adr-template.md"]
        L["scripts/adr_lint.py"]
        TT["scripts/test_adr_lint.py"]
        W["skills/read-adr/writing.md"]
    end
    subgraph dev2["kc-dev-flow-2 (dev2 task, later)"]
        S["sync script: cp, no transform"]
        C["byte compare: cmp, required check"]
        DT["references/adr-template.md copy"]
        DL["scripts/adr_lint.py copy"]
        NG["scripts/number_guards.py (stays whole)"]
    end
    W -->|"points at, relative to its folder"| T
    W -->|"points at"| L
    W -->|"dev2 repos only"| NG
    T --> S
    L --> S
    S --> DT
    S --> DL
    T -.->|"must equal"| C
    DT -.-> C
    L -.->|"must equal"| C
    DL -.-> C
    TT -->|"runs against"| L
    TT -->|"reads"| T
```

### Exact paths in kc-adr (the stable contract for the dev2 FO)

| kc-adr path | Content | dev2 copy path (dev2 task generates) | Relation |
| --- | --- | --- | --- |
| `kc-adr/references/adr-template.md` | dev2's template with "the option the worker or FO recommended" replaced by "the option the recommender recommended" | `kc-dev-flow-2/references/adr-template.md` | byte-identical after sync; `cp` then `cmp` |
| `kc-adr/scripts/adr_lint.py` | dev2's linter, unchanged | `kc-dev-flow-2/scripts/adr_lint.py` | byte-identical; `cp` then `cmp` |
| `kc-adr/scripts/test_adr_lint.py` | `AdrLintTests` extracted (8 tests) | none: dev2 keeps its own `AdrLintTests` in `test_adr_doc_checks.py` (9 tests, with `DocImpactTests`) | not synced, not byte-compared |

How dev2's copy is generated: a plain byte copy of the two files, in this table's direction, and no text transform (the one wording change is already in the kc-adr source, so sync does not edit). Reference form, rehearsed on 2026-10-23 against scratch copies of the base tree:

```
for f in references/adr-template.md scripts/adr_lint.py; do cp kc-adr/$f kc-dev-flow-2/$f; done      # sync
for f in references/adr-template.md scripts/adr_lint.py; do cmp kc-adr/$f kc-dev-flow-2/$f || r=1; done; exit ${r:-0}   # compare
```
Before sync the compare exits 1 and names `references/adr-template.md` ("differ: char 410, line 21"); after sync it exits 0. Interface requirements for the dev2 task (it owns the design, not this task): the compare's workflow trigger must include `kc-adr/references/adr-template.md` and `kc-adr/scripts/**`, because today `kc-dev-flow-2-tests.yml` triggers on `kc-dev-flow-2/**` only and a kc-adr-only edit would merge with no check; and no workflow runs anything under `kc-adr/` today, so `kc-adr/scripts/test_adr_lint.py` runs in CI only if that required check also runs it as one more step; this is a requirement on that task, not a Captain decision here.

### The exact `writing.md` change (`kc-adr/skills/read-adr/writing.md`)

`## Where the tools are` becomes:

```
## Where the tools are

This plugin ships the ADR template and the ADR linter. `<kc-adr>` is the folder two levels above this file's folder, the one that holds `skills/`; take it from the path you read this file at, not from a search.

- ADR template: `<kc-adr>/references/adr-template.md`
- ADR linter: `python3 <kc-adr>/scripts/adr_lint.py docs/adr --require NNNN`
- Number reserver, only in a repo that runs kc-dev-flow-2: `python3 <package>/scripts/number_guards.py reserve --kind adr --task <task>`

Numbering: where no number was reserved for you, one writer at a time adds an ADR, and its number is one above the highest on the base branch; under kc-dev-flow-2, use `number_guards.py reserve` instead.

Resolve `<package>` (needed only for the reserver) in this order, never as a literal path (`${CLAUDE_PLUGIN_ROOT}` is this plugin's root, not kc-dev-flow-2's):

1. The `Package root:` line in your dispatch notes or in the loaded kc-dev-flow-2 skill header.
2. The installed copy: on Claude Code the `installPath` of `kc-dev-flow-2@kc-claude-plugins` in `~/.claude/plugins/installed_plugins.json`; on Codex the version directory under `~/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/`.
3. Neither: there is no reserver; number as above.

The reserver's path is written against kc-dev-flow-2 <current version>. Read `version` in `<package>/.claude-plugin/plugin.json`; if it differs, still use the file and report "written against <current version>, found X".
```
What the diff removes: "Today the ADR template, linter and number reserver are files of the kc-dev-flow-2 package, and this skill ships no copy of them", the `<package>/references/adr-template.md` and `<package>/scripts/adr_lint.py` lines, and "Neither: stop. A repo without kc-dev-flow-2 has no writing tools." The version stamp stays because the reserver is still a dev2 file; the implementer writes the version actually read from `kc-dev-flow-2/.claude-plugin/plugin.json` at the PR base (the stamp says 0.27.0 and the package installed here is 0.28.0), not a guess.

The relative-path form is chosen because the old text already warns that `${CLAUDE_PLUGIN_ROOT}` is not a path to rely on for another plugin, and a sibling file read by path needs no variable on either host. AC-3 checks the two relative paths exist, not only that the words are present.

Conflict in the numbered list above this section (Decision D1): item 2 says "Invent none; no such section means ask the coordinator" and item 5 says "The coordinator reserves numbers with the number reserver", both true only under dev2. Proposed minimal edit: item 2 becomes "The number is the one the task reserved (`ADR: NNNN` in its `## Number guards` section), or, in a repo whose tasks reserve none, the one `## Where the tools are` gives. Invent none otherwise; ask the coordinator." Item 5 becomes "In a repo that runs kc-dev-flow-2 the coordinator reserves numbers with the number reserver. You do not run it."

### Risk: the template wording change against dev2's own lint and tests

The change is one phrase on the `**Recommended:**` line. Risk: it is the only line the linter's `--require` rule reads (`"**Recommended:**" not in Decision`), so a slip in the edit that damages the label breaks every required record. Catch: AC-2's overlay run puts kc-adr's template and linter on dev2's paths and runs dev2's suite. That is needed because this PR does not touch dev2's files, so dev2's suite run "unchanged" at the candidate is green by construction and proves nothing about the new wording. Rehearsed 2026-10-23: overlay, 9 of 9 pass; mutation damaging the label (`**Recommended:**` to `Recommended:`) fails 3 of 8 kc-adr tests; mutation renaming `## Status` fails 5 of 8. What no test can catch: the wording itself (no test reads that phrase). Stop condition from Scope ("stop if dev2's lint or tests would break") did not fire in the rehearsal.

## Evidence plan

Notation: `WT` is the candidate worktree, `B` the PR's base commit, `C` the candidate head. Commands were rehearsed on 2026-10-23 against scratch copies of `8bfac961` in `/tmp` (nothing written to the repository); the results below are rehearsal results, not candidate results.

**AC-1** (filed text unchanged). Clauses:
1. `git -C "$WT" show "$B:kc-dev-flow-2/scripts/adr_lint.py" | cmp - "$WT/kc-adr/scripts/adr_lint.py"` exits 0. Rehearsal: identical.
2. `git -C "$WT" show "$B:kc-dev-flow-2/references/adr-template.md" | diff - "$WT/kc-adr/references/adr-template.md"` prints exactly one hunk, line 21, `worker or FO` to `recommender`. Rehearsal: one hunk, `21c21`, one line changed.
3. `git -C "$WT" diff --stat "$B..$C" -- kc-dev-flow-2` is empty (this task edits no dev2 file).
Fails if: the linter differs by one byte, the template differs outside line 21, or any dev2 file is touched.

**AC-2** (filed text unchanged). Clauses:
1. `python3 -B "$WT/kc-adr/scripts/test_adr_lint.py"` prints `Ran 8 tests` and `OK`, run from kc-adr's folder (and again from another cwd). Rehearsal: 8 tests OK.
2. dev2's suite unchanged: `python3 -B "$WT/kc-dev-flow-2/scripts/test_adr_doc_checks.py"` and the three suites that name the linter (`lint-skills.py`, `test_lint_skills.py`, `test_dispatch_records.py`) pass at `C`.
3. Overlay run (the one that exercises the new wording): `git -C "$WT" archive "$C" kc-dev-flow-2 kc-adr scripts docs/adr .claude-plugin | tar -x -C "$SCRATCH"`, copy `kc-adr/references/adr-template.md` and `kc-adr/scripts/adr_lint.py` onto the `kc-dev-flow-2` paths, then run the same four commands there. Rehearsal: `test_adr_doc_checks.py` 9 of 9 OK, `lint-skills.py` exit 0, `test_lint_skills.py` 35 of 35, `test_dispatch_records.py` 47 of 47, and the repo's 28 ADRs pass the linter. Not run in the rehearsal: `test_sd_dispatch.py` (needs a pinned Spacedock plugin root; it names `adr_lint.py` in prose checks only) and the extension suites; the implementer runs `test_sd_dispatch.py` if the Spacedock root is available, else states it as a limit.
4. Falsifiers, run once and reported: damaging the `**Recommended:**` label in the kc-adr template makes clause 1 fail (rehearsal: 3 of 8 fail); renaming `## Status` makes it fail (5 of 8).
Fails if: any suite is red, or clause 1 passes with a damaged template.

**AC-3** (filed text unchanged). Clauses:
1. Text check of `$WT/kc-adr/skills/read-adr/writing.md`: under `## Where the tools are`, `<kc-adr>/references/adr-template.md` and `<kc-adr>/scripts/adr_lint.py` appear; `<package>/references/adr-template.md` and `<package>/scripts/adr_lint.py` do not; `<package>/scripts/number_guards.py reserve` does; the sentence containing "one above the highest" also contains `number_guards.py reserve`.
2. Path check: from `$WT/kc-adr/skills/read-adr`, `test -f ../../references/adr-template.md && test -f ../../scripts/adr_lint.py` exits 0.
3. Single-writer dry run, in a scratch git repo: base branch `main` holds `docs/adr/0001..0003` made from the template; on a feature branch, compute `HIGH=$(git ls-tree --name-only main docs/adr/ | sed 's|.*/||' | grep -E '^[0-9]{4}-' | cut -c1-4 | sort | tail -1)` and `N=$(printf '%04d' $((10#$HIGH+1)))`; write `docs/adr/$N-a-new-ruling.md` from the template; then `python3 ../../scripts/adr_lint.py docs/adr --require $N` and `--since <main sha>` both exit 0. Rehearsal: highest 0003, new 0004, both exit 0; a fourth file numbered 0003 exits 1 ("number 3 is also used by").
Limit stated with the criterion: the linter checks one working tree, so two writers on two branches can both take `$N` and each passes; it is caught at the merge, which is why the sentence says one writer at a time (ADR 0002 records the same limit). The dry run proves the numbering rule and the linter path, not concurrency safety.
Fails if: a required string is missing, a relative path does not resolve, or the linter exits non-zero on the dry-run ADR.

## Needs decision (Captain)

Two decisions, D1 and D2; they are independent.

- **D1. Do the numbered steps above `## Where the tools are` change too?** Recommend yes, the minimal edit to items 2 and 5 shown above. Without it `writing.md` tells a non-dev2 agent both "invent none, ask the coordinator" and "number it one above the highest". It adds two edited lines beyond the filed scope. Residual either way: `SKILL.md` ends "no reserved number means do not write one: ask the coordinator"; that file is task `read-adr-reporting-rule-followup`'s, so this task leaves it and reports it.
- **D2. Do the two claims this change makes false ship in the same PR?** Recommend yes: the `README.md` kc-adr paragraph ("One skill, `read-adr`, and no tool ... ships no copy"; also stamped 0.1.0 while the plugin is 0.1.1) and `docs/journey/kc-decision-log/boundary-contract.md` (the tools paragraph says kc-adr becomes the source of numbering "配號中 ADR 部分的來源" and "在那張任務完成前，read-adr 的寫入部分照舊指向 dev2 的工具", both overtaken by the narrowed ruling). The repo's README sync rule and the retained-document practice call for it; neither file is in the filed scope. Without it both documents state the opposite of the merged behaviour.

Not decisions, recorded as residual: the unverified assumption that `read-adr-reporting-rule-followup` (a task in another workflow, whose file is not in this state checkout) edits only `SKILL.md` and not `writing.md`, so a merge collision is possible and FO can check it; the kc-adr linter's docstring still says "dev2 ADR format" (byte-identical by the ruling); the substituted phrase reads "the option the recommender recommended" (the ruling's exact words); kc-adr's CHANGELOG and version move through release-please from a `feat(kc-adr):` commit, never by hand.

## Stage Report: ideation

- DONE: Design kc-adr's side of the narrowed packaging ruling: the exact paths in kc-adr for the ADR template, `scripts/adr_lint.py` and `AdrLintTests`. They are byte-identical to dev2's files at base 8bfac961ddb0167acff2005e256493dfc7942bc5, except the template's "the worker or FO" becomes "the recommender". Show exactly how dev2's copy will be generated from them later, so the dev2 FO's sync script and byte compare can rely on stable paths.
  `## Design`, "Exact paths" table: `kc-adr/references/adr-template.md`, `kc-adr/scripts/adr_lint.py`, `kc-adr/scripts/test_adr_lint.py` (AdrLintTests only: the dev2 file also loads `doc_impact.py`, so it cannot be byte-identical); sync is `cp`, compare is `cmp`, both rehearsed on scratch copies (before sync exit 1, after exit 0).
- DONE: Show the exact `writing.md` change: `## Where the tools are` points at kc-adr's own template and linter, keeps the number reserver under kc-dev-flow-2, and adds the single-writer numbering sentence. Note the risk that the template wording change affects dev2's own lint or tests, and how the AC-2 run will catch it.
  `## Design`, "The exact writing.md change" and "Risk": full replacement text, plus items 2 and 5 conflict (D1). Overlay rehearsal: dev2 `test_adr_doc_checks.py` 9/9, `lint-skills.py` exit 0, `test_lint_skills.py` 35/35, `test_dispatch_records.py` 47/47; the AC-2 overlay run is needed because this PR leaves dev2's files untouched.
- DONE: Give AC-1..AC-3 reproducible evidence clauses and list decisions for the Captain.
  `## Evidence plan` (per AC, below) and `## Needs decision`: D1 (numbered steps 2 and 5), D2 (README and boundary-contract claims made false).
- DONE: AC-1 evidence (not yet verified at a candidate).
  Clauses: `cmp` on the linter, one-hunk `diff` on the template, empty `git diff --stat <base>..<C> -- kc-dev-flow-2`. Rehearsed on scratch copies of 8bfac961: linter identical, template differs only at `21c21`.
- DONE: AC-2 evidence (not yet verified at a candidate).
  Clauses: kc-adr test file run (rehearsal 8/8), dev2 suites unchanged, overlay run of dev2 suites with kc-adr's files, two falsifiers. Rehearsed: label-damaged template fails 3 of 8, `## Status` renamed fails 5 of 8. Not rehearsed: `test_sd_dispatch.py` (needs a Spacedock plugin root).
- DONE: AC-3 evidence (not yet verified at a candidate).
  Clauses: text check, relative-path `test -f` check, single-writer dry run. Rehearsed: highest 0003, new 0004, linter exit 0 with `--require` and `--since`; a duplicate 0003 exits 1. Limit: the linter sees one tree, so two concurrent writers are not caught (ADR 0002).
- DONE: Run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/design_surfaces.py check <task>`.
  `python3 .../0.28.0/scripts/design_surfaces.py check kc-adr-format-source.md` printed "kc-adr-format-source.md: design surfaces presentable", exit 0. The skill header resolved to 0.26.0; `diff -rq` of the two roots differs only in plugin.json and `.in_use`, so the checker is the same bytes.
- DONE: Write no repository file, branch or commit.
  `git status --short` in the worktree shows only the pre-existing ` M .gitignore` (not mine); my only writes are this state file and scratch copies under `/tmp/kc-adr-ideation-rehearsal`.

### Summary

kc-adr gets the template and linter as byte copies of dev2's (one phrase changed) plus an extracted `AdrLintTests` file, and `writing.md` points at them; dev2's sync is a `cp` and its compare a `cmp` over the two stable paths. The wording change did not break dev2's lint or tests in a scratch overlay run, but that run is the only thing that can show it, so AC-2 must include it. Two Captain decisions: D1 (steps 2 and 5 in `writing.md` contradict the new numbering sentence) and D2 (README and boundary-contract claims become false); the CI step for kc-adr's tests is a requirement on the dev2 task. Unverified: that `read-adr-reporting-rule-followup` does not also edit `writing.md`.

## Stage Report: implementation

- DONE: Build the approved design: kc-adr/references/adr-template.md ("the worker or FO" -> "the recommender"), kc-adr/scripts/adr_lint.py (byte-identical), kc-adr/scripts/test_adr_lint.py (AdrLintTests only); apply the approved writing.md replacement text; D1 and D2; no dev2 file changes.
  Commit 57b86de4 on spacedock-ensign/kc-adr-format-source, base c3514876339cb732d0bea8b2d2dd45c234bcdeaf (rebased ff from 8bfac961; the dev2 linter, template, test file, kc-adr, README and boundary-contract had no diff between the two). Six files: three new kc-adr files, `writing.md` (replacement section plus items 2 and 5 per D1, version stamp 0.28.0 read from `kc-dev-flow-2/.claude-plugin/plugin.json` at base), README kc-adr paragraph (0.1.0 -> 0.1.1, tools stated), boundary-contract tools paragraph.
- DONE: AC-1 evidence.
  `git show $B:kc-dev-flow-2/scripts/adr_lint.py | cmp - kc-adr/scripts/adr_lint.py` exit 0; template diff is the single hunk `21c21`; `git diff --stat $B..$C -- kc-dev-flow-2` is empty. Fails if the linter differs by one byte or any dev2 file is touched.
- DONE: AC-2 evidence.
  kc-adr `test_adr_lint.py`: Ran 8 OK, from kc-adr and from /tmp. dev2 at candidate: `test_adr_doc_checks.py` 9 OK, `test_lint_skills.py` 35 OK, `test_dispatch_records.py` 47 OK, `lint-skills.py` exit 0. Overlay (scratch `git archive` of C, kc-adr template and linter copied onto dev2 paths): same four green, repo's 29 ADRs pass the linter. Not run: `test_sd_dispatch.py` (requires `--sd-plugin-root`, no pinned Spacedock root provided; this change touches no dev2 file); extension suites.
- DONE: Two template falsifiers.
  Label `**Recommended:**` -> `Recommended:` in a scratch copy: `test_adr_lint.py` FAILED (failures=3) (asserts the required-record rule and the template-is-valid test); `## Status` -> `## State`: FAILED (failures=5). Neither would pass with a damaged template.
- DONE: AC-3 evidence.
  Text check on `## Where the tools are`: both `<kc-adr>/` paths present, both `<package>/` template/linter paths absent, `<package>/scripts/number_guards.py reserve` present, the "one above the highest" sentence also names `number_guards.py reserve`. From `kc-adr/skills/read-adr`, `test -f ../../references/adr-template.md && test -f ../../scripts/adr_lint.py` exit 0. Dry run in a scratch git repo: highest 0003 -> new 0004 written from the template; `adr_lint.py docs/adr --require 0004` and `--since <main sha>` both exit 0; a second file numbered 0003 exits 1 ("number 3 is also used by"). Limit as designed: one tree only, concurrent writers are not caught (ADR 0002).
- DONE: Closing checks.
  `version-parity-check.sh` exit 0 (kc-adr 0.1.1 all sources); `skill-frontmatter-lint.sh` exit 0; `comment_ratio.py` "code lines 216, comment lines 1, 0.5%, maximum 5% met" (the one comment is in the byte-identical linter); `design_surfaces.py check` exit 0 "presentable"; `doc_impact.py` lists 0 documents; sanitize-check on kc-adr (rules from `sanitize-rules.yaml`, 8 block literals, REJECT and WARN patterns): 0 BLOCK, 0 REJECT, 0 WARN. No ADR added or changed, no `## Number guards` section.
- DONE: Roborev step.
  `roborev_gate.py --repo <worktree> --base c3514876...` exit 0: `clean on 57b86de48; evidence=roborev:1066`.

### Summary

kc-adr now ships the ADR template and linter as byte copies of dev2's (one phrase changed) plus `test_adr_lint.py`, `writing.md` points at them with the single-writer numbering rule, and the README and boundary contract no longer say kc-adr ships no tools. No dev2 file, version or CI workflow was touched. Residuals for FO: `kc-adr/skills/read-adr/SKILL.md` still ends "no reserved number means do not write one: ask the coordinator" (owned by `read-adr-reporting-rule-followup`; it may also edit `writing.md`, so a merge collision is possible, unchecked); `test_sd_dispatch.py` not run; the CI step that runs `kc-adr/scripts/test_adr_lint.py` and the compare's trigger paths are owed by dev2 task `kc-adr-tools-with-dev2-copy`; push, PR and release are FO's.
