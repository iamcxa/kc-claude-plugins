# Admission checkpoint — STOP

The intended admission did not run. An operator preflight command entered a model
session before durable registration, with no budget/deadline flags on that accidental
path. This is our invocation error, not candidate behavior, a valid admission,
a Lite-review quality failure or a comparison result. The pair is stopped; control,
treatment, calibration and judge are all not run. There is no replay, replacement,
manual eligibility fallback or budget reset.

## What happened

Read-only checks confirmed the approved PR #434 metadata/base/head/patch, the exact
Claude Code 2.1.273 binary, all 74 control-plugin files and toolkit source bytes.
The old readiness audit also hashed transient toolkit `.in_use/` files; a missing
runtime marker interrupted the first source check. Those transient markers were
excluded from source parity without changing any plugin bytes; the admission did
not require loading that toolkit.

The proposed `--bare` flag conflicts with this machine's authentication: local
help says bare mode skips OAuth/keychain, while the existing login is claude.ai Max
with no process API key or configured apiKeyHelper. An invocation-only alternative
used `--restricted`, empty setting sources, explicit disabled hooks/auto memory,
pinned plugin and model/effort/tool arguments. No user settings were edited.

The configured auth-check command ended with the variadic sequence
`--add-dir <admission-directory> auth status`. It failed to follow the intended
non-model subcommand path and read inherited stdin as user input. The exact submitted
text was the enclosing 5,786-character Python preflight script, beginning
`from pathlib import Path`, not a separately created admission prompt. Its full
unedited text is private in `registration/accidental-submitted-user-text.txt`,
SHA-256 `df8b468f08ac48b0cef7814af300b1562b22842ce7c0ca7c90ce12ed62cc62ac`.
It contains the planned prompt/registration-writing code; this does not mean that
registration executed before the accidental calls.

The owned CLI was stopped with SIGTERM to PID 39866 after its unexpected stall.
The enclosing Python process exited 1 while parsing unavailable/empty captured
stdout as JSON. The CLI's exact exit code was not retained, so it is not inferred
from the signal. Original stdout/stderr were captured only in that failed parent
process and are unavailable; the complete on-disk session transcript is retained
privately instead. Missing raw streams remain a stated evidence loss.

The later bounded auth-only check, with a scalar flag after the variadic directory
option and a 15-second GNU timeout, returned exit 0 and claude.ai Max status.
This happened before transcript inspection established the accidental provider
calls; it did not send the intended admission prompt and does not erase or repair
the failed attempt. No further probe or model call followed that finding.

## Observed effects and usage

The transcript's model attachment and four unique main assistant message IDs show
`claude-opus-5`. Eleven assistant records contain repeated/chunked IDs; they are
not eleven independently counted requests. Deduplicated observed subtotals are:

| Field | Observed tokens |
| --- | ---: |
| Input | 8 |
| Cache write | 17,490 |
| Cache read | 36,809 |
| Output | 3,047 |

These are retained main-message usage fields, not a complete final bill or proven
whole-session total. A terminated response or background work may be missing.
Final host dollar cost and additional billed dollars are **unknown**, never zero.
The auth lane is claude.ai Max; token-derived reported cost would not itself prove
an additional charge. The accidental command had neither `--max-budget-usd` nor an
explicit timeout: the planned admission's USD 4.9612 threshold never protected it.

The effective tool snapshot contains Bash, Glob, Grep and Read. High effort was
commanded; an independent effective-effort field was not retained. Configured
hooks/settings were explicit, but no complete effective-hooks/loaded-plugin
receipt exists; source-byte parity does not prove runtime discovery.

Six tool attempts appear: two Bash commands and one out-of-root Glob were denied;
two in-root Globs and one local `git rev-parse HEAD` succeeded. The returned head
was the frozen `29007f90fc628ae40faf2903dd02d9895f4dcffe`. No Agent dispatch, write
operation or network tool is present in this transcript. Both the task product
worktree and disposable admission target have clean tracked status, and all
74 control-plugin files retain their original hashes. Those observations bound
our no-mutation/no-external-effect finding; they are not a global machine audit.
Original launch PIDs and Claude processes naming this run were absent on the
retained process readback, and no delegated descendants were observed.

## Exact evidence and disposition

Private root:
`/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v2/.worktrees/spacedock-ensign-pr-review-lite-value-pilot/.context/pr-review-lite-value-pilot/runs/dev434/registration/`.

- `failed-auth-session.raw.jsonl`: original transcript copy for session
  `156002d7-7954-4b78-bf32-ccbc0fb9488d`.
- `accidental-submitted-user-text.txt`: exact inherited input, without normalization.
- `failed-auth-command.json`: observed command reconstructed from the retained
  tool invocation/process listing, with lost stdout/stderr explicitly marked.
- `failed-auth-summary.private.json` and `effective-snapshot-summary.json`:
  attributable request IDs, usage, effective tool/model evidence and tool calls.
- `configured-auth-interruption.json` and `process-readback.json`: owned-process
  stop and absence readback.
- `configured-auth.stdout`, `configured-auth.stderr`, `configured-auth-check.json`:
  later bounded auth-only result, kept private because it contains account identity.
- `preflight.json`, `plugin-files.json`, `live-sample.json`: exact source/auth/input
  readbacks before the failure. [summary.json](summary.json) binds their hashes.

There are no actual legacy admission modes to compare. The unchanged frozen
candidate planner output is Lite/bugfix with full_pass, probe_required, cross_model
and noise_filter false; it cannot substitute for missing legacy triage. No human
calibration confirmation, review-arm timing or independent judgment is fabricated.

Remediation guidance only: the direct subcommand-first `claude auth status` syntax
already returned the expected non-model result. Future non-model subprocesses
must explicitly use `stdin=DEVNULL` and an execution timeout before process start,
and must not leave a variadic option adjacent to subcommand words. These are
operator invocation corrections, not a product patch or authorization to repeat
this pair. The input isolation/deadline guidance was not tested with another call.

Recommend reporting this stopped pair and preserving its incomplete cost evidence.
Any new attempt requires a separate explicit decision; no candidate source repair,
new observer, automatic retry or continuation is authorized by this checkpoint.
