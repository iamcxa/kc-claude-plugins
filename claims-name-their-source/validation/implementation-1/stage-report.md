## Stage Report: implementation

- DONE: Implement the approved written rule printed by the two gate commands with no hold, in only the design's named files.
  Local candidate `792c3c6847966824ab002d91ad41f7f164ee373c`, branch `spacedock-ensign/claims-name-their-source`, base `4f08f008f9b117876ffe4b569210278e240d203d`; six approved files, no version bump (`git diff --name-only <base> HEAD`, 2026-11-03). Evidence: `claims-name-their-source/validation/implementation-1/`.
- DONE: ADR 0055 records the ruling the design names, quoting the Captain's words from the task file and its gate records.
  ADR 0055 quotes 「可以」 and the exact ideation gate question; follows ADR 0027 D4, records the ideation report's replay as not run by implementation, and the Captain-approved +55 startup words after ADR 0054.
- DONE: AC-1, AC-2 and AC-4 structural behavior, with their falsifiers run as isolated mutations (python3 -B, copied source without caches).
  `prove.py`, `mutation-results.json`: removing the ledger step fails with “raise step of 55”; removing only check's emit fails its reminder assertion while question's control passes; rewording the chat phrase fails lint. Tests cover question/check exits 0, 1 and 2 and ASK remaining last. Baseline reminder regressions failed (`reminder-red.log`).
- DONE: AC-5 independent per-moment recount at the candidate.
  `prove.py`, `word-counts.json` and actual base/candidate fixture outputs (2026-11-03): workflow 5836→5891 (+55), mod 48 unchanged; question 3→30 and check 57→84 (+27 each), both exits unchanged. Idle/archive (`pr_watch.py`) and ideation (`design_surfaces.py`) sources match the base. This recount imports the base command from git show rather than subtracting the new line.
- SKIPPED: AC-3's 24-run behavioral replay and a claim that every acceptance criterion is green.
  FO stopped the route after four no-answer attempts, below the hard stop of 30; `attempts.json`, `protocol*.json`, `runs/*/meta.json` retain each provider/model/token record. Three Claude attempts reported input/output 0; Codex returned no usage record, not zero tokens. No behavior result or README-raise benefit is claimed.
  The original old-model Claude --bare attempt was followed by the FO-corrected claude-opus-5-5 safe-mode routes. Fresh HOME and then FO-authorized normal HOME + --safe-mode in scratch cwd both returned “Not logged in · Please run /login”, exit 1. `claude-help.txt`, argv and normal-run initialization retain the supported isolation evidence; built-in plugins remain visible, no file-open trace claimed. No credential file was copied; the first Codex auth link was removed.
  The gpt-6.1-sol attempt exited 1 with connection failures. No further Codex half ran: exec --help lists no supported switch to skip global AGENTS.md with normal CODEX_HOME. `grader-falsifiers.json`: original messages FAIL, stored corrections PASS; the PR #706 correction is read through the task Reviewer line, not from the hosted PR. Replay scripts/inputs are retained in this validation folder; the base-saturation/README-removal decision is unresolved.
- DONE: AC-6 existing callers and the required repository/ADR/number/comment/design checks.
  `python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'` exits 0: 891 tests, 6 skips (`full-suite-final.log`). `lint-final.log` is 5891/5891; `adr-lint-final.log` (--since base --require 0055), `number-guards-final.log` (base/head bound), `comment-ratio.log` (within maximum) and `design-check.log` exit 0. Commands and candidate hashes are retained in `manifest.json`; all ran 2026-11-03.
- SKIPPED: Push, one stacked Draft PR on PR #773, exact-head RoboRev and CI green on the PR head.
  FO explicitly retained these duties under ADR 0042/0048 on 2026-11-03. Worker did not push the product branch, open/comment/request a review, mark ready or merge. RoboRev is not run, with no evidence= or incomplete-line claim. CI cost per PR was not measured; no CI trigger changed. Exact title/body are `pr-title.txt` and `pr-body.md`.
- DONE: Record each affected document's disposition (`doc_impact.py <base> HEAD`, 2026-11-03).
  `docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md` — unaffected: budget equality, Captain quote and loading ledger are retained.
  `docs/adr/0037-workers-check-shared-work-and-return-to-fo-early.md` — unaffected: Team dispatch rule and its protected +144 entry are unchanged.
  `docs/adr/0044-delivery-gate-summaries-carry-review-facts-with-legacy-call-compatibility.md` — unaffected: summary and legacy reviewer checks are unchanged.
  `docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md` — unaffected: model/effort lint and model table are unchanged.
  `docs/adr/0051-the-merge-ask-check-requires-the-round-count.md` — unaffected: round-count hold is unchanged; the new line is advisory.
  `kc-dev-flow-2/README.md` — unaffected: entry, adoption and maintenance commands remain correct.
  `kc-dev-flow-2/skills/maintain-flow/SKILL.md` — unaffected: word-budget and test maintenance procedure is retained.
  `learning.md` — unaffected: retained evidence is unchanged; independent lifecycle recount and consumer search were followed.
- DONE: Commit product locally and preserve the report/evidence in the assigned split-root state checkout.
  Product commit is the candidate above; state writes are task-scoped. State commit/sync receipts are reported separately after this write.

### Summary

The written rule, advisory output, observer list, +55 ledger and ADR 0055 are implemented at the local candidate above. AC-3 is unverified after the authorized routes failed; FO owns the replay decision, publication, exact-head RoboRev and hosted CI, so this is a handback, not an all-green implementation claim.
