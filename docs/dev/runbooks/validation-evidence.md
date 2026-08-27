# Validation Evidence Runbook

Load this runbook for Production validation, or when accepted Pilot evidence
explicitly names it. POC never loads it. The selected profile verification
contract owns the mission; this runbook only binds evidence to the exact change.

## Bind the claim

Record the exact candidate revision, merge-target revision, accepted claim or
AC revision, and the instruments that can falsify each material claim. A stale
buffer, base commit, remote trunk, and worktree are different artifacts.

Use the smallest evidence set that can fail the accepted claims. Do not create
empty fields, mandatory `N/A` lines, a prose transcript of routine checks, or a
review round for an unfired risk.

```text
Revision: <candidate and merge target>
Accepted claims: <claim -> falsifier>
Observed journey: <scenario and result>
Fired risks: <only applicable risk -> evidence>
Provider feedback: <finding disposition when a delivery artifact exists>
Residual: <material unproved limit or none>
```

## Select evidence by risk

- behavior: accepted journey, errors, fallback, and swallowed failures;
- contract/schema: producer-consumer compatibility, migration, and defaults;
- state/concurrency: ownership, interruption, retry, and duplicate delivery;
- security/privacy: trust boundaries, credentials, disclosure, and destructive
  scope;
- runtime/platform: relevant OS, clock, tool, configuration, and timeout edge;
- delivery: exact-head provider checks, version propagation, install, and
  release surfaces.

Measure diff coverage only when it changes confidence in owned behavior. Run an
adversarial probe only for a claimed guard. RoboRev evidence uses fixed reviewer
Codex `gpt-5.6-terra`, reasoning `medium`, and `panel: none`; actual host and
implementation family are provenance only.
Science Officer remains risk-triggered and advisory.

When an accepted claim originated in a consumer or external runtime, re-observe
that reported scenario in the originating runtime or a justified equivalent.
Name the actor, instrument, delivery path, configuration, claim-relevant
conditions, exact artifact revision, and result. An unavailable runtime is
missing evidence, not a pass.

## Correction

Route material failures to one implementation owner. Re-enter validation at the
changed revision and perform one final re-verification of affected claims. If
the same boundary fails twice, ask Chief Engineer for the next smallest delivery
step; use Science Officer only when the underlying technical judgment is
contested, high-risk, hard to reverse, or low confidence.

Delete unmapped implementation scope or ask the Captain to authorize it. Do not
expand acceptance, add ceremony, or compress required proof silently.
