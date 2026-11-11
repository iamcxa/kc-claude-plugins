feat(kc-dev-flow-2): hold task budget overruns for the Captain

Implementation and validation dispatches now show the recorded Budget and spent
cycles, holding the first admitted overrun before build. Budgets support the two
fixed cycle forms and a total-dispatch cap; named-symptom follow-up messages count
toward the total, answer messages and special-role records do not. Mixed minutes
stay visible but uncounted. A hold defaults to preserving results, reporting the
remaining work and stopping additions unless the Captain replaces that outcome.

New seeds require a countable Budget and ideation designs require Worth questions.
Ideation gates show the answers; backlog gates show Budget. Old first dispatch
records without a Budget header remain exempt, and a larger bound needs the
same amendment's verbatim Asked/Captain authority. Countable tasks lose the old
advisory reminder; existing special-role events remain. ADR 0077 records the bound
Captain rulings and amends ADR 0026. No separate Material-finding repair rule is added.

Validation at local candidate 5bf7cf78866a2f0f6376c15b59fc400519c5ffeb, base
e8664a72b0f904e5dda3c391d52ab3abaca876b4: all 28 local Python commands from the
unchanged CI workflow exit 0, with original documented skips retained; 24 mutation
falsifiers are caught. Actual CLI dispatch tests cover removal-before-build and
preserved results; the merge boundary probe retains old-record compatibility.
Four pinned state replays and independent workflow/lifecycle word counts are saved
with the task report. Required lint, ADR, reserved-number and comment checks pass.
Test fixture updates retain every existing assertion and negative case; exact
changed lines are listed for independent validation under amendments 4 and 6.

Local binary: Spacedock 0.27.2, with plugin root 0.27.3; hosted CI pins both to 0.27.2. Hosted CI, RoboRev, product
push and Draft PR creation are not run by this worker and remain FO-owned. CI cost
was not measured; no workflow/trigger, version or migration was changed. No release
or adopter-delivery claim is made.

Refs #837
