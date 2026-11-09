# Frozen PR #812 replay fixture

Authorized by dispatch/implementation-1-message-1.md. Cutoff: 2026-11-08T11:13:00Z.
Every substitution and removal with source, record id and timestamp is in rewrites.json.
Live sources are preserved under ../source; they are not served. PR fields, checks and run attempt 3 use the contemporaneous hosted-refresh captures. The PR body uses the committed prepared body, not a historical GitHub response. Review comment moving commit_id values are frozen to the historical head; original_commit_id is retained. The target comment exists at run start, unlike the original two-minute delay. All other records created or updated after cutoff are excluded. Shim calls not registered are refused, logged and invalidate a run.

## Harness repair authorized by implementation-1-message-2
The interrupted attempt is excluded from D1 by FO; it remains one raw provider attempt against the hard-stop budget. No completed report or outcome was observed. Fixed Codex invocations set allow_login_shell=false (official OpenAI configuration reference: https://learn.chatgpt.com/docs/config-file/config-reference), retain normal HOME, and inherit the shell guard environment. Per-run ZDOTDIR startup files reset PATH after system login startup; BASH_ENV does the same for bash. Preflight checks zsh and bash, login and non-login; every resolution must be the registered shim or the run refuses to launch. Scope notes additionally require the absolute shim path and prohibit bypass. shell.jsonl records shell startup and gh.jsonl records transport calls. This proves ordinary child command resolution on the tested shells; it is not an OS-level denial of malicious absolute binary execution.


## One registered fixture extension
See extension-1.json and live source/extension-run-attempt-3.json. Adds the recorded third-attempt number and database id to run-view projections, plus truthful field-gap logging. The triggering codex-base-1-fixed run is excluded even if it completes; its original refused field remains in the raw event stream. This transport projection does not validate real gh JSON field syntax. No second extension is available.

The initial reconstruction script is retained as ../prepare_fixture_initial.py. It predates the explicitly recorded metadata extension and shell repair; final fixture bytes and rewrite records are authoritative. Do not regenerate over the retained final evidence.
