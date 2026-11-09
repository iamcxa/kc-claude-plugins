# Replay result: HOLD, no behavioral verdict

The first Codex base run started gpt-6-astra at xhigh, then was interrupted when the launcher PATH control was shown invalid. The login shell resolved /opt/homebrew/bin/gh rather than the registered shim. events.jsonl records real gh command invocations and no shim log was created. The CLI wrapper returned 0 after SIGTERM, but there is no completed stage report or turn-completed usage event; exit 0 is not a successful run. See path-preflight.json and bypassed-shim-commands.json. No model or wording failure is inferred.

| Host | Arm | Wording | Verdict | Found | Read comments | Precision miss | Tokens | Counted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Codex gpt-6-astra xhigh | base 1 | original | no completed report; invalid harness | not measured | not measured | not measured | not returned | no |

Attempts: 1 of planned 12, hard stop 16. D1 stops the task after the first incomplete Codex attempt. Claude and the remaining Codex cells were not run. No wording-2 run or third wording was used. Neither per-host stop condition, precision, report-word means nor cost can be evaluated. The product candidate remains wording 1; it has static proof only.

Pre-registration commit: e7e7b74b4, before runs/codex-base-1 was created. Historical fixture substitutions/removals follow dispatch/implementation-1-message-1.md and fixture/rewrites.json. Static checks and the workflow-budget/grader/shim-refusal controls pass. The shim refusal control alone did not exercise the host login-shell boundary; that missing preflight caused this failure.

Needs decision for FO: repair and prove the launcher's command resolution, then obtain explicit restart authority. The Captain's D1 ruling does not permit silently retrying or substituting a Claude-only result. This is a harness defect, not evidence that Codex cannot authenticate or that wording 1 misses review comments.
