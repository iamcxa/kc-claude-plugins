# Delivery record contract

This file owns `delivery-facts/v1`, its preparation recipe and reader rules.
It lives with the package references so the checker, adopted workflows, observer
and reviewer extensions share a versioned boundary without copying instructions.

## Producer and preparation

FO writes the decision question, sufficiency/necessity judgments, dispositions,
accepted limits and facts the tool cannot observe. FO still exercises the
Captain's requested steps; a stored digest does not prove execution.

`python3 <package>/scripts/delivery_gate.py check <task> --pr <owner/repo>#<N> --text-file <question> --record-facts`

The delivery check is the writer. It saves observations in `<task>/merge/`:
`ask-N.json` for exit 0, `observation-N.json` for a hold, sharing one increasing
sequence. Nonzero holds delivery. Private or unknown repository visibility
returns exit 2 without saving; private adopters retain the legacy text route.
The field allowlist below excludes repository content: no title, body, diff,
review prose, logs, question text or human reasons. No private content belongs
in this record or its public state branch.

`python3 <package>/scripts/delivery_gate.py question <task> --text-file <question> --facts-record <record>`

`question` accepts the newest record only when its check passed and dispatched
candidate, unchanged question bytes, validation report and Captain-step source
still match. FO state-commits it and binds its JSON bytes unchanged as the native
gate artifact summary and `--reference`. FO writes no factual summary. After a
repair push, revalidate and rerun both commands for the new candidate/question;
keep prior records. A later hold supersedes an earlier successful ask.

## Readers and limits

`question` consumes the bindings above; FO reads observations to decide what to
ask. Spacedock fingerprints the committed reference and transports the summary.
The merge audit consumes successful `ask-N.json` PR/head identities; a held
observation must never use that filename. Observations establish neither
execution nor approval, merge authority, reviewer completeness or future CI/trunk
state. Validation's verdict is reported, not certified by the checker.

For validation questions naming `--match-head-commit <sha>`, the observer finds
the `context` Reference ending `/merge/ask-N.json` at the briefing's revision. Compare
its SHA-256 to `rev` after `sha256:`, its head prefix to `<sha>`, its question digest
to the bound question and its JSON bytes to the artifact summary. Report the
delivery-check-before-ask rule `ok` on matches, `violation` on a mismatch; quote
reference id, time and head. Without a reference, report `violation` if the
event-time workflow required one. For older workflows, use the highest-numbered
ask at that head no later than the briefing commit: `ok` with time/head, or
`can't tell` if absent/later, quoting the earliest record and briefing times when
available. Report FO's sufficiency/necessity judgment from the record route's
question, quoting it; absent judgments are `can't tell`, not missing JSON fields.

Count distinct `(reviewer, head, evidence)` PR-scope observations whose outcome
is `clean`, `answered` or `findings`; exclude local jobs, refusals, pending,
security-only/unrecognized responses and missing identities. Repeated reads add
no round. This counts saved observations, not unobserved review history.
`answered` means the adapter saw a review, not that FO found it clean.
FO still reads findings and applies the workflow's disposition rules.
For each `findings` or `answered` observation, the question needs one
`Review decision: <reviewer> <evidence> disposed: <judgment>`; `answered` may
instead use `clean:` after FO reads it. These are human judgments, not new
adapter outcomes or proof of a truthful classification or Captain waiver.
Both commands apply the shared reviewer declaration/profile guards. The text
summary and facts readers feed one `question` guard sequence, which rereads current
reviewer configuration. Merge questions need a valid head token.

List an unread reviewer in the question when the record cannot establish its
status; the Captain decides. An untriggered conditional second reviewer is
exempt: FO may write `Second reviewer: not triggered` except for structured
prod/db triggers. An unread head after a deliberately unrepeated Copilot request
names its last reviewed commit. An unanswered requested review holds the ask.
Copilot exit 2 is a configuration error, never clean. Pending observations hold
the record route; legacy intentional not-read exceptions retain the text route.
Exit 5 is not run, never a
round or clean, and needs no wait. Do not request it again in this task until the
Captain says quota is back; offer that retry in the question. The record route
needs no refusal-quote boilerplate or copied review heading. For exit 5 the question
needs `Copilot not read: <decision>` (or `Copilot not run: <decision>`) and
`Copilot retry: available when the Captain confirms quota is back.`

The check scans the question and PR body with the text route's count/scope
readers. It writes `unchecked_counts` and `scope_disclosure` counts plus the
`（未對過紀錄）` mark into the record, without changing the question or copying
claim prose. A marked count means uncited existing-item effect claims; these
warnings neither hold the ask nor certify the claims.

### Legacy text route

Existing text commands retain their checks. The observer compares the reference
digest/head and its `sufficiency`/`necessity` against the first 200 cleaned clause
characters in question plus summary (`delivery_gate.clean`/`clause`); report
those judgments from the record, or `can't tell` if neither key exists.
Copilot exit 2 is reported as `copilot not run: configuration error: <reason>`.
Legacy Copilot asks name not-read with its refusal quote and a retry. Save exit-5
stdout to `<task>/review/copilot-not-run.txt`, copy
`copilot not run: "<quote>"; answer=review:<id>` and
`Copilot retry: available when the Captain confirms quota is back.`; the text
checker compares the saved output. On exit 0 the legacy gate summary records
the round with its heading quoted; the observer checks FO's clean reading
against it. Legacy summary counts and configured-reviewer checks remain in
the checker's text path.

## Fields

The JSON Schema below defines the saved field allowlist and types. Every listed
top-level field is required; null represents an unavailable observation where
permitted. Nested descriptions name the source or the meaning a reader may use.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object", "additionalProperties": false,
  "required": ["schema", "tool_version", "time", "public", "pr", "head", "candidate", "pr_state", "ci", "workflow_runs", "required_checks", "trunk", "merge_result", "validation", "reviewers", "external_rounds", "round_scope", "captain_steps", "question_sha256", "unchecked_counts", "scope_disclosure", "role_calls", "result"],
  "properties": {
    "schema": {"const": "delivery-facts/v1", "description": "Format version; incompatible shapes require a new version."},
    "tool_version": {"type": "string", "description": "Producing package version, not a source commit."},
    "time": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", "description": "UTC observation time; not authenticated ordering proof."},
    "public": {"const": true, "description": "Repository visibility verified before saving."},
    "pr": {"type": "string", "pattern": "^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[0-9]+$", "description": "Public repository-qualified PR identity."},
    "head": {"type": ["string", "null"], "pattern": "^[0-9a-f]{40}$", "description": "Observed PR head, unavailable on reader failure."},
    "candidate": {"type": "array", "items": {"type": "string", "pattern": "^[0-9a-f]{40}$"}, "description": "Latest dispatched candidates equal to the observed head."},
    "pr_state": {"type": "object", "additionalProperties": false, "required": ["isDraft", "mergeable", "baseRefName"], "properties": {
      "isDraft": {"type": ["boolean", "null"], "description": "Observed draft flag."}, "mergeable": {"type": ["string", "null"], "description": "Observed mergeability."}, "baseRefName": {"type": ["string", "null"], "description": "Observed target branch."}}},
    "ci": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["status", "conclusion", "state"], "properties": {
      "status": {"type": ["string", "null"], "description": "Check-run status."}, "conclusion": {"type": ["string", "null"], "description": "Check-run conclusion."}, "state": {"type": ["string", "null"], "description": "Status-context state."}}}},
    "workflow_runs": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["id", "status", "conclusion"], "properties": {
      "id": {"type": ["integer", "null"], "description": "Actions run identity."}, "status": {"type": ["string", "null"], "description": "Run status."}, "conclusion": {"type": ["string", "null"], "description": "Run conclusion."}}}},
    "required_checks": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["bucket"], "properties": {"bucket": {"type": ["string", "null"], "description": "Required-check result bucket; empty inventory is not proof of required checks."}}}},
    "trunk": {"type": ["object", "null"], "additionalProperties": false, "required": ["head", "trunk", "position"], "properties": {
      "head": {"type": "string", "description": "Compared PR head."}, "trunk": {"type": "string", "description": "Compared trunk commit."}, "position": {"type": "string", "description": "Observed compare relation."}}},
    "merge_result": {"type": ["string", "null"], "description": "Matching merge-result record name, 'not run' requiring its reason in the question, or no owed result."},
    "validation": {"type": "object", "additionalProperties": false, "required": ["verdict", "rounds", "report_sha256", "dispatch"], "properties": {
      "verdict": {"enum": ["PASSED", "REJECTED", "not-observed"], "description": "Latest report's candidate-bound reported verdict."}, "rounds": {"type": "integer", "minimum": 0, "description": "Numbered validation dispatch count."}, "report_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$", "description": "Latest validation report digest."}, "dispatch": {"type": ["string", "null"], "description": "Latest validation dispatch filename."}}},
    "reviewers": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["reviewer", "head", "outcome", "evidence", "scope"], "properties": {
      "reviewer": {"enum": ["codex", "copilot", "roborev"], "description": "Configured reader identity."}, "head": {"type": ["string", "null"], "description": "Head supplied to the reader; pending is not a head verdict."}, "exit": {"type": "integer", "description": "Adapter exit; absent for unobserved local jobs."}, "outcome": {"enum": ["clean", "answered", "findings", "not-run", "error", "pending", "not-observed"], "description": "Adapter interpretation, not FO's finding disposition."}, "evidence": {"type": ["string", "null"], "description": "PR verdict identity; refusals/local jobs have none."}, "scope": {"enum": ["pr", "local"], "description": "Remote verdict or local observation."}}}},
    "external_rounds": {"type": ["integer", "null"], "minimum": 0, "description": "Distinct saved PR verdict identities under the rule above; null on history-read failure."},
    "round_scope": {"type": "string", "description": "Human-readable coverage limit of the count."},
    "captain_steps": {"type": ["object", "null"], "additionalProperties": false, "required": ["path", "sha256", "candidate_matches"], "properties": {
      "path": {"type": "string", "pattern": "^captain-steps/[1-9][0-9]*\\.md$", "description": "Newest step record relative to task folder."}, "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$", "description": "Step-source digest."}, "candidate_matches": {"type": "boolean", "description": "Step header equals observed head; not execution authentication."}}},
    "question_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$", "description": "FO-written question byte digest."},
    "unchecked_counts": {"type": "integer", "minimum": 0, "description": "Question and PR-body quantity claims without matching saved-number evidence; not a hold."},
    "scope_disclosure": {"type": "object", "additionalProperties": false, "required": ["cited", "marked", "mark"], "properties": {
      "cited": {"type": "integer", "minimum": 0, "description": "Existing-item effect claims citing task-local evidence."}, "marked": {"type": "integer", "minimum": 0, "description": "Uncited existing-item effect claims carrying the record's scope mark."}, "mark": {"const": "（未對過紀錄）", "description": "Unverified scope mark; claim prose stays outside the record."}}},
    "role_calls": {"type": "object", "additionalProperties": false, "required": ["exit"], "properties": {"exit": {"type": "integer", "description": "Special-role reader exit; nonzero holds."}}},
    "result": {"type": "object", "additionalProperties": false, "required": ["exit", "problems", "unreadable"], "properties": {
      "exit": {"enum": [0, 1, 2], "description": "0 passed, 1 problems, 2 unreadable without problems."}, "problems": {"type": "integer", "minimum": 0, "description": "Observed problem count."}, "unreadable": {"type": "integer", "minimum": 0, "description": "Unreadable-source count; problems take exit precedence."}}}
  }
}
```
