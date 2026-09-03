# plan-flow station 0 — pain inventory (kc-claude-plugins, read 2026-09-03)

Sources read: ship-defects S1..S18 (DEV-62/67/84/89 evidence), the `strongest_limit` and change lists of the four archived POCs (DEV-62, 67, 78, 79), the four most recent SD debriefs (2026-08-20, 08-22 x2, 09-03), and the `## The problem` section of every open DEV Issue. Each pain is one row; `hits` counts distinct occurrences in those sources; `felt by` is who paid; `class` is what kind of gate would have caught it. Items with hits >= 2 are the Ask UI option pool for the next station 2.

| # | pain (one line) | hits | felt by | class | first / latest source |
|---|---|---|---|---|---|
| P1 | A candidate passes surface checks but carries files or comments that map to no acceptance criterion | 5 | Captain at UAT, FO at review | minimal-necessity gate | DEV-66 r0 parser; DEV-48; DEV-52; Captain Q1; DEV-78 motivation |
| P2 | The FO or Captain re-asks the same three questions on every PR (smallest stack? without-it run? what verified?) | 4 | Captain, FO | evidence contract | Captain Q2; DEV-62 limit (3); DEV-67 #10; DEV-84 raw requirement |
| P3 | Worker self-verification is the minimum (all three DEV-67 workers reported only `contract-test.py`), so review finds P1s the checks cannot | 3 | FO, Codex rounds | dev-flow exit check | S5; DEV-67 #11; DEV-78 |
| P4 | A fix on a lower layer after the upper layer was dispatched breaks the stack base | 2 | next-layer worker, Captain at merge | dispatch ordering | S10; DEV-67 #1/#9 (rebase round) |
| P5 | Worker transcript reads are unreliable (64 KB truncation, `--after` 404, evidence block located by fence or heading) | 6 | FO | read path | S2, S8, S9, S13, S15; DEV-64 |
| P6 | A task sent before the workspace is ready is silently dropped; no delivery acknowledgment | 2 | FO (10-min stalls) | dispatch ack | S1; DEV-84 token ack |
| P7 | Cloud workers share one usage pool; a limit on one idles every new worker with the same banner | 2 | FO, Captain (day lost) | quota detection | S17, S18 |
| P8 | Verification steps bundled in one call exceed tool timeouts and lose partial results | 2 | FO | step isolation | S4; DEV-84 acceptance |
| P9 | A without-it "sandbox" that only unsets variables is not a sandbox; a script path in an untracked file is not evidence | 3 | FO, Codex | isolation contract | S3; DEV-62 limit (3); Codex r3 P0-8 |
| P10 | Holder handover cannot revoke an in-flight create; at most one worker, never exactly-once | 2 | FO on wake, Captain (orphan cost) | intent/reconcile | DEV-79 limit; Codex r4 |
| P11 | Review findings outside the Brief either loop forever or get scoped out blindly (security among them) | 2 | FO, Captain | finding disposition | S6; Codex r3 S6 reversal; Captain Q1 (security unmeasured) |
| P12 | Contract-test phrase pins turn green when a rule is dropped but its words survive elsewhere | 2 | maintainer | behaviour assertion | DEV-51; DEV-73 |
| P13 | An existing handoff (kc-pr-review <- kc-dev-flow) exists and never fires | 1 | Captain | wiring proof | DEV-60 |
| P14 | Linear body parsing drifts from the README template (heading name, hard-wrapped bullets, truncated branchName) | 3 | FO at admission, worker at push | admission guard | DEV-50; DEV-59; S11 |
| P15 | A POC "proof" that lives only in an unpushed or throwaway location is rejected at validation | 1 | FO (a full cycle repeated) | durable evidence | 2026-09-03 debrief |
| P16 | Proportionality failure: 6 gate attempts and 9 stage reports for a 25-line reader | 1 | Captain | ceremony budget | 2026-08-22-02 debrief |
| P17 | A vendored mod prescribes a procedure the current binary refuses (pr-merge 15 versions behind; `local-merge:` sentinel grammar) | 2 | FO at terminalization | vendored-copy drift | 2026-08-20 debrief; DEV-79 close |
| P18 | The FO nudges a worker with remote state the FO did not read from the worker's source | 1 | worker (correctly refused) | FO message discipline | S14 |
| P19 | Forge Phase 2 baseline inherits the operator's global CLAUDE.md, memory, hooks | 1 | maintainer | clean environment | DEV-80 |
| P20 | Fixture files outlive their reason (10 files for 6 assertions) | 1 | maintainer | without-it on fixtures | DEV-83 |

## Observations for station 2 option mining

- The top cluster (P1, P2, P3, P9, P11) is one theme: verification that a person still has to redo. It matches every option the Captain selected in DEV-89 Q3 and is the demand behind the three ship-flow sentences. Any future Ask UI for a ship-flow item should offer P1, P2, P3 as options before anything else.
- P5, P6, P7, P8 are FO-runtime pains; they never reach the Captain directly and should not appear as user-value options, only as ship-flow contract items.
- 22 of 41 open DEV Issues have no Development Brief shape (all Qnow Issues, DEV-3/4/5/6, DEV-15/81/82). Station 0 for a Qnow item has no pain evidence to mine from Issues; it must come from the Captain or from a market-signal pass.
- Only P1 and P14 have a mechanical gate merged today (DEV-78, DEV-50/59). Every other row is still enforced by a person.
