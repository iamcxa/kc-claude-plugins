# AC-6 real run, FO-run, 2026-11-02, candidate 57321c0b4

A committed fixture roster (the candidate's recommended set) was resolved by the candidate's `model_roster.py` in /tmp/roster-fixture-b12: ideation claude-opus-5-5 high, implementation gpt-6.1-sol xhigh, validation gpt-6-astra xhigh, digest sha256:64e98765c78. FO spawned each child with `create_agent`, notifyOnFinish true, using those values; the control is the same model at low.

| Child | Requested | Transcript shows | FO received | Send-tool rows |
|---|---|---|---|---|
| 5cbc07b9 | Opus high, auto | claude-opus-5-5, perTurnEffort high | finished, `Done: AC-6 Opus high completed.` | 0 |
| d241e97a | Opus low (control) | claude-opus-5-5, perTurnEffort low | finished, `Done: AC-6 Opus low completed.` | 0 |
| b5491f32 | Sol xhigh, auto-review | gpt-6.1-sol, effort xhigh | finished, `Done: AC-6 Sol xhigh completed.` | 0 |
| 4199a1c9 | Astra xhigh, auto-review | gpt-6-astra, effort xhigh | finished, `Done: AC-6 Astra xhigh completed.` | 0 |

Sources: runtime.json (transcript path, models and efforts read from each), the *.log files, and FO's transcript for the inbound notifications.

Limits: FO extracted these, so judge them as FO's record. The Claude transcripts also mention claude-fable-5-1, not requested; the run does not explain it. The children's `ps` output was not retained in the logs, so process arguments are missing and the transcript fields stand in for them. The fixture roster is not this repository's roster. The two stack conditions, #763's merge commit in the base and an empty origin/main workflow diff, cannot hold until the parents merge.

Correction from the chief-engineer review, 2026-11-02: claude-fable-5-1 in the Claude transcripts is only the advisor tool attachment. Process arguments survive in transcript 3ca59078 and were not copied here; they carry a bearer token and must be redacted first. Codex process arguments are absent.
