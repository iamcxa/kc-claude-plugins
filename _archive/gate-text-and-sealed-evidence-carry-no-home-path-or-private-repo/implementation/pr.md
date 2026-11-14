fix(kc-dev-flow-2): scan gzip headers in public state guards

Merging adds the validation acceptance-command rule and gzip-header scanning; it installs nothing and changes no live guard modes. The home class stays at warn. The private-repo class can move to refuse after this change's release is synced to the workflow README, by a reinstall FO runs.

Home can move to refuse only after all four approved conditions hold:
- (a) A release carrying PR #871 is synced to both sessions' workflow READMEs. That release is already going out under the Captain's release-order ruling; this change does not hold it.
- (b) The release carrying this change and its acceptance-command rule is synced the same way.
- (c) A count-only scan finds no in-flight task between its validation report and delivery gate with a home path in that report.
- (d) Replaying commits written after (a) finds no home hit from a dispatch or evidence writer.

The reform session authorized implementing the three nonoverlapping files on current origin/main without waiting for PR #869. AC-1 exercises main's current question/summary route. When #869 lands, its record route removes FO's hand-written gate summary; this branch neither stacks on nor changes that route.

The guard scans each gzip layer's raw bytes alongside its decompressed content. This includes filename, comment and extra fields in concatenated members and nested gzip. Broad owner-supplied `re:` patterns can match compressed bytes; a refusal identifies the affected file and class. The validation rule writes home paths as unquoted `~/…` words, names no private repository, and passes paths into retained scripts as arguments. Sealed private evidence still follows the existing drop-and-record-reproduction route.

Validation at d8ce3421219a8ff6112628de7cbf5f46274c634a (base c9b2c240078238b66c98179c4ddc686eac0e3918):
- Installed-hook suite: 14 tests pass, including private header refusals and clean gzip commits/pushes. The regression fails when raw headers or intermediate gzip layers are discarded.
- Real steps, question and Spacedock 0.27.2 gate preparation pass on an invented throwaway workflow with its own remote. Its committed blobs contain neither fixture-home bytes nor the invented private name. Absolute-home text is refused; mixed command forms fail coverage.
- Sealed private evidence and a reproduce line retaining its private name are refused; dropping the evidence and using a placeholder re-seals and commits. Matched names are not printed.
- The sealed argument-taking script exits 0 from fresh bash and zsh; the sealed literal-home script exits 1. Removing the acceptance-rule sentence fails its check.
- Bounded post-candidate replay c59f13d255f7bed028e68e7ba3b04a1bb0c9295e..180ee2461a0af267e545467c71fc0e195aaee961: one public state commit passes, no identifier classes hit. All 110 gzip blobs at that tip were scanned; 92 have a filename or comment, with zero raw-only class hits. This is not evidence for future dispatches or live rollout.
- Repository lint-skills, ADR lint, number guards and comment-ratio checks pass; added-code comment ratio is 0% against the 5% maximum.
- All 29 Python entries listed by `.github/workflows/kc-dev-flow-2-tests.yml` pass locally, using Spacedock 0.27.2 and upstream plugin root 4d158a484ec73e184861067f8ed1e20087fdc26a (`runs/ci.json`, `runs/ci.xml`, individual `runs/ci-*.log`).

Evidence: this task's `evidence/implementation-1/runs/` on the public state branch, including `probe.json`, `probe-commands.json`, `replay.json`, `mutations.json`, `guard-tests-candidate.log`, and the CI entry reports.

RoboRev and hosted CI: not run by the worker; FO owns them. CI cost per PR: not measured; this change edits no CI trigger or job.
