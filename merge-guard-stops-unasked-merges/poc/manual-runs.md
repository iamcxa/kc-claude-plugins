# Runs outside run.sh (2026-11-06)

1. Claude interactive, auto mode (tmux, `claude --setting-sources project --settings <hook> --permission-mode auto`,
   non-matching merge): screen in `claude-tui-nomatch-prompt.txt` shows "Hook PreToolUse:Bash requires confirmation
   for this command" and "Do you want to proceed? 1. Yes 2. No" with the guard's reason; answered 2; the fake gh
   log had no `pr merge` line. The folder-trust dialog for the throwaway folder was answered "trust" first.
2. Codex with the operator's execpolicy rules loaded (no `--ignore-rules`, so `prefix_rule(["gh","pr","merge"], allow)`
   applies) and `-c approval_policy="on-request"`, plain `gh pr merge 1 --repo merge-guard-poc/does-not-exist ...`
   at the non-matching head: `command -v gh` printed /opt/homebrew/bin/gh (the real gh, zsh -lc reset PATH), and the
   router logged "Command blocked by PreToolUse hook: merge guard: no task's newest merge/ask-N.json carries ...";
   the merge never ran. The run then idled until the 300 s timeout (exit 124) with no final message. Hook log of this
   run was lost when run.sh reset /tmp; the two lines are quoted from the session transcript.
3. Codex with the hook in the throwaway folder's `.codex/hooks.json` (with `--ignore-user-config`): the hook did not
   fire and the merge ran. Bounded: the folder was not a trusted project, and trust lives in the ignored user config.
4. `codex-askroute-stderr.txt`: stderr of the `ask` run; no warning that `ask` is unsupported. The binary's strings
   carry "unsupported permissionDecision:ask" and "unsupported permissionDecision:allow".
