# Independent validation of PR #773

Verdict: **REJECTED** at `4f08f008f9b117876ffe4b569210278e240d203d`, against fetched `origin/main` `713d4e6ed6381e65fa6d8305e08b282ceb56a8fb`. The declared Pilot profile and non-UI surface are unchanged. Product bytes were not repaired. The task remains at validation for FO disposition.

## Primary evidence and scope

The assigned branch and worktree were verified clean at the candidate. Validation ran in a disposable detached worktree below that assigned checkout; identity and source hashes are in manifest.json. GitHub's live PR response confirms the same head, open Draft status and five successful checks (pr.json). The exact-head RoboRev stored job 1438 has the correct base..head and clean verdict (roborev-1438.json); this is a primary stored result read independently, not a new reviewer invocation. No review was requested, no PR was commented on, and no ready/merge or code-push operation was performed.

RoboRev's read CLI could not connect inside the sandbox and attempted an unavailable daemon-log open. No daemon was started. The three existing reviews were instead read through SQLite's read-only mode; their primary job identities and outputs are retained. This does not replace the independent behavioral checks.

## Acceptance criteria and counterexamples

- **AC-1 passed.** The existing step test rejects a missing observation and an unjustified unrun step, naming step 1. Mutation 1 removes S2 and fails that test.
- **AC-2 passed.** The QNow replay places the script only under the archive, points at a card with a :13 suffix, and independently holds a copied missing path and an omitted fenced command. Restoring the script makes it pass. Mutations 2 and 3 remove the respective checks and fail the test.
- **AC-3 passed.** A fenced command plus an unrecorded link is held, and recording the link passes. Mutation 4 removes link coverage and fails.
- **AC-4 passed.** Missing and one-word Captain reasons are held; a dash plus his WorkOS account passes. Mutation 5 removes the reason check and fails.
- **AC-5 passed.** Both legacy and separate-summary routes hold a missing record with one problem and one next line; a later candidate is rejected and the dispatched candidate passes. Mutations 6 and 7 remove the clause and head checks and fail.
- **AC-6 failed as a value criterion.** Its literal three-step fixture passes, and three actually executed harmless shell commands pass the real CLI with exactly three steps and one Captain-only field; mutation 8 corrupts the count and fails. But captured `GET /health 200` shown in its exact Observed fence is rejected as a missing local file. Both question input sources reproduce the false hold. This is F1, not a claim that the fixture failed. The Captain-only password field in the positive probe is a parser fixture; no browser, password or account was used.
- **AC-7 passed.** Repository lint reports 5836 of 5836 words; the +55 ledger entry and ADR 0054 quote match the actual ideation gate. Restoring the old observer chat-only phrase yields the specified lint defect (observer-mutation.json).
- **AC-8 passed.** The exact requested discovery command, with bytecode disabled, passes 889 tests with 6 existing skips (full-suite.log, exit 0). Removing the Captain record from a legacy QuestionTests fixture fails the existing positive test (ac8-falsifier.log). Extension tests and pinned Linux Spacedock were not rerun locally; the current successful hosted job covers that CI route.
- **AC-9 passed with the stated arithmetic correction.** An independently written recount confirms workflow 5781 to 5836, startup with the unchanged 48-word mod 5829 to 5884, validation passage 64 to 33, new section 86. Idle/open/merged/archive inputs and merge ask remain unchanged, checked by file bytes plus check/write_record AST and ASK literal. The mandated success line contains 9 whitespace-split words, not the table's 8; implementation explicitly disclosed the correction. Adding one word fails the exact-budget lint.

All 24 existing isolated mutations were rerun from candidate source, plus the observer restoration and separate AC-8 legacy-caller falsifier. The original implementation recount was rerun and agrees with the independent one. Commands, logs and exit codes are retained; no green suite was used as proof that F1 is absent.

## Findings and review dispositions

### F1 — Material, P2; reject the proposed Codex decline

Released user and normal workflow: FO shows an exercised step beside its actual observation, preparing a normal validation question.
Observable harm: the legitimate route string is treated as a local file, so steps and question exit 1 even though the requested step has no missing file.
Affected boundary: `value-ac[AC-6]`: a step FO ran itself, shown with its output, passes; `contract[kc-dev-flow-2/references/sd/workflow.md#captain-steps]`: show each step beside its observation.
Trigger: Codex comment 4455190837, read live at the assigned head; probes/observed-route.log, probes/gate-question.log and probes/gate-report.log. Controls pass with the same output moved into a named card or omitted.
This is not P1 in substance: it fails closed, loses no data and has a presentation workaround. It is still Material because an observed, ordinary supported workflow violates the value criterion. ADR 0004 blocks Material findings in every round, including external round 3. The workaround does not justify calling the direct required presentation correct.

### F2 — Needs decision: RoboRev 1419 finding 1

The unrecorded prose instruction still passes (probes/prose.log); an untried instruction may reach the Captain. However, Design / PRFAQ explicitly excludes this trigger unless FO records it, so it does not establish Material harm to the accepted detector. No P1 in substance within this accepted scope; recommend accepting the disclosed limit, not adding an unapproved exhaustive message format.
The primary review says High. ADR 0004 maps the highest reviewer severity to P1, independently of validator agreement. Therefore FO must obtain and record a Captain waiver; this validation neither grants nor assumes it.

### F3 — Needs decision: RoboRev 1423

The same reproduction, harm and excluded boundary apply. Its primary stored review also says High. Recommend the same scoped decline, with a separate explicit Captain waiver under ADR 0004. The chief-engineer's prose-limit recommendation supports scope interpretation but is not that waiver.

### F4 — Needs decision: required installed checker drift

The exact dispatched .claude package's dispatch_records.py exits 1 on all four task records, requiring main as completion recipient. Its hash differs from both candidate and .codex copies, which agree. This is an installed-checker mismatch, not four demonstrated broken Paseo handoffs. FO owns package reconciliation; no installed file was changed and the mandated result was not silently replaced.

### F5 — Needs decision: shortened repair-message completion record

The candidate checker still exits 1 on implementation-1-message-1.md: its completion sentence omits the canonical suffix beginning “End your turn with the Done line below”. The other three records pass that grammar. The actual implementation report exists, so no missing handoff was demonstrated. Under the validation principles an incomplete dispatch record must be returned to FO; validation does not edit another role's record or rewrite the event.

## Implementation limits independently judged

The prose, inline-code, quote-fence, list-marker-fence and four-space-indented-code omissions reproduce at this head. They are retained parser limits, not fixed behavior; prose is explicitly excluded and the other shapes were disclosed and routed in the engineering-reviewer's advice. A normal fence, a longer closer and an unclosed fence now hold; unrecorded Mermaid/evidence fences hold too. Their loud holds are the disclosed tradeoff, and no allowlist was reintroduced.

The checker validates form and coverage, not truth, real execution or chat interception. Synthetic preview URLs and card fixtures are parser evidence, not proof of a visit. A justified unrun credential step remains accepted. Skipping both record and check can still bypass chat enforcement. Observer record availability is established by the retained rule and lint; no new real adopter/archive run was claimed. The output-fence exception works for the recorded numbers and links tested, but its path-check mismatch is F1.

The change is sufficient for the two bounded historical replay shapes, not for every legitimate output. Its retained files map to the approved detector, required record, word-budget ruling, observer alignment and caller fixtures; removing the corresponding checks fails the named counterexamples. The two additional fixture files were FO-authorized and preserve the intentional missing-record hold. There is no evidence of needless additional product scope.

## Required checks and retained documents

checks.json records the exact commands and exits. ADR lint ran from the detached candidate with the required installed script, `docs/adr --since 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb --require 0054`: exit 0, 51 records and 0 legacy. Number guards, design surfaces, diff check and repository lint exit 0. Comment ratio is 1/493 added code lines (0.2%), below 5%; the added explanatory usage/limits text was read, with no extra comment finding.

doc_impact.py returns the same eight documents listed in implementation's doc-dispositions.json. Each disposition was checked against the actual changed responsibility: ADRs 0020/0037/0044/0049/0051 retain their cited budget, worker, summary, model and merge rules; package README entry/adoption stays valid; maintain-flow commands and learning's independent recount practice stay valid. The workflow, observer and new ADR carry the changed behavior. Consumer impact remains explicit: in-flight validation questions now need the Captain steps record. CI cost per PR was not measured; no CI trigger was changed.

## Five-step acceptance

Run `/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/fo-tries-what-it-asks-the-captain/validation-1/acceptance.sh`. The script is self-contained, declares the assigned candidate checkout and required installed ADR tool, and contains five exact steps with expected output. Its unchanged bytes were run in a fresh bash shell with CAPTAIN_STEPS_WORKTREE pointing to the detached exact-head checkout. Observed output is acceptance.log: steps 1–4 pass, step 5 expects a valid record to pass but exits 1 with `message S4: missing path /health`. This is an acceptance failure, not a green demonstration.

It takes under five minutes, has no browser UI, uses only synthetic route-style text emitted by a harmless shell command, and reads/writes only temporary fixture files. It does not prove actual preview availability, sign-in, observations' truth, host compliance, installation, adoption, release or merger.

## Ownership and next action

FO owns disposition and the repair route for F1, the two reviewer-High waivers, installed-checker alignment and the shortened dispatch record. No repair, review request, scope amendment or delivery approval was made by validation. The detached worktree is removed after evidence capture; the assigned branch stays at the reviewed head. State report and evidence are committed through the exact task-scoped Spacedock command requested by dispatch.
