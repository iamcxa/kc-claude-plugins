# Exact-head validation findings

Verdict: REJECTED for implementation repair. Product candidate remains
`55b7cd28fbf73095bd3f6982e1ab3db00a0c9071`, base
`3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`, branch
`feature/kc-pr-review-capability-protocol-pilot`. No product file was edited.
The six repair groups below are deduplicated, not six extra capabilities or
permission to change the accepted route. The original implementation worker
owns a read-only repair plan first; the First Officer routes it.

## Confirmed repair obligations and falsifiers

1. **Preserve sampled routing and reject a contaminated control arm (AC-7, AC-10).**
   The new skill invocation at lines 114–118 overwrites both flags with `on`;
   the runner at core lines 1204–1209 inspects protocol output only for treatment.
   Thus the child cannot enforce the sampled off values, and a control that
   accidentally executes that snippet has no protocol-artifact refusal.
   Keep the default-off gate mechanical at the existing invocation/runner seams.
   Falsifier: invoke that exact adapter command under sampled control-off flags
   with a model stub; it must remain legacy and make no capability call. A
   control leaving profiled artifacts must be refused, not scored as control.

2. **Close malformed inputs and classify unsupported evidence (AC-2, AC-4, AC-10).**
   Fresh CLI reproductions: a 257-character repository value, dispatched JSON
   missing `prepared`, and fallback `[null]` each exit 1 with empty stdout and
   an uncaught Invalid/KeyError/AttributeError. `main`, `collate`, and exception
   echo construction must preserve a validated terminal on these paths, without
   weakening schemas or emitting an unchecked echo. A committed Latin-1 text
   patch currently exits 2 as `schema_failure`; unsupported encoding/oversized
   material belongs in the existing evidence-missing partition rather than
   being mistaken for invalid caller schema. The >1 MiB boundary is source-bound
   at EvidenceMaterial.maxLength, not independently executed here.
   Low-severity closure checks: `Token` accepts `abc` followed by newline;
   an out-of-plan result emits `required_gap` despite the spec's one-trigger
   restriction; malformed normalized finding input raises KeyError instead of a
   named experiment refusal. Preserve exact allowed terminal/status semantics.
   Falsifier: each malformed artifact yields its bounded, schema-valid refusal;
   unsupported material remains explicit, never clean; no traceback-only exit.

3. **Retain failed-run evidence and whole experiment cost accounting (AC-8–AC-10).**
   Core `pilot_telemetry` requires model/cost metadata for every attempt, then
   exits on a null failed/retried provider envelope; `cmd_pilot_run` can exit
   before writing a v4 receipt. Retaining unavailable usage as incomplete is
   correct; losing the attempted-run receipt is not. Record a closed failed
   attempt/pair without making it eligible for timing or quality promotion.
   Do NOT implement Claude's suggestion to ignore failed-attempt usage: paid
   failed calls/retries remain charged or explicitly unknown.
   Independent cost finding: core lines 1066–1071 reserve only arm manifest
   count; pre-freeze admissions and independent adjudication have no reservation
   or usage slot. Terminal treatment cost is explicitly replaced with null.
   The accepted single budget therefore has no demonstrated end-to-end guard.
   Falsifier: a failed first attempt then success preserves both attempts and
   whole cost status; unavailable cost blocks scoring; admission, arm, retry,
   adjudication, and designated backup consumption share the approved total.
   No real paid call is authorized to test this. Use existing runner fixtures.

4. **Close inherited credential access in the blind harness (AC-4, AC-8; non-goals).**
   `cmd_pilot_run` combines ambient environment with Read/Glob/Grep/Bash/Write,
   empties only GH_CONFIG_DIR, and gives the clone a real GitHub origin. It
   does not isolate global git credential configuration or prevent its use by
   Bash. Local clean-tree checks cannot detect a remote write. This is a
   source-proven permission gap, not a claim that a remote write occurred.
   Falsifier: a synthetic inherited git credential helper/push target must not
   be available to the child; identity remains verifiable while remote mutation
   is refused. Preserve required auth to the model without exposing GitHub auth.
   No OS-wide arbitrary-egress guarantee or new sandbox product is requested.

5. **Preserve inline finding shape and arm-hidden input (AC-7, AC-8).**
   Inline projection is confirmed missing, not dismissed because body text
   exists: the ordinary skill's section 6a requires the surviving CODE finding's
   location/quote-bound inline representation. The new route skips directly to
   section 6c. Fresh collation of a quoted HIGH/confidence-9 contribution returns
   REQUEST_CHANGES, `inline_comments: []`, and only the severity/summary in the
   body, without file/line/quote. Restore the existing projection, not posting.
   Separately, `pilot_normalize` passes protocol-specific summary prose through
   verbatim: a supplied `Required questions resolved` survives into the blind
   sample. Removing arm keys does not make this content arm-hidden.
   Falsifiers: a real bound CODE finding produces the existing location-bound
   inline shape; equivalent control/treatment findings normalize without
   treatment-only protocol markers. Never conceal findings to hide the arm.

6. **Deliver promised proof and coherent retained documents (AC-1, AC-2, AC-6, AC-10).**
   The retained spec explicitly promises a generated question table and a
   table/catalog drift test; no generator or test reading that table was found.
   The generated status-matrix claim is likewise unsupported. New execution
   tests for `projection_mismatch` and candidate-bearing non-succeeded projected
   lanes were not found (an enum fixture is not execution of the mismatch seam).
   Add the narrow falsifiable checks or request an exact accepted-contract
   revision; do not just remove the obligation.
   Existing confirmed-blocker mismatch and pending-post ambiguity coverage was
   located and is NOT a missing-test finding. The proposed external JSONL file
   is a historical shape estimate, not a delivered-file claim; the six inline
   fixtures exist. Its stale row needs accurate record placement, not a 21st file.
   The document calls itself a retained contract while carrying shaped/pending
   state, old pass counts, and mutable implementation estimates; runtime usage
   embeds a measured timing record. Rules 1/2/6 put records with the work item.
   Preserve accepted outcomes, limits, and historical evidence when planning
   cleanup; do not assume deletion permission or count savings in advance.
   The author explicitly confirmed the new Mermaid diagram was never rendered:
   no command, result, or artifact exists. Rendering and code comparison remain
   an owed proof, not a claim that its syntax is invalid. No dependency installed.
   Falsifiers: wrong prose table/derived authority output reddens its named
   check; the diagram actually renders; retained claims match their owners.

## Faithful disposition of every Claude finding

Claude's unchanged report is `claude-result.json`: NEEDS_FIXES, eight Medium
and six Low. The identifiers below refer to its original severity/number, not
a new product label scheme.

| Claude item | Validation disposition |
|---|---|
| M1 hardcoded opt-in | Confirmed boundary weakness; group 1. Surrounding prose is an outer guard, not evidence the child receives sampled flags. |
| M2 evidence encoding/size | Latin-1 diagnostic repro confirmed; >1 MiB source-bound only; group 2. Already fails closed, not an approval bypass. |
| M3 traceback-only paths | Three CLI repros confirmed; group 2. Posting StopIteration subclaim is not established because replay validates relationships first. |
| M4 missing failed v4 receipt | Confirmed source path; group 3. Reject suggested skipping failed usage; unknown cost must stay incomplete. A failed promotion must never become an admissible timing sample. |
| M5 inherited git auth | Confirmed environment/policy gap; group 4; no remote attempt. |
| M6 inline plus prose leak | Both retained in group 5 with fresh collation/normalization observations; body-only HIGH summary is not the existing location-bound inline shape. |
| M7 payload/performance | Risk/hypothesis only, not a demonstrated speed regression or repair requirement. AC-9 is budget-gated; no optimization or manifest deletion authorized by this review. |
| M8 document/fixture gaps | Partially confirmed, group 6. Inline JSONL fixtures exist; file map is an estimate. Confirmed-blocker mismatch and pending ambiguity already have tests. |
| L1 required_gap trigger | Reproduced; group 2. Keep status/reason contract aligned without silently widening it. |
| L2 newline patterns | Reproduced acceptance by Token; group 2, low syntactic closure risk. No demonstrated stale-head/approval bypass. |
| L3 baseline archive status | Disproved: review-ablation.test.sh line 23 enables pipefail; no repair. |
| L4 mapping directory | Conditional exposure risk, not independently established defect: a tool-less adjudicator handed only the input bytes cannot read the sibling map. Do not hand over its directory; no new path option required solely for co-location. |
| L5 malformed blind finding | KeyError reproduced; group 2. Must remain explicit non-passing experiment input. |
| L6 runtime derivation | No current mismatch established. repo key hashes repository, config hash uses canonical config, and actual real-seam integration passes. New runtime accessor would be an unjustified expansion; no repair assigned. |

Claude's seven explicitly unverified questions are not carried as seven defects:
CLI help confirms empty tools means none; `structured_output` remains a stubbed
provider-format seam (no paid capability call is claimed); actual integration
proves policy/observation/rehydration compatibility; repo key matches; severity
order is CRITICAL/HIGH/MEDIUM/LOW/NIT; selected runtime case ran 8/0; pipefail
is enabled. Existing `review-shadow.test.sh` lines 228–237 exercises divergent
confirmed-blocker evidence, and posting tests exercise durable ambiguous payloads.

## Exact-revision proof and limits

- Fresh real-seam test: `python kc-pr-flow/scripts/review-capability.test.py PlannerTests.test_selected_evidence_binds_the_runtime_identity_and_rehydrates` passed 1/0 in 79.344 seconds. Six provider stubs, not models; altered model/raw usage is refused; actual runtime receipt/replay/rehydration and independent posting projection run. Projection 70.066604541 s, rehydrate 5.742714292 s are local overhead only.
- Fresh named document-check selection: closed fixtures, deterministic plan, and terminal matrix passed 3/0 in 0.008 s. No full protocol/ablation regression replay claimed.
- Fresh CI entry: `bash kc-pr-flow/scripts/review-runtime.test.sh --case profiled-receipt` passed 8/0; malformed identity/uncertain input and reused sealed start are refused. This rules out Claude's hypothesized case-allowlist failure.
- Actual without-it: delete the newly added projector function and CLI entry only in an ephemeral copy. The same prepared clean journey loses its approval-ready output: runtime exit 2; `ABORTED_INCOMPLETE/receipt_incomplete`. Product bytes never changed. Artifact: `local-checks.json`.
- Runtime blob `699535682a914a54faa22a29c42a12ad4c6fdb63` matches the implementation report; posting `70bbe96f5417369a1decf00a9bd9eea372180edc` and daemon `15542da657ccaa19a7518142f8f96dcdcd47a072` equal delivery base. Existing runtime 372/0 and shadow 213/0 are author evidence reused only for unchanged owners. The prior split protocol runs are not relabeled a single final 17/0.
- Independent section-overlap/context inspection: spec sections map to catalog/schema, adapter, existing runtime/posting, and existing experiment owner. PRODUCT's profiled Lite section and ARCHITECTURE's adapter section match exercised default-off and real receipt boundaries, subject to groups 1/5/6. No new service, daemon, dependency, posting owner, expansion, or unmapped surface was found.
- Product count: 20 files, 5,428 added+deleted lines; focused schema/catalog/test 1,256, or 1,263 including corpus. Stops remain 20 / 5,600 / 1,800. Only 172 total lines remain. Repair-plus-tests has material overrun risk; no credible within-cap estimate is asserted. Author must plan before changes, and the Captain owns any exact scope/limit delta. Documentation cleanup is not pre-authorized deletion credit.
- Runtime used: activated Python 3.13.2 in the declared existing local venv at `/Users/kent/conductor/workspaces/recce-cloud-infra-v1/brussels/.venv`, Bash 5.3.3, jq 1.7.1. No dependency installation. This is local macOS proof, not an Ubuntu hosted run; hosted incremental CI cost per PR remains unmeasured.

## Independent review provenance and measured cost

Fresh Claude Code 2.1.261 command used `--model claude-opus-5 --effort xhigh`,
`--safe-mode`, `--disable-slash-commands`, strict empty MCP, `--tools ""`, JSON
output, full frozen prompt file on stdin, and no persistence/resume/fallback.
Authentication probe: AUTH_OK method=claude.ai. Main model readback is Opus 5;
effective effort has no separate result field, so xhigh is explicit CLI-request
evidence, not an invented effective-effort readback. Internal Haiku and Fable
advisor usage is disclosed; pure-provider exclusivity was not required.

- Session: `d259cfcf-8e27-4939-a933-04e1023e5d66`; exit 0, is_error false, terminal_reason completed; one turn; spawned subagents 0, server web calls 0.
- Total USD 8.4982805: Opus 5 USD 5.9702385; Haiku USD 0.086922; Fable advisor USD 2.44112. All reported internal models are included, not just the requested model. No host-reissued request or subsequent paid consult.
- Duration 1,781,095 ms; API duration 1,782,901 ms. Usage: input 6, cache creation 294,291, cache read 127,312, output 127,084 including thinking 119,217; advisor iteration usage is separately preserved in full JSON rather than re-summed as if disjoint counters.
- Prompt SHA-256 `12949f586a6987280b5f33f8b54aafb7196e5cfdff07855e8e82c15915010221`; frozen diff SHA-256 `5a4fedb19db5ca656e69425a8a1bfb875dc1980ec384bfd6074ebb2ae61fc736`. Full prompt/diff and reproducer scripts remain locally at `/tmp/capability-validation.nNycq6`; this report retains the complete unchanged provider result and compact observed outputs.

## Captain-owned blind gate, distinct from repair

AC-8 and AC-9 remain NOT RUN: no real admission, five-pair sample, independent
paid adjudication, quality verdict, or speed improvement. No publication,
posting, merge, release, version bump, or Pilot completion is authorized.

Read-only shipped helper reproduced six historic qualifying REVIEW records,
maximum USD 4.9612, latest 2026-03-15T20:00:05Z, ledger SHA-256
`a6e8fc70c891f2840300cc132a2fa15fbe8c00080b9a95fe1fc1e90b20a7872c`.
These are old composite daemon costs, not current isolated Opus review prices.
A concrete planning allocation is USD 115: six admission units, ten ordinary
arm units, five pair-adjudication units, and two designated-backup arm units;
23 times the historical ceiling is USD 114.1076, with children/retries inside
each unit. This is NOT an enforced whole-experiment ceiling: group 3 identifies
the missing admission/adjudication accounting. It is not approval to spend or
an assurance the current model fits. The ordinary USD 8.4982805 review has a
different workload and cannot substitute for real-PR cost or timing evidence.

Next decision is the original author's bounded repair plan under unchanged
scope/stops. If it cannot credibly fit, the First Officer presents one exact
Captain-owned delta before any product edit. A later measured paid-budget
decision remains pending even after all fixable defects are removed.
