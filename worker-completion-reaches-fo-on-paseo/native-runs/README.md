# Real runs for AC-1 and AC-2, FO-run on the receiving FO (Paseo 2e87a82e), 2026-11-02, candidate c129cb215

Every spawn used `create_agent` with notifyOnFinish true and an explicit modeId. Prompts carried the candidate's sentence that the final reply is the completion message. These are cheap probes (Haiku, Sol low), not stage dispatches; the real stage dispatch is the next task's.

| Run | Agent | Event received by FO | Body |
|---|---|---|---|
| Claude, Done line | f33b5aa3 | finished | `Done: AC-1 Claude read CLAUDE.md completed implementation. Do not change any file.` |
| Codex, Done line | e48b1442 | finished | `Done: AC-1 Codex read CLAUDE.md completed implementation.` |
| No Done line | e97e30ec | finished | a sentence about the weather, no Done line |
| Cancelled | 1aef76e0 | errored, "was canceled" | none |
| Permission | e627ae31 | permission-required, Write /tmp/b12-hold-test.txt | FO did not respond; it killed the probe |

Failed attempts at the permission case: b489a552 ran `date` with no prompt; ea3b9b09 refused a send it judged to come from another agent. Neither is evidence.

Limits: the Claude body repeated part of the prompt after the Done line, so "Done" is not the last word and a strict line match would need care. A `finished` event also fires when a worker pauses for a background job (ca686dda, 2026-11-02), so FO checks the task file before treating it as completion.

Send-attempt check: in f33b5aa3.log and e48b1442.log the only match for SendMessage or send_agent_prompt is the prompt line itself; no `[Send message]` tool row appears.
