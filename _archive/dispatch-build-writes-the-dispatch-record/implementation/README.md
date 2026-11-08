# Implementation evidence

Candidate: `afa4523468a2e86e6c6e0467591df00bf8e51d35`.
Base: `334d91e3165953b2ca7191e3308d80b6c02c4a99`.
Branch: `spacedock-ensign/dispatch-build-writes-the-dispatch-record`.

`fresh/` is the decisive run: `acceptance.sh` exited 0 after exporting that exact
candidate, with `python3 -B`, `PYTHONDONTWRITEBYTECODE=1` and no exported caches.
Its three JSON test reports contain the real seam tests, lint mutation tests and
dispatch-record tests. `fresh/sd-dispatch.log` covers the real dispatch transport.
`fresh/falsifiers/results.json` and the adjacent patches/logs retain thirteen
counterexamples; a passed result there means the mutated behavior was rejected.
The CI deletion counterexample checks workflow wiring; it is not a hosted CI run.

To reproduce, supply `SPACEDOCK_BIN` (real 0.27.2 binary) and `SD_PLUGIN_ROOT`
(Spacedock source at `4d158a484ec73e184861067f8ed1e20087fdc26a`, the v0.27.2
commit pinned by CI), then run `bash --noprofile --norc acceptance.sh <absolute
code-worktree> <candidate-SHA> <absolute-output-directory>`. The local source
dependency was downloaded from GitHub's codeload archive at that full commit.
The runner declares its project-specific package and workflow paths explicitly.
The code worktree must remain at the supplied candidate; it is checked before
and after execution. No product push or PR was performed.

`lint-skills.log` is the expected before-observer-correction failure;
`lint-skills-after-observer.log` and the fresh log pass at 5931/5931 words.
FO authorized that one extra observer list entry in
`dispatch/implementation-1-message-1.md`. `adr-lint.log` and `base-adr-lint.log`
retain the installed 0.35.0 linter's known false positive on the historical ADR
0047 assertion. FO's follow-up 2 requires the candidate's corrected linter;
`fresh/adr-lint.log` is that passing result. The historical assertion is unchanged.

The `*-first.log`/`*-second.log` files retain early fixture setup failures;
they are superseded by the fresh run. `goal-without-change.log` records the base
checkout's missing writer. `doc-impact-verdicts.json` records each document's
disposition, and `lifecycle-words.json` records the per-moment recount.
`prepared-pr.md` duplicates `/tmp/impl-dispatch-build-writes-the-dispatch-record-pr.md`
for FO. Hosted CI, RoboRev, publication and independent validation remain FO-owned;
CI cost per PR was not measured.
