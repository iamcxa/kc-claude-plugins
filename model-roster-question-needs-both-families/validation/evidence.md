# Validation evidence: PR #765

Verdict: **REJECTED for incomplete accepted evidence**, not a demonstrated defect in the scoped resolver changes.
Observed 2026-11-02, Asia/Taipei. Candidate `57321c0b4e9006c2a80c72b4afb1aa368e1ec2a2`.
Stack base: PR #764, `562b1a87198d97bb2ae1d87b72884e390b20e146`; `origin/main` observed `146727ded0d4ce8014ea0b41a45dc3409d6b269b`.
Product tested detached at `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/roster-validation-57321c0b`; this checkout is removed after validation. The assigned product branch and bytes are unchanged.
Author report names an earlier product head, `e2eb2fb5`; all checks here use the assigned final head, including the inherited test repair and parent integration.

## Independent checks and falsifiers

The commands below ran from the detached candidate. `<package>` is `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`, resolved from the loaded validation skill, as the stage definition requires. Its version is the same 0.34.0 as the dispatch's Claude installation.
The full stage report is in the entity; logs in this folder retain primary results. Executable fixtures are tests, not live child proof.

| Criterion | Verdict | Exercise and observation | Falsifier rerun |
|---|---|---|---|
| AC-1 | Pass | `python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3 --keep` exercised all eight prerequisite combinations, block/inline extension lists, existing roster, unavailable/disabled providers, empty and malformed input, and unchanged manifests. Actual `paseo provider ls --json` matches the tested input shape; template without paseo correctly skips. | Removing the Claude prerequisite returned ask in the Codex-only case; test exit 1. |
| AC-2 | Pass | Same suite resolves three models at six efforts from committed fixtures and rejects wrong pairings and Sonnet with field errors. Own recommended fixture resolves all three rows. Exact stack-base resolver refuses Opus with `stages.ideation.provider: expected codex`, exit 1. | Flattened model list and xhigh cap each fail, exit 1. |
| AC-3 | Pass | Explicit expected rows and question are exercised: Opus/high, Sol/xhigh, Astra/xhigh. | Independent defaults and question-effort changes each fail, exit 1. |
| AC-4 | Pass | Every option id is exercised, absence is null, Claude ultra remains ultra in tuple and emits ultracode. Live Paseo list_models independently lists all six emitted ids for each model (capabilities.json). | Unmapped Claude ultra and fabricated absent effort each fail, exit 1. |
| AC-5 | Pass | Same suite exercises openai/anthropic/different-family/unverified, multiple and unknown authors, Claude Roster header and dispatch-record parsing; legacy Claude remains unknown. | Fixed-openai and mixed-family lie each fail, exit 1. |
| AC-6 | Fail: evidence incomplete | Own committed recommended fixture resolves, but is not tied to any supplied live spawn. Named real workers' current inspect settings verified; process arguments, turn model/effort and same-run low control not independently proved. Supplied Opus worker used a manual send route. This running validator cannot observe its later finish receipt. PR #763 has no merge commit. | Native low-control and missing-receipt falsifiers NOT rerun; not passed. Historical Opus route independently inspected, not recreated. |
| AC-7 | Pass | Absent/deleted/linked-root behavior, read-only manifests and null effort pass in the existing suite. | Removal of each follow-family sentence and fabricated absence effort each fail, exit 1. |
| AC-8 | Pass | `python3 <package>/scripts/adr_lint.py docs/adr --since 562b1a87198d97bb2ae1d87b72884e390b20e146`, with and without `--require 0050`: exit 0, 49 records, 0 legacy. ADR 0050 quotes rulings and retains defaults/consent; ADR 0047 points to it; resolver pointer exists. | Restoring ADR 0047 Accepted fails, exit 1. |
| AC-9 | Partial; literal diff unmet | Lint, full dispatch suite and version-parity check exit 0. `git diff --stat origin/main HEAD -- kc-dev-flow-2/references/sd/workflow.md` reports 4 additions/4 removals inherited from #764; exact stack-base diff is empty. | Adding words to workflow makes lint fail, exit 1. |
| AC-10 | Not yet due | Explicitly owed after release. Candidate remains Draft, unpublished; no predicted version or unreleased resolver is accepted as consumer evidence. | Release-bound falsifier NOT rerun before release; not passed. |
| AC-11 | Pass | Actual disposable-template builds: Claude ideation model opus with Skill bootstrap; Codex implementation/validation model null with Codex bootstrap. Full commands and envelopes retained. | Independently omitted --host under Claude: implementation emits sonnet. Both launch-sentence mutations fail, exit 1. |

All 16 mutations were independently run via `python3 -B`, against a fresh archive of the exact head, with no copied caches. See mutations.py, mutations.log and mutations/results.json. Every failure log was checked for the intended assertion rather than an environment/import error. AC-6 and AC-10 are explicitly excluded from that count.

## Native evidence and authority

- `paseo agent inspect a2d90652 --json`: actual id `a2d90652-f276-4dad-bdbd-b2b3811dfa61`, Claude/claude-opus-5-5/high, auto, closed. Created 2026-11-01T17:48:24.384Z, before this candidate. Its recent tool timeline shows a completion sent with send_agent_prompt and notifyOnFinish false, explaining that main points to itself. This is the improvised route AC-6 excludes; it is not evidence the candidate route failed.
- `paseo agent inspect 8a750bcc --json`: `8a750bcc-2b31-44d8-8bf3-0ec0b5aa5036`, Codex/gpt-6.1-sol/xhigh, auto-review, idle. Final report is present; no matched parent receipt independently established here.
- `paseo agent inspect 0602ec7c --json`: this validator `0602ec7c-de2c-45b4-92bd-13f3b67260cf`, Codex/gpt-6-astra/xhigh, auto-review, running. Dispatch-file identifier 5c030106 is not the agent id; it returned AGENT_NOT_FOUND before actual identity was resolved.
- These are Paseo settings, explicitly insufficient under AC-6. No worker assertion is promoted to runtime proof.
- The ideation report's high/low plan-mode probes were read, not independently rerun. They are not the required candidate-based, roster-resolved auto-mode integrated run.
- FO reply `e3223f76-b54a-49a2-b318-cee8b9a4f461`: “There is no committed Captain ruling changing AC-6's timing. The dispatch sentence saying a roster-resolved dispatch stays owed after delivery was FO's own and has no authority; judge AC-6 as written and classify the gap as you see it.” Thus no deferral or waiver is applied.
- `git merge-base --is-ancestor c129cb215c2630d08853eeffae0fd5a2ee7e40c6 562b1a87198d97bb2ae1d87b72884e390b20e146` exits 0 for the completion task's **candidate**, but GitHub reports #763 OPEN and mergeCommit null. This is not the required ancestry of its merge commit.
- Completion sibling's later validation report conditionally recommends PASSED pending its own callback; it supersedes the implementation report's earlier rejected-sibling observation. This does not supply this task's roster/runtime/control/receipt proof.

## Finding dispositions

- **F1 Needs decision — AC-6 integrated runtime proof remains due.** Released user/normal workflow: an adopter using the committed mixed roster through Paseo. Observable harm: no malfunction established; the current evidence cannot establish that resolved settings reach the three real workers. Protected claim: `value-ac[AC-6]` requires the same roster-resolved run and discriminating low control. Trigger evidence: fixture resolution is separate from the supplied workers; inspect is only settings echo; no approved timing amendment. FO must obtain the promised evidence or return timing/scope to the Captain. It would become Material if a supported live run applies the wrong settings.
- **F2 Needs decision — AC-6 completion proof is incomplete.** User/workflow: the same three requested stage workers finishing to FO. Harm: no current candidate callback loss established, but acceptance cannot claim complete delivery. Protected claim: `value-ac[AC-6]` requires a matched inbound receipt after each child's last turn with no improvised route. Trigger evidence: supplied Opus worker actually uses manual send_agent_prompt, Sol receipt is not established, and this validator's receipt is future. Collect compliant matched evidence; do not count historical manual sending or this eventual callback alone as the whole criterion.
- **F3 Needs decision — AC-6 merge ancestry is pending.** User/workflow: delivery of this stacked candidate after the completion task. Harm: no scoped resolver defect; upstream delivery has not occurred. Protected claim: `value-ac[AC-6]` explicitly requires the completion task's merge commit in the candidate base. Trigger evidence: #763 OPEN, mergeCommit null; candidate ancestry alone passes. This is a stack dependency, to recheck at an approved later candidate; no product repair is proposed.
- **F4 Needs decision — AC-9 literal origin/main comparison is not empty.** User/workflow: reviewing this task's workflow-reading budget. Harm: no additional words or this-task workflow edit; the parent task owns the approved wording. Protected claim: `value-ac[AC-9]` explicitly names origin/main. Trigger evidence: inherited 4+/4- diff and empty assigned-base diff, 5781 words. FO must reconcile the literal criterion with stack integration; validation does not silently change its base.
- **F5 Polish — installed checker predates final-reply grammar.** The required installed 0.34.0 dispatch checker exits 1 for implementation-1 and validation-1, demanding the obsolete main-recipient line. The candidate checker exits 0, “4 dispatch record(s) complete”, with the same records. No current delivery failure is established. Preserve the historical records; do not add a contradictory main line merely to satisfy the old checker.

No Material product-code finding was demonstrated. These proof/scope decisions prevent a PASSED recommendation under the current criteria.

## Other checks and implementation-report limits

Commands run from the candidate:
- `python3 <package>/scripts/number_guards.py check --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/.. --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/model-roster-question-needs-both-families.md --base 562b1a87198d97bb2ae1d87b72884e390b20e146`: exit 0, no findings, migrations not applicable.
- `python3 <package>/scripts/comment_ratio.py 562b1a87198d97bb2ae1d87b72884e390b20e146 HEAD --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/..`: exit 0, 1/165, 0.6% <= 5%. The added historical-fixture comment states an evidence boundary, rather than narrating code.
- `python3 <package>/scripts/design_surfaces.py check /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/model-roster-question-needs-both-families.md`: exit 0, presentable; no UI surface or changed diagram.
- `python3 <package>/scripts/doc_impact.py 562b1a87198d97bb2ae1d87b72884e390b20e146 HEAD`: every result accounted for. ADR 0047, ADR 0050 and adoption.md updated; package README unaffected (same public test command/bounded runtime claims); learning.md unaffected (no changed practice). Those dispositions were checked against the final diff.
- Installed and candidate dispatch-record checks are described in F5, including implementation checklist ownership and no unaccepted product requirements.
- Hosted PR #765 is OPEN/DRAFT at the exact head, with five SUCCESS checks. The “multi-profile route gate” job is green but its workflow skips actual gate execution for this non-release PR; it is not additional runtime proof.
- Publication/CI implementation limits are now closed by observed Draft PR and checks. Exact-head RoboRev remains **unverified**: no bound clean result was supplied or found in the task; validation did not start a new review owned by FO.
- Native proof and upstream merge limitations remain; after-release #762 update is correctly not yet due.
- Words independently counted against the exact stack base: model-roster.md 760 -> 873; adoption.md 2241 -> 2242; workflow.md 5781 -> 5781. No CI trigger changed. CI cost per PR and model spend are not measured.
- Goal sufficiency: local question/resolution/host-build behavior passes, but the accepted Pilot journey across real runtime and completion seams is not established. Minimal necessity: the exact-base refusal and 16 negative mutations justify the seven changed files; each maps to accepted behavior, its evidence or required ADR/document updates. No extra product surface found.
- No product repair, product commit, push, PR comment, review request or ready transition was performed. Native falsifiers were not replaced with synthetic proof.

## Captain acceptance script

See acceptance.md for all five exact steps, expected outputs, and the fresh-shell invocation. acceptance-output.txt is the full observed output. All five steps exited 0; the script made its own detached checkout and removed it.

This script covers local behavior and package consistency only. It does not establish AC-6 live model/effort/receipts, upstream merge ancestry, AC-9's literal origin/main equality, RoboRev, or AC-10's post-release adoption.

