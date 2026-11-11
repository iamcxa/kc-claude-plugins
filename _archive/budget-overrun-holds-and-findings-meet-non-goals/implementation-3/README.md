# Worth section validation repair

Candidate: 6da9a765ee04e1e2c7836517ba01f75b0ea91d73.
Repair parent / rejected PR head: 5bf7cf78866a2f0f6376c15b59fc400519c5ffeb.
Task base: e8664a72b0f904e5dda3c391d52ab3abaca876b4.
Branch: spacedock-ensign/budget-overrun-holds-and-findings-meet-non-goals.
Assignment: dispatch/implementation-1-message-5.md, repair F1/F2 after validation-1.
Commands run on 2026-11-11. No product push, PR edit, review comment, version edit,
RoboRev, hosted CI, merge, release or adopter rollout was performed by this worker.
FO owns pushing the local repair to existing Draft PR #841 and its fresh review.
CI cost was not measured; CI definitions and triggers are unchanged.

## Owned repair

F1: only the new Worth check reads stage with Spacedock's parsed single-file
`status --read <absolute-task> --json`. It reuses dispatch_records.find_readme
to select the definition root for split-root tasks, falling back to the file's
parent for standalone files. The returned command, canonical path, frontmatter
mapping and status type are checked. A missing executable, command failure,
timeout, malformed response or response bound to another file refuses the check.
There is no new YAML scalar parser or regex fallback. SPACEDOCK_BIN selects the
binary; otherwise it must be on PATH. The query is needed only when the Worth
heading and explicit Design section are both absent and opening frontmatter
could make this an ideation task. Ordinary complete designs add no native query.

F2: a local visible-line scan for Worth tracks code fences and HTML comments
together, so closed or unterminated comments cannot supply a heading. A fence
marker inside a comment does not hide a later real heading; a literal comment
opener inside a fenced example does not consume a later real section. The same
filtered lines decide the explicit Design boundary and Worth heading. Other
section readers and their inputs are unchanged.

Only design_surfaces.py and its two existing named test files changed this round.
scope-proof.json confirms every other pre-existing function, every pre-existing
test method, and the legacy status branches/main remain unchanged. No older
assertion or negative case was removed or weakened; no stale fixture updates
under amendment 6 were needed in this repair.

## Failing before, passing after

f1-red.log and f2-red.log were produced before production edits at parent 5bf7cf788.
They show assertion failures for the reported commented-status and hidden-heading
bypasses. focused-green.log passes six focused tests after the repair, including
the old Worth controls. The actual CLI test checks plain, commented and quoted
statuses, flat and folder-form split-root task files, input-byte preservation,
missing-section refusal and a visible-section pass. The comment test covers
closed/unclosed HTML comments plus code-fence interactions and positive controls.

repair-proof.py re-exports the exact parent and runs the final regression tests
against its production files, then against four isolated reverse mutations.
repair-proof.json records three parent tests failing and four mutants caught,
all as assertion failures with zero errors: raw-stage reading restored, HTML-blind
scanning restored, native read errors ignored, and response binding/type checks
removed. previous-mutations.py re-runs the prior 24 Budget/Worth falsifiers;
mutations.json and raw mutation logs record all 24 caught, with no errors counted.

## Full checks and environmental retry

The initially executed final-checks.py extracts the unchanged CI workflow's 28 Python commands, saves
unpiped exits, and binds the unchanged base-to-working-tree patch in
final/test-identity.json and final/tested.patch. The initial run has 27 successes
and one setup exit: test_sd_dispatch.py's old Codex plugin-root 0.27.3 had become
absent, so argument validation exited 2 before exercising product behavior.
final/full-checks.json and its raw failed log retain that result.

Only that command was rerun with the existing Claude-cache copy of the same
plugin version 0.27.3. sd-rerun-identity.json records the path, version and mod
digests, plus the unchanged product patch. sd-rerun.log and full-summary.json
retain its result and the original setup failure. All 28 commands have a passing
final result; existing skips/Not run limits remain in their logs. The 224-test
design suite also passes with SPACEDOCK_BIN pointing to a missing executable,
showing no need to move CI's existing install step or skip old tests.

For a new full run, `python3 -B rerun-checks.py <code-worktree> <available-sd-plugin-root>`
accepts an explicit root and writes a separate reproduced/ output directory; it
preserves the initial commands/evidence rather than reusing the absent root.

The local native binary reports 0.27.2, plugin test root is 0.27.3; hosted CI pins
both to 0.27.2. This is local evidence, not a hosted CI or 0.28.0 runtime claim.
identity-at-commit.json compares the final commit's bytes to the tested patch.
Required post-commit lint, ADR 0077, number and comment checks all exit 0: 6008/6008
workflow words, 68 ADRs, fresh state number fetch, comments 12/517 (2.3%, max 5%).
required-checks.json and the raw logs retain each result. All 14 affected documents
have updated/unaffected reasons in doc-impact-verdicts.jsonl.

## Sibling sites listed before code changes

sibling-sites.json and sibling-sites.md inventory every other stage read and
required Markdown section selector, plus the related label/report-root readers,
at parent 5bf7cf788 before code edits. Only the two new Worth consumers were
selected for repair. sibling-probes.json records nine representative observations
before edits; sibling-probes-after.json reproduces the same observations after.
The old stage review bypasses and hidden FO/AC/amendment/unterminated-seed cases
are not silently repaired. Closed seed comments were already ignored.

sibling-findings.json sends the remaining 15 entries to FO, distinguishing
executed failures from source-only risks. In particular, commented statuses still
skip the old prod security, UI design and built-screen review checks; scope
classification and the gate reminder still use the old regex. HTML-comment-blind
FO alignment, acceptance criteria, amendment/Scope/validation-report selectors
and required body labels remain outside this repair. The report-root mapping
checks consume YAML reports rather than rendered Markdown; their HTML rendering
semantics were not claimed to be a matching defect.

The corpus checker was rerun over the same four pinned state exports in both
seed/design modes; no prior diagnostic disappeared and every addition remains
the approved Worth/fixed-Budget refusal. corpus-check.json preserves all verdicts;
pins.json names the source clones and commits. To reproduce, export those pins
with implementation-1/export.py and point corpus-md at that export. Native single
file reads do not change live state or historical task files.

The pre-change design of this task still lacks the literal Worth heading and is
refused by the candidate; validation-1 already identified this as the declared
historical compatibility cost, not permission to backfill approved designs.
Budget history replay results from implementation-2 and validation-1 are retained;
the Budget/dispatch logic was not changed by this repair. Current full suites and
24 prior falsifiers were rerun; no new Budget-history replay was required or claimed.

## Delivery handback

The prepared PR title/body is /tmp/impl-budget-overrun-holds-and-findings-meet-non-goals-pr.md,
also saved as prepared-pr.md here. The task's last complete implementation report
supersedes earlier implementation reports. FO must push this local candidate,
re-run RoboRev and obtain an independent validation recheck before delivery.
