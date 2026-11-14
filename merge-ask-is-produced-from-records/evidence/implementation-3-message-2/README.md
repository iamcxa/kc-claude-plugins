# Implementation 3, feedback message 2

Candidate: a5657edd6531916cd01f659b888feaa021219ead.
Repair base: 4652caa3a2f2c28bf4e395f2473b6ca00786834a.
Scope: the authorized fail-closed visibility finding from local review job 1862.

The record producer now requests gh repo view --json visibility and saves a record only when the field is exactly PUBLIC. PRIVATE, INTERNAL, any other value or a missing field cannot pass that comparison; unknown/missing visibility keeps the existing exit-2/no-record behavior. Contract producer wording and the public field description agree. Legacy callers are unaffected.

The existing public fixture now returns visibility PUBLIC. The existing visibility test keeps PRIVATE and missing-field controls and adds exactly one INTERNAL/isPrivate=false case. No new test method was added. visibility-red.log captures the added case failing on the previous implementation; visibility-green.log captures the repaired control. visibility_probe.py runs that existing test and the existing PUBLIC record/binding test, then restores the old boolean criterion in memory. The reverse mutation fails the visibility test without errors. Test doubles establish the owned save boundary; no live API call is claimed.

checks.json joins all four requested commands to the exact candidate, exit and log: repository lint, full delivery suite, full POC suite and installed comment-ratio check. The runner checks unchanged candidate/clean tree before and after execution. Owned package caches were cleared and all commands use python3 -B, PYTHONDONTWRITEBYTECODE=1 and task-owned TMPDIR. doc-impact-dispositions.json accounts for all seven referenced ADRs plus the updated contract.

Reproduce by setting PRODUCT_WORKTREE to this candidate, PACKAGE_ROOT to the assigned kc-dev-flow-2 0.41.0 package and WORKFLOW_DIR to the adopted docs/dev2 workflow. Copy these scripts into task-owned scratch; set TMPDIR there and PYTHONDONTWRITEBYTECODE=1, then run python3 -B run_repair_checks.py and python3 -B visibility_probe.py. No credentials, private content or provider state are required for these fixture checks. Retained log paths are normalized.

No product/state push, PR write, review request, ready transition, merge, new ADR, version bump, workflow budget or CI-definition change. CI cost per PR was not measured. RoboRev, hosted CI and independent validation remain FO-owned and are not reported clean. The existing pin-deletion experiment remains separate in implementation/pr.md.
