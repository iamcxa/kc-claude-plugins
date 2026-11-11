feat(kc-dev-flow-2): hold task budget overruns for the Captain

Implementation and validation dispatches show Budget and spent cycles, holding
the first admitted overrun before build. Fixed cycle budgets and total-dispatch
caps support a deliberate bound; only follow-up records with named symptoms count
toward totals. Minutes remain visible and uncounted. A hold defaults to keeping
results, reporting remaining work and stopping additions unless the Captain
replaces that outcome. Older first records without a Budget header stay exempt,
and raising a bound requires verbatim authority in the same Captain amendment.

New seeds require countable budgets; ideation designs require Worth questions.
The Worth check reads the native parsed stage when needed, so YAML comments or
quotes cannot bypass it, and ignores headings inside HTML comments or code
examples. Native read failures or mismatched responses refuse the check. Other
legacy stage/section readers are preserved and their sibling findings are reported
to FO. Backlog presents Budget and ideation presents the answers. ADR 0077 records
the Captain's rulings and amends ADR 0026; no separate Material-finding rule is added.

Local candidate: 6da9a765ee04e1e2c7836517ba01f75b0ea91d73, task base
e8664a72b0f904e5dda3c391d52ab3abaca876b4. The three repair files are children of
rejected head 5bf7cf78866a2f0f6376c15b59fc400519c5ffeb. Both regression tests fail
against that exact parent and pass after the fix. Four repair reverse mutations
and the previous 24 falsifiers are caught; original tests/assertions are unchanged.
All 28 local CI commands have a passing final result: 27 in the full run, with the
one missing-cache setup failure retained and rerun successfully using the same
plugin version from its remaining cache. The tested product patch matches the
commit. Lint, ADR 0077, fresh reserved-number and comment checks pass; comments
12/517 (2.3%, maximum 5%). Exact evidence and the pre-edit sibling inventory are
saved in the task's implementation-3 folder.

Local binary/plugin test root: Spacedock 0.27.2/0.27.3; hosted CI pins both to
0.27.2. This worker did not push the product branch, edit the existing Draft PR
#841, run RoboRev or hosted CI, merge, release, or deliver to adopters. Those steps
remain FO-owned; CI cost was not measured and no CI trigger or version changed.

Refs #837
