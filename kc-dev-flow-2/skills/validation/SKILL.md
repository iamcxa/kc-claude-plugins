---
name: validation
description: Validate a dispatched kc-dev-flow-2 outcome against its recorded profile, exact artifact and accepted evidence boundary.
---

# Validation

Invocation: `kc-dev-flow-2:validation`

Package root: ${CLAUDE_PLUGIN_ROOT}
`<package>` in this skill and its linked files is this root. If the value above
is not an absolute path, the root is two directories above this `SKILL.md`.

Read the [framework](../../README.md) for authority and stage ownership.
Required inputs: the exact work item, recorded variant/profile, current stage,
approved scope and the stage's available artifact/evidence. Resolve inconsistencies
with FO rather than inferring a selection or loading another variant.

## Profile routes

<!-- profile-routes -->
| Profile | Availability | Profile principles | Stage reference |
| --- | --- | --- | --- |
| poc | active | [poc](../../references/profiles/poc.md) | [poc](profiles/poc.md) |
| pilot | active | [pilot](../../references/profiles/pilot.md) | [pilot](profiles/pilot.md) |
| prod | active | [prod](../../references/profiles/prod.md) | [prod](profiles/prod.md) |
<!-- /profile-routes -->

Select the recorded row and read its shared profile principles first, then
[stage principles](principles.md), then that row's stage reference and relevant
adopted project learning. A `skip` row means report the inapplicable dispatch;
do not perform stage work or create an extra gate. Unknown profiles or missing
references require a hold report, not a default route.
Before useful work, a resumed or reused worker re-establishes these inputs and
loads the current selected references. End the dispatch context with a short
profile/boundary reminder rather than another copy of the rules.
When work changes retained documents or behavior they describe, read
[retained-document practices](../../references/retained-documents.md).
Return the stage output and unresolved decisions to FO in a stage report
Spacedock 0.27.2 parses by exact form: a `## Stage Report: <stage>` heading with
nothing else on that line, then unindented `- DONE: <item>`, `- SKIPPED: <item>`,
or `- FAILED: <item>` bullets — not `- [x]`. Checklist parsing stops at the first
`### ` sub-heading, so put any `### ` sections after the bullets, not inside them.
`FAILED:` marks only an item that was not met; a report with nothing failed has
no `FAILED:` bullet, and a summary such as "FAILED: none" is never a bullet. To correct a report, append a complete new one under the same `## Stage Report: <stage>` heading: every item DONE or SKIPPED with its evidence, and a closing `### Summary` that says it supersedes the earlier report. Spacedock's completeness check and the validation readers use the newest report for the stage, and a short addendum passes that check while hiding the earlier items.
This skill grants no state, approval or delivery authority.
