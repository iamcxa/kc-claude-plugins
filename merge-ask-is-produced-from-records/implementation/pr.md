feat(kc-dev-flow-2): save delivery observations for merge questions

The delivery check can save public PR and task observations directly as delivery-facts/v1 JSON. The new question route binds that record, allowing FO to write the question and unobservable judgments without copying factual summary fields. Passing observations retain ask-N.json; held observations use observation-N.json so the merge audit does not mistake them for successful asks. Legacy check and question commands, including --summary-file, keep their released behavior.

This is a held local candidate, not ready for publication. The approved four-file change removes a recipe still required by test_sd_dispatch.py's readme-keeps-delivery-rules pins. The pin checker passes on base and fails on this candidate; changing that fifth product file requires FO authorization. No fifth file or ADR was changed.

Local validation: 235 delivery tests passed (one optional integration skip); 64 lint/merge-audit tests and both remote-review adapter suites passed. Repository lint, installed ADR lint, number guards, design surfaces and comment-ratio checks passed. Two archived task/report replays pass check, question and isolated native JSON binding without a manual summary; fresh report-reading Captain-step fixtures replace stale archived paths and do not prove historical acceptance execution. Four named falsifiers were exercised. A live public observation saves a held record, and no green live delivery is claimed.

Workflow words: 6099 to 6069, with a matching budget cut; the dispatch's 6071 is the earlier probe figure. Full lifecycle reading and elapsed-time improvement were not measured. No CI definition changed; CI cost per PR was not measured.

RoboRev not run: FO runs RoboRev after the worker report because the Codex sandbox cannot reach its local daemon. Hosted CI and product publication were not run; FO owns pushing, opening the Draft PR and reading CI after scope is resolved. Candidate: 4675077b582a0875a9ceec0f5e5dcf374da3578e. Base: bfc53d82510006b52baf41569c1e25176e99d87a.
