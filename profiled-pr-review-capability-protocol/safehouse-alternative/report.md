# Existing Safehouse alternative — concrete insufficiency

**FAILED owner-integrity proof; not ready for integration.** Safehouse 0.9.0's generated Claude policy plus an exact synthetic owner-tree write deny still permits an ancestor-rename bypass. Product remains unchanged at `9bb526170156a44cff90e2a2fab9eeab081e0eb1`. This single alternative reused approval `087047c577d4f58003f6833478c345c50f7b377e`, reread before execution; the earlier native-policy evidence at `c7673f29ca023460f1aeb7b7c0f8e54ee2a6deda` is preserved unchanged.

## Actual policy inspection

The installed `kc-safehouse` and Claude skills, `/Users/kent/.codex/skills/claude/scripts/probe_auth.py`, current `safehouse --help`, and installed policy source were read. Explain/diagnostic mode only was used. No setup, package/global/project configuration or `.safehouse` file was changed. The local probe source's modern command is `claude auth status --json`, but its automatic legacy `-p` fallback would spend a model call, so that helper was not invoked.

Policy generation used a synthetic workspace, explicitly disabled workdir-config trust, removed ambient `SAFEHOUSE_*` configuration variables, and selected the actual `claude` command profile without executing it. Observed explain: explicit optional integrations **none**; implicit **keychain, browser-native-messaging, microphone**. Docker, browser automation, process-control, lldb, cloud-credentials, wide-read and other broad optional integrations were not enabled. Current 0.9.0 help/source exposes trusted workdir config and explicit append-profile; no automatic `local-overrides.sb` loader was found, despite the older skill's description. That drift was observed, not repaired.

The [exact effective profile](effective.sb) grants broad `/tmp`, `/private/tmp`, per-user temporary and several agent/toolchain writes; `network*` enables inbound/outbound access; named Mach services include DNS/system configuration and Keychain. Process info/signalling/task-port access is scoped to `same-sandbox`, not an explicit unsandboxed-parent debugger grant. The Claude profile grants write access to its local state/config and installer-managed binary locations. Named Docker/SSH-agent socket denies remain present. These are source-observed permissions, not provider roundtrips or demonstrations that a live intermediary will perform arbitrary owner writes.

The one-off appended rule was only `(deny file-write* (subpath "<exact synthetic owner tree>"))`. It was generated and stored by the parent inside that protected owner tree. No file protection was relaxed to obtain a pass.

## Reused instrument and result

The previous [instrument, extended only for this policy delta](proof.py), still imports the unchanged real runner and existing ten-record fixture, uses prelaunch hard-link refusal, and calls real `pilot_invoke`, `pilot_attempt`, parent receipt writing and `pilot_join`. It used the same owned `/tmp/pilot-isolation-proof.68ALze` root with fresh case directories. All attacked paths were synthetic; no real worktree, state, credential or user file was attacked.

An initial run could not execute the external venv symlink because that path was outside the generated readable execution scope (host exit 126, Operation not permitted). Its child never ran. The initial instrument incorrectly printed PASS on unchanged bytes alone; **that output is invalid proof and explicitly rejected**. [Its raw result](startup-binding-failure.json) is retained. The test was corrected to require actual child checks, actual detached descendant execution and successful parent finalization, and used the same already-installed Python's resolved `/opt/homebrew` executable rather than granting another writable path.

The resulting actual child ran successfully. Current preplant, earlier receipt absolute/chmod/traversal/symlink writes, creation of a new hard link, protected internal unlink/rename/rmdir, and the detached descendant write after parent finalization were all denied with errno 1. Normal workspace/output/temp writes and nested Bash execution succeeded. The synthetic auth sentinel remained available. No pre-existing hard-link alias was admitted.

**The policy failed on a directly related filesystem route:** the child renamed its synthetic case directory (the protected owner's parent) to a sibling path under writable `/tmp`, changed the earlier receipt through that new path, then renamed the directory back. The exact owner-subpath rule no longer matched during the temporary rename. The real parent subsequently finalized its own current measurement normally, and the real join accepted ten records with earlier `2-control.wallclock_ms = 1` while current `1-control.wallclock_ms = 134.459584`.

```json
{"child_exit":0,"ancestor-rename-restore":true,"prior_unchanged":false,"joined_count":10,"earlier_wallclock_ms":1,"instrument_exit":1}
```

The strict instrument ended with `AssertionError: SAFEHOUSE OWNER INTEGRITY FAIL`. This is the one concrete insufficiency that ends this alternative; no ancestor-policy patch, further sandbox search or repeated full suite was attempted. The distinct descendant PID 29486 was absent at cleanup readback; direct processes were waited by the real parent. All prior native control, hard-link failure and guarded native results remain separate historical evidence.

Actual final command, after existing venv activation and `which python`:

```sh
python -B /tmp/pilot-isolation-proof.68ALze/proof.py --safehouse
```

It generated the profile through `/opt/homebrew/bin/safehouse --workdir=<synthetic work> --trust-workdir-config=false --append-profile=<owner>/deny-owner.sb --explain --stdout -- claude --version`, then executed the synthetic Bash child with `/usr/bin/sandbox-exec -f <owner>/effective.sb`. Here `--stdout` is generation-only: **no Claude command was executed**. For reproduction, copy the retained instrument into a fresh temporary directory with the prior proof's `proof.sb`; its explicit `SOURCE` points at the pinned product checkout. The script refuses existing case directories.

Artifacts: [complete actual result](results.json), [instrument](proof.py), [effective policy](effective.sb). SHA-256 respectively: `674e6e202cb6a2f4ed63707188617184b33c2722c14d4f3d192477a7a1b74d4b`, `05ee548e825b37bae2007a6685b99e165f64272b24dbbabe36815444afa41dfb`, `75886df6d74204d76b0eaee39aa86d4d2d8bb1e351fb7521be615cd848dae38d`.

## Compatibility and remaining authority

Claude executable startup and modern auth status are **NOT RUN**, because the filesystem insufficiency triggered this alternative's stop condition first. No claim is made that auth failed, that its modern command inherently requires network, or that the generated allowances suffice. The read-only auth command remains separate from a real provider/API/structured-output roundtrip, which is also NOT RUN and unapproved. No paid legacy fallback, login or token-refresh request was made; no credential contents were read, printed or copied.

Network/local IPC and selected Mach routes are source-permitted; their ability to proxy a measurement write is unverified, not a demonstrated exploit or a demand for universal security proof. Writable agent/toolchain state is a further integrity consideration for future host launches, not a proven parent-process escape here. Privileged actors, debugger/process-memory access and inherited writable-FD misuse were not tested. The concrete blocker reported here needs none of those hypotheses: ordinary filesystem rename plus write sufficed.

Smallest conditional recommendation: **do not integrate this policy as-is**. Any future candidate must keep the existing runner as measurement owner and protect both authority files and renameable ancestors (or use a placement whose ancestor chain is outside every effective child write grant), then exercise this exact failing path before considering host/auth compatibility. This is a necessary condition, not an implemented or proven remedy. No new ledger/service or telemetry owner is proposed.

Using Safehouse for product launches would introduce an explicit external CLI/version dependency and effective-policy pinning obligation, even though it is already installed locally. It remains macOS-only here and still relies on deprecated sandbox-exec; Linux/hosted support is unproven. Both arms would require identical generated policy/features and placement rules. Missing/incompatible tools must fail before spend, not fall back to unisolated execution. Product integration, dependency/support choices and any further proof require the First Officer's scoped decision.

## Counts and handoff

Counts remain **6,431 total / 20 product paths / 1,939 complete focused**, with no reduction credit. The previous native estimate of 60–100 implementation and 80–120 focused test lines is not certified sufficient for this failed alternative. Source-backed generation/provenance plumbing adds an estimated 10–20 implementation lines over that shape, and preserving the ancestor bypass plus policy-selection/startup negatives adds roughly 10–20 focused lines: a provisional **70–120 code / 90–140 test** range, excluding unresolved auth/platform/IPC work and the other repairs. No added file is proposed if these remain in the existing runner/shell test, but the dependency/platform policy is a real lifecycle obligation.

The previously mapped 85–121 equivalent-reduction candidates remain estimates, not actual deletions. Even `1,939 + 90 − 121 = 1,908` exceeds 1,800 before the other repairs. No within-cap fit or cap increase is claimed. All five repairs, reduction, F14 sequence evidence, independent review and budget-gated AC8/9 remain pending; product, status, stage pin, review round and earlier reports remain unchanged. This report returns the concrete insufficiency to the First Officer and ends the single alternative.
