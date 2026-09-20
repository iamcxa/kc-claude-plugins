# Replacement admission checkpoint — STOP

The one authorized replacement admission was launched and stopped after 27.04 seconds.
No complete legacy classification or final cost receipt exists, so this is not an
eligibility pass, candidate-quality result, comparison, or implementation completion.
Control, treatment, calibration and judge were not run. No retry or configuration
repair followed. [Summary and evidence hashes](summary.json) retain exact attribution.

## Invocation correction and frozen inputs

Captain approval `核准重跑` was registered in the separate private `runs/dev434-retry1`
directory before any model call. All retained first-attempt artifact hashes still
match; its unknown cost remains unknown. PR #434, original metadata/base/head,
control `6bf62d1d7d3c343a97c973a7abd7424d03676437`, candidate
`0d2e3164ccd2d60006688c5443717b818825a305`, Opus 5/high, and the four non-transferable
allocations are unchanged. Admission used `--max-budget-usd 4.9612`; that is a
reported-cost stop with possible overshoot, not a guaranteed invoice ceiling.
Max subscription authentication proves neither extra billing nor zero cost.

Local CLI help established `claude auth status --json` subcommand-first syntax.
A harmless argument/empty-stdin probe preserved literal `auth status --json` and
observed EOF; a TERM-ignoring process was killed by a preinstalled timeout in about
0.4 seconds. The real auth-only subprocess used DEVNULL, preopened stdout/stderr,
a 15-second timeout plus 1-second KILL fallback, and exited 0 with claude.ai Max.
No credentials were read or exposed. No model-only availability probe was run.

The sole admission used an explicit prompt file, `-p`, stream-json/verbose, and
preopened durable stdout/stderr. Its external GNU timeout started before Claude,
TERM at 1,198 seconds and KILL two seconds later; the driver created a new process
group, retained PID/exit/readback, and rejected a second invocation via an exclusive
claim file. This private single-attempt driver is evidence, not a standing harness;
it has no authorized reuse and can be removed with the private run after retention.
Exact argv/environment overrides and prompt are bound by hashes in the summary.

`--bare` was omitted because local help excludes OAuth/keychain in that mode.
The normal-auth configuration used `--restricted`, empty setting sources,
`disableAllHooks=true`, `autoMemoryEnabled=false`, empty enabledPlugins, the exact
explicit control plugin, strict empty MCP config, dontAsk, and Read/Grep/Glob/Bash.
Startup reported exactly Opus 5, those four tools, the one pinned control plugin,
and zero MCP servers. Debug reported skipped plugin hooks and zero active hooks;
no hook execution event was emitted. High effort was set in argv and environment;
an independent effective-effort field was not available. No fallback was configured
or observed in the four retained assistant message IDs.

## Stop trigger and attributable effects

The model attempted `rtk ls <RUN>/admission/kc-pr-flow/reference/`; the exact expanded
command is in summary.json. dontAsk denied it because Bash allowed only git/rtk git
patterns. That listing supported triage but was not indispensable: Glob was already
available. The early progress description of a necessary Bash failure was too strong.
The transcript also retains four successful Reads and three successful Greps; it
contains no successful Bash, Agent dispatch, write tool or network tool.

Separately, the CLI itself attempted a background refresh of `cargento-marketplace`
at `~/.claude/plugins/marketplaces/spacedock-dev-cargento`: its debug log reports a
failed git pull, then a clone attempt from `git@github.com:spacedock-dev/cargento.git`,
then unavailable marketplace.json. This occurred despite DISABLE_AUTOUPDATER=1 and
no declared marketplaces in the headless installer. It is an unexpected host effect,
not a model tool action, extra loaded plugin, or proof that an agent ran a network tool.
Post-stop readback found the directory absent; there is no captured before state,
so deletion attribution, successful clone and net tree mutation remain unknown.
No remote write/push is evidenced. No marketplace repair was attempted.

The operator sent SIGTERM to the owned group; the timeout wrapper exited -15 and
its group was absent on readback. The 27.04 seconds measures local process lifetime,
not externally observed whole-arm time. Later process listing found no Claude
command for this run. The 74 control files match the pinned Git archive byte-for-byte;
both product and target tracked trees are clean at their original heads; the Claude
binary hash and all retained old-attempt hashes still match.

## Usage, comparison and next boundary

The raw stream and session transcript show four unique main assistant message IDs:
8 input, 25,752 cache-write, 52,551 cache-read and 2,196 output tokens. Repeated/chunked
IDs were deduplicated using the maximum retained numeric usage per ID, including
completed per-message fields from the session transcript. These are partial observed
subtotals; interrupted in-flight usage may be absent. No final result/usage receipt
or dollar figure exists. Current host dollars, additional Max charges, old-attempt
cost and proven cumulative invoice are all unknown, never zero.

The pure unchanged candidate planner ran with the identical frozen PR identity and
file metadata and returned Lite/bugfix with four false booleans. Legacy modes are
absent, so comparison is unavailable and this attempt stops. No accidental first-run
analysis was reused. Human calibration and external timing are still unperformed.

The comparison is not demonstrated operable with this frozen normal-auth configuration:
its background marketplace refresh crossed the no-unexplained-effect boundary.
Return that concrete host-control gap to FO; do not infer a broken candidate, introduce
new isolation infrastructure, alter product/global config, or authorize a third attempt.
State remains implementation, with no gate, validation or product delivery action.
