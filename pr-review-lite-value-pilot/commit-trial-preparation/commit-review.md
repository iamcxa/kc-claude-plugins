# Prospective commit review

Status: the captured two-file diff is reviewable but incomplete by itself; the minimal exact correction commit is the validated three-file kc-pr-flow projection below. No commit authority is granted here.

## Frozen source and worktree state

- Product worktree: /home/vercel-sandbox/kc-claude-plugins/.worktrees/spacedock-ensign-pr-review-lite-value-pilot-r5-accounting-correction
- Branch / HEAD: spacedock-ensign/pr-review-lite-value-pilot-r5-accounting-correction / 0d2e3164ccd2d60006688c5443717b818825a305
- Real index: zero staged paths.
- Dirty paths: exactly kc-pr-flow/scripts/review-capability.py and kc-pr-flow/scripts/review-capability.test.py.
- Frozen passed candidate: tree fd9b3a244e965157e3c48f5fba527b6670dc07b2; source/test SHA-256 a7a5e169133d8a2ac70723508d35ef1661b1c1d885276488869393ec903cc5f2 / 0074f5b279edc4478b5ecbcb37962a78dd04ac7d1236809e1894d05d45d3665e; R5-round-1 seal 39f694dc6660576be6b4a3b60dcb47f2cda69f1efd71164648d1b4e43e578637.
- Full HEAD-relative two-file patch: prospective-two-file.patch, SHA-256 a12841c2ec853cfa886f636a6e7e911f7134acc0e830b82621e0e421979a90e9, 55,496 bytes. Numstat is 145+/143- for review-capability.py and 149+/151- for review-capability.test.py: 294+/294- total.
- Proposed English commit title after integration is authorized and complete: "fix(kc-pr-flow): harden Lite provider custody and typed output".

No product byte, real index entry, branch, commit, remote or PR was changed while preparing this review.

## Accumulated behavior in the candidate

The diff is one integrated adapter/custody change accumulated across the Pilot corrections, not merely the final cost-ordering edit.

- Test selection: the profile catalog's code-change signal must include .mjs so the supplied PR434 storymap test is selected. This behavior is not in the two dirty scripts; it depends on the validated catalog blob described below.
- Trusted-host and auth boundary: normal provisioned first-party OAuth is checked through the child executable's supported auth status command. Children receive only the explicit environment-key allowlist and traffic controls, use restricted/safe mode, empty explicit settings/plugin/hook sources, no plugin directory, no MCP configuration beyond the empty contract, and no credential values in durable receipts.
- Startup proof: configured argv/settings evidence is separate from observable init. Accepted init is pinned to the requested model, the locally read CLI version, permission mode dontAsk, tool metadata exactly [StructuredOutput], empty MCP/plugins, no hook event, the fixed 16 built-in skill names, and the observed absence of setting_sources recorded as unreported. Model/version/permission/tool/skill/config/hook drift remains terminal failure.
- Typed output: result_schema exposes CapabilityResult as the provider-bound root object and carries only its transitive definitions/references. Required fields, property types/enums and additionalProperties refusal remain the repository schema contract; malformed structured output remains rejected. Local compiler/init-only evidence is model-free and does not establish provider acceptance.
- Durable attempt custody: per-attempt argv, executable hash/version, environment key names, input/settings/system-prompt hashes, stdout/stderr/debug byte counts and hashes, raw stream, parsed envelope and terminal receipt are retained. Input or repository identity drift fails closed.
- Timeout and cleanup: each child starts in a new process group, is polled against its attempt deadline, receives TERM and then KILL as necessary, retains partial streams, and records timeout or supervisor cancellation. Only exit 75 on the first attempt is retryable; terminal failure stops the run.
- Cost custody: one finite nonnegative non-boolean final-event cost is recorded once with provider_result_event provenance even when provider exit, result contract or stream/startup structure rejects the review result. The result stays failed and unusable. Missing, duplicate, conflicting, string/null, boolean, negative and nonfinite costs remain explicitly unknown.
- Downstream accounting: the unchanged R4 supervisor costs() consumer sees each retained terminal exactly once. Focused validation proved hook, missing-init and result-first failures retain USD 0.01 and cross a probe threshold; ambiguous/invalid cases aggregate zero/unknown. The six byte-exact R4 streams still total USD 1.210485, while the historical pre-fix terminal-only USD 0 remains immutable failure evidence rather than a zero-spend claim.

Relevant independent validation is cycle 15 PASSED for tree fd9b3a24. It is offline evidence only. The consumed R4 live proof reached the provider but finalized incomplete; it does not prove current provider compatibility, useful review quality, savings, calibration, two-day fit or release readiness.

## Commit projection and integration gap

A private index over HEAD with only the two dirty blobs writes prospective tree 0d34ba122130c0f77558c4ef1510e89a23078f7e. It does not equal the passed tree and its kc-pr-flow subtree 2d8194aeff6e40b6d2260d5c99d2d5170f03dd05 differs from the passed subtree only at kc-pr-flow/schemas/review-capability-catalog-v1.json.

HEAD catalog blob d2846063b65959b97861b3b6e16b34c145f219cc, SHA-256 c4194fbfb83c1fbb92f7d550e9b162022d80c34e4cc559239f37471f6f87fe48, omits mjs from code_change. Passed catalog blob 10284f91b492e2eb144a821fa34b46603681fad0, SHA-256 630006b4351569d2674e2e0fb6229cd826c995624668ba4bc49d1d35571b1da9, includes it.

A private projection over HEAD with that catalog blob plus the two passed script blobs writes tree 1922e7c86493f01923baa54824396ba9ffce25b4. Its kc-pr-flow subtree is 3dc6c1f76c952f2b189006190fc9032d7cdbcfb4, exactly the passed tree's kc-pr-flow subtree. The whole repository tree still differs from fd9b3a24 because that validation index was an integrated repository snapshot; only plugin-subtree parity is established.

The three-file HEAD-relative projection is catalog 1+/1-, source 145+/143-, test 149+/151-: 295+/295-. The one-line catalog correction adds mjs to the code_change path pattern and changes nothing else in that file. review-runtime.sh is byte-identical at blob f61d421e8ac18339319ff1e63b505e1bba6f5e78. Claude/Codex plugin manifests are byte-identical at blobs 1d00b7d4a58ee9a4d86fb3f20b35724b1d1434e8 / 12a597ac6b26746d14906e9e95c876bb61ca64cf, both version 1.12.0.

The whole marketplace diff is unrelated repository evolution: kc-plugin-forge 1.9.1 to 1.10.0; kc-team-ops description change plus 1.7.0 to 1.8.0 and journey keywords moved to the new kc-journey-map 0.4.1 entry; kc-dev-flow 4.3.0 to 4.6.0; new kc-ship-flow 0.3.0; and new kc-dev-flow-2 0.3.0. The kc-pr-flow entry is byte-identical across HEAD, the validated base and passed tree (canonical entry SHA-256 f21576646aa9f520cf7cb5aa82a843579e7a8066b3d805af32c3d7f0509f04b6) at version 1.12.0. Do not stage marketplace.json; no kc-pr-flow version bump is implied.

## Eventual staging list

Do not stage now. After separate authority materializes the already validated catalog blob and verifies the exact projected subtree, the complete correction commit stages only:

1. kc-pr-flow/schemas/review-capability-catalog-v1.json
2. kc-pr-flow/scripts/review-capability.py
3. kc-pr-flow/scripts/review-capability.test.py

Staging only the current two dirty files would omit required .mjs selection behavior and would not reproduce the passed plugin subtree. Budget allocation is not part of this staging list, is not part of the proposed title, and is not a prerequisite to committing this already validated correction.

## Remote and PR readback

- origin feature/kc-pr-review-capability-protocol-pilot remains 0d2e3164ccd2d60006688c5443717b818825a305.
- GitHub reports no open PR for that remote feature branch and no open PR for the local correction branch.
- PR 434 is MERGED at https://github.com/iamcxa/kc-claude-plugins/pull/434; its frozen base/head are 33ffd50b217004411f58277cf986ccee7974fe55 / 29007f90fc628ae40faf2903dd02d9895f4dcffe. A future trial would review that immutable snapshot, not a current live PR.

## Review disposition

Keep three decisions distinct:

1. Minimal correction commit: materialize the validated catalog blob beside the two frozen script blobs, verify tree/subtree identities, and—only with separate commit authority—commit exactly the three listed paths under the proposed title. This commit contains no budget-policy change.
2. Later budget-allocation implementation: separately design, implement and validate an explicit per-lane policy within the unchanged USD 2.4806 child-reported threshold. It creates a later candidate and is required before another paid proof, not before the correction commit.
3. Paid launch: only after a fresh packet binds that later exact candidate may a separate decision authorize one paid run. The consumed R4 packet is never reused.
