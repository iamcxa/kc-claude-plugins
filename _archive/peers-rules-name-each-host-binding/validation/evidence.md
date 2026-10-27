# Independent validation evidence

Candidate: `bff1d8147b626ae91c6ca431f7dde459a63f254d`, pull request #730. Base: `c70f1b22cb1e4a66fd15c617647c778d54c59ec9`.
Validator used the detached checkout `/tmp/peers-validation-730`; the implementation branch was not edited.
Verdict: **PASSED within the accepted prose/manual-replay boundary**, with one Polish finding requiring FO disposition before a delivery recommendation.
The acceptance criteria expressly leave real delivery unverified; this verdict does not extend that boundary.

## Criterion results and falsifiers

| Criterion | Independent observation | Counterexample exercised | Boundary |
| --- | --- | --- | --- |
| AC-1 (transport selection) | Reviewed all native Claude, Claude/Codex in Paseo, bare Codex, unavailable skill/tool and ambiguous transport rows against the exact candidate. Incoming replies do not load unlisted paseo; native questions keep the probe/opening. | Re-ran vendor-route, unlisted-read, no-probe and no-opening bad traces; all rejected. | Manual policy decisions audited, not a shipped policy executor. |
| AC-2 (bounded exchange) | Fake events at 0/299/300/301: busy new asks send zero; idle 299 can send; 300/301 cannot. No work and a still-busy recheck stop waiting. Replies explicitly steer with no completion callback; own workers remain outside the peer rule. CLI help and current tool schema agree with the arguments and interruption fallback. | Missing behavior, interrupt, busy new send, polling, reset deadline, expired send, blocked worker, receipt-as-answer and duplicate send rejected. | Fake event outputs and policy reading; no real messages or prevention of host fallback proved. |
| AC-3 (collaboration and records) | Every 8 round-1 and 8 round-2 row was reviewed; taskless package notices are explicitly recorded. Open briefings stay fixed, matched backlog is reused, inaccessible originals remain unverified. Real Spacedock status and pr_watch on disposable state discover only some-task, not the task-shaped hidden note. | Duplicate task, lost record, bound-briefing edit and relayed-authority bad traces rejected. | Discovery is real local execution; future agent compliance and authenticity of user words are not authenticated. |
| AC-7 (optional activation) | Package default remains [learn, peers]; helper accepts peers alone and peers+paseo; malformed dependency rejected. Real three-way merges retain default/custom/opt-in lists byte-for-byte. Adoption text conditionally offers paseo and refuses paseo without peers. | Changing paseo's README tier to required is rejected; removing dependency logic fails its direct-helper test; unlisted-read trace rejected. | Selection/refusal at installation is prose followed by FO; no adopting-README CLI enforcement exists. |
| AC-6 (reading cost and integration) | Full upstream skill included: peers 805 + paseo 290 + upstream 1380 = proactive 2475; inbound/gate reply 2185. Unaffected moments remain 5631/1045/1318/3276/742; native/unsupported/task-opening 805, warm exchange 0, withdrawn source repair 0. Independent regex/line-section count agrees. | Independent sum check rejects omitted upstream and omitted inbound route; missing optional document mutation fails its test. | These are word counts, not measured attention or performance. |

The reused `replay.py` produced 37 manually selected traces and rejected 17 bad-event mutations. It never reads the policy files: those failures establish the scratch auditor's checks, not automated enforcement of the candidate prose. I separately read the policy against the scenarios and the implementation's base/initial/final reader transcripts. Those three model runs were inspected, not rerun; no new model or real peer exchange was launched. The initial taskless-notice omission is repaired by the pinned head's explicit sentence.

## RoboRev finding and consumer trace

The PR body reports `roborev:1229`; its High finding concerns rejection of a listed optional extension.
FO's reading is correct: `extension_tier_errors` reads `root / "references/sd/workflow.md"`, where root defaults to the package tree.
`--root` accepts another package-shaped tree, not an adopted workflow README. CI calls the default package lint. The optional-tier rejection predates this change.

`selection-probe.txt` proves adopter lists [learn, peers], [learn, peers, paseo], and [learn, paseo] all leave the dependency call's actual input [learn, peers].
The new helper has a caller in package lint and direct tests, but its **paseo-specific rule has no adopting-workflow consumer**.
On a deliberately malformed package template [learn, paseo], it adds a third error; deleting that new check still leaves both old tier errors and refusal.
The direct helper test's failure on base is an absent-helper error, not evidence that an adopter lost dependency protection.

- F1 Polish: the paseo dependency check adds no new refusal on the shipped/default path and cannot validate an adopter's choice. Released user/normal workflow: a maintainer runs package lint; adopter activation is FO-led. Observable harm: none reproduced; only redundant implementation/test surface and an extra diagnostic on an already-invalid package template. Affected boundary: none; AC-7 remains a prose installation rule. Trigger evidence: three adopter lists produce identical template input; removing the check preserves invalid-template refusal. Recommend removing the unused dependency automation or retaining it explicitly as package-template diagnostics, without claiming adopter enforcement. FO owns disposition; no product repair was made.

Sufficiency: accepted host-policy and local integration evidence is present at the explicitly limited boundary.
Necessity: peers rules, optional extension, README/adoption guidance, ADR and document-presence guard map to accepted outcomes or a falsifier. The dependency helper's incremental necessity is not established; F1 must be explicitly dispositioned before FO recommends delivery.

## Executed checks

- 46 lint, 182 design-surface, 113 watcher and 6 POC README tests passed (347 total).
- Real Spacedock dispatch fixtures passed with installed CLI 0.27.2 and supplied plugin 0.27.3; host execution, gate actions and remote delivery remain outside that fixture.
- ADR lint: 37 records, 0 legacy, exit 0, including --require 0038.
- Number guards: PASS; no migration path/task, so migration guard skipped; exit 0.
- Comment measurement: 25 added code lines, 0 comment lines, 0.0%, maximum 5% met; exit 0.
- Dispatch records: 4 complete; design surfaces presentable, scope check deliberately not run outside ideation.
- doc_impact matched all four implementation dispositions: package README updated; ADR 0020 unaffected because budget unchanged; maintain-flow unaffected because replay/lint rules unchanged; learning.md unaffected because full-bundle measurement practice unchanged.
- No CI workflow bytes changed. Cost per PR not measured. Hosted CI 5/5 passing is FO-supplied evidence dated 2026-10-27, not independently rerun here.
- GitHub API read succeeded and identified the requested open pull request and exact head. No PR write, review request, code push or merge was performed.

`commands.json` records the actual check commands; raw results are adjacent. Scratch probes use the named detached checkout and output directory; recreating that checkout from the pinned head is required to rerun them.

## Acceptance script and observed output

Run exactly:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/peers-rules-name-each-host-binding/validation/acceptance.sh
```

The five numbered steps, exact commands and expected output are in `acceptance.sh`; complete observed output is `acceptance-output.txt`.
Executed unchanged in fresh Bash: exit 0. It created and removed its own detached checkout.
Step 1 printed the pinned head; step 2 printed lint PASS and 46 tests OK; step 3 printed 37 ADR file(s) checked, 0 legacy;
step 4 accepted [peers] and [peers, paseo], and printed the expected refusal for [paseo];
step 5 printed peers 805, paseo 290, upstream 1380, proactive 2475 and inbound 2185, with no candidate diff.
The first sandbox attempt could not create Git administrative metadata outside the writable root; the authorized elevated rerun succeeded.
No user-visible screen changed. The script does not prove real peer delivery, automated adoption enforcement or human authority.

## Limits disposition

The implementation's no-live-send, scratch-auditor, fresh-reader, source-check/backfill omission and host-interruption caveats are accurate and consistent with amendment 1.
Its RoboRev-daemon failure is superseded by FO's later recorded review, not treated as a clean review.
Draft PR creation is now verified by a successful API read; hosted CI remains FO evidence.
Current installed Spacedock startup/idle passages count 133/507 rather than the design's stale 365/100: the same current bytes were charged to both arms, so no candidate-only increase is hidden.
No claim is made about a released upgrade, installed adoption, real cross-host messaging, authenticated Captain words, merge permission or merge completion.
