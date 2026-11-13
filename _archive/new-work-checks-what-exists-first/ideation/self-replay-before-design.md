# Same-worker replay: findings before the proposed integration

This is the current assigned worker reading a generated dispatch, not a fresh model, independent validation, a baseline model comparison or proof of host-wide compliance. The first replay checklist explicitly asked for the check and is excluded as behavioral evidence. The neutral replay uses the real public directory-crash task with a neutral ideation checklist; it changes none of that task's state or code.

Checked, in order:
- Spacedock: its own ensign shared core, workflows/entities and stage-lifecycle docs. These own stage/state/dispatch and provide user-defined stage standards, not this package's upstream-first rule. No new Spacedock contract is needed.
- Package at base 8125e6d516d32abbf79c6772de10cde2c20900a8: design_surfaces.py check_task/main and its callers/tests. Existing CLI constructs Path(task) directly; check_task catches its first directory read but scope_hold reads it again. The directory entry produces IsADirectoryError; an explicit .md reaches ordinary missing-design diagnostics instead. Use the existing checker; do not add another parser or an upstream runtime hook.
- Relevant siblings: three adopter workflow READMEs and committed state branches, only presence counts saved in adopter-counts.json. None of the three workflow READMEs contains an explicit upstream-first clause. Task mentions are not a reusable tool contract or compliance evidence.
- Governing records: repository ADRs 0041 (seed bounds), 0057 (amendment comparison), 0077 (budget/worth questions), all Accepted at the base. The small path-entry proposal would preserve them. For this check-rule task, ADR 0037 keeps the broader upstream check separate and ADR 0020 prevents an unapproved workflow-word increase.
- External contract: read Spacedock's own docs/source, not an adopter's workaround. No extra third-party library is needed. No applicable RFC/public standard was identified by the bounded primary-source search recorded in research.json; this is a package working practice, not a protocol.

Unknowns: the public census is only lexical presence; it proves no private task was completed correctly. No private task text, ruling or log was copied. No new application/server/browser/database tests were run.
