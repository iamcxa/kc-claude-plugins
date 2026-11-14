# Blind reader findings

Product context read: only the assigned `references/delivery-record.md`. No implementation, tests, other workflow documents, external services, or real task state were inspected or changed.

## Deliverables and limits

- `ask-1.json`: synthetic passing record, `result.exit = 0`.
- `observation-2.json`: synthetic held record, `result.exit = 1`, caused by nonzero `role_calls.exit`. Its later sequence/time intentionally supersedes the earlier synthetic ask.
- `synthetic-source-bytes.json`: exact synthetic strings whose UTF-8 bytes were hashed for question, report, and Captain-step source. These are illustrative strings, not workflow-valid source documents.
- `schema-validation.json`: independent validation against the JSON Schema extracted directly from the assigned document.

These demonstrate field/schema construction only. They do not demonstrate that the delivery checker would produce or accept either record, that a native gate question would pass, or that any repository/public visibility/review/validation/execution was observed. All identities, source contents, commit strings, and outcomes are invented fixtures. No delivery checker was invoked.

## Questions and assumptions encountered

Every question encountered is recorded below. No human clarification was requested; assumptions were limited to fixture construction.

| Question | Classification | Resolution or assumption |
| --- | --- | --- |
| What is the complete field set and which fields can be null? | Contract-defined | Used the embedded schema, including all required top-level fields and no extra record fields. |
| How are successful versus held records named and ordered? | Contract-defined | Used `ask-1.json` then `observation-2.json`; one increasing sequence; later hold supersedes earlier success. |
| What produces a deterministic hold without unknown reviewer behavior? | Contract-defined | Nonzero special-role reader exit holds. Used `role_calls.exit = 1`. |
| What exact problem count results from that special-role exit? | Needs other context | Assumed one problem for the one selected failure; aggregation rules and source diagnostics are not specified. |
| Does schema validity prove that a successful record is possible? | Contract-defined limitation; guard details need other context | No. Schema allows result 0, but does not encode all behavioral checks or cross-field invariants. Synthetic passing means structurally valid with reported pass. |
| What package version and repository/head/time should be used? | Needs runtime context | Used explicit fixture values; document defines meaning and formats, not current observations. Public visibility is assumed only within this fiction. |
| What are the valid mergeability, CI, workflow-run, required-check bucket, and trunk-position vocabularies/casing? | Needs other context | Schema permits arbitrary strings. Chose `MERGEABLE`, `COMPLETED`/`SUCCESS`, `completed`/`success`, `pass`, and `ahead`. Their checker acceptance cannot be established from this document. |
| What candidate dispatch inventory establishes the candidate array? | Needs other context | Assumed one latest dispatch matching the fabricated observed head. Dispatch naming and selection rules beyond the brief description are unspecified. |
| When is a merge-result record owed, and what filename format does it use? | Needs other context | Assumed no owed result and used null. Document explains null and `not run`, but does not define the triggering rule or filename format. |
| What is a valid validation dispatch filename and report format? | Needs other context | Used illustrative `validation-1.md` and a synthetic report string. Only field type and report digest shape are supplied, not a dispatch naming/report-content contract. |
| Which reviewers must be configured and what declaration/profile guards apply? | Needs other context | Assumed only Codex is required and observed clean. Shared guards and current reviewer configuration are referenced but absent. |
| What form must reviewer evidence take, and what exit represents a clean Codex review? | Needs other context | Used illustrative `review:1` and exit 0. Schema accepts these; reviewer-specific success mappings/evidence grammar are not defined. |
| How should external rounds be counted? | Contract-defined | One distinct `(codex, head, review:1)` PR-scope clean observation gives one saved round. No claim about unobserved history. |
| Are there mandatory minimum rounds or a conditional second-reviewer trigger? | Needs other context | Assumed one sufficient configured reviewer and no triggered second reviewer. Structured production/database trigger rules and reviewer minima are not included. |
| What contents and header grammar make a Captain-step source candidate-bound? | Needs other context | Filename and digest format are defined, but source grammar is not. Used illustrative source bytes and assumed `candidate_matches = true`; no execution claim. |
| How are quantity claims and existing-item effect claims identified and matched to evidence? | Needs other context | Assumed zero claims in synthetic question and imaginary PR body. The document refers to text-route readers but does not define their extraction/matching grammar. |
| Which special-role readers must run and how is their aggregate exit calculated? | Needs other context | Assumed aggregate exit 0 in passing fixture and 1 in held fixture. Role inventory and aggregation are unspecified. |
| What exact question content makes a native gate question valid? | Needs other context | The synthetic question is hash input only. It is not claimed to satisfy declaration/profile guards, sufficiency/necessity judgment requirements, or native gate formatting. |
| Are human sufficiency/necessity/disposition judgments fields in the record? | Contract-defined | They belong in the question, not new JSON fields. Clean synthetic review does not require the findings/answered disposition line. |
| How are absent sources represented when a digest field cannot be null? | Needs other context | Not exercised: used available synthetic bytes. `validation.report_sha256` and `question_sha256` require 64 hex characters even though some observations may be unavailable; unavailable-source digest convention is not stated. |
| May fixture caveats and explanations be embedded in these JSON records? | Contract-defined | No additional record fields; explanations stay in this separate file. Human reasons and question/source text are excluded from records. |
| Can these records establish approval, execution, reviewer completeness, or future CI/trunk state? | Contract-defined | No; the document explicitly excludes those conclusions. |

## Usability conclusion

The document alone is sufficient to construct schema-conforming synthetic records and understand their trust limits, naming, key digest meanings, and saved-round counting. It is insufficient to guarantee a semantically passing production record or gate question without the referenced workflow/configuration/adapter conventions. No contract repairs were made.
