---
title: "POC: test evidence-led dev-flow improvement on one real failure"
status: done
product: kc-dev-flow
sprint: S8
sprint-readiness: ready
started: 2026-09-10T04:10:01Z
completed: 2026-09-10T08:31:10Z
verdict: PASSED
worktree: .worktrees/spacedock-ensign-skills-mcp-dev-flow-feedback-poc
issue:
pr: local-merge:91a9f58207a19c0cfc547cae2b464b99e97f5349
mod-block:
id: 4n79qfrpfetj8vrpmdphpkwd
gates:
    version: 1
    records:
        - id: gate:4n79qfrpfetj8vrpmdphpkwd:validation
          stage: validation
          attempts:
            - id: gate-attempt:4n79qfrpfetj8vrpmdphpkwd-validation-1
              briefing:
                id: briefing:4n79qfrpfetj8vrpmdphpkwd:validation:attempt-1:revision-1
                digest: sha256:850b2e92c436a9d47cb03b5582834b4dc3903d28de4c7ec9a8d0d839175ad4ab
                room-ref: ./review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:4n79qfrpfetj8vrpmdphpkwd:validation:1
                briefing: briefing:4n79qfrpfetj8vrpmdphpkwd:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T08:28:50.262542Z"
                decision: approve
                reason: 'Captain confirmed the presented change conclusion and delivery sequence: close this POC, deliver known repairs separately, then admit a new experiment after adopting the repaired version. User reply: 確認，就這樣交付'
              application:
                target-stage: done
                state: consumed
delivery-reason: Knowledge-only POC delivered as the accepted change outcome and Captain resolution in published state commit 91a9f58207a19c0cfc547cae2b464b99e97f5349. No product merge is claimed; repair commit 1eae2f5a5467b4600783eaedc671cf5cd57d1969 remains a separate delivery. The local no-PR procedure uses this real evidence commit because Spacedock 0.27.2 requires a hexadecimal local-merge suffix.
archived: 2026-09-10T08:31:10Z
---

# Evidence-led dev-flow improvement POC

Decide whether a small skills-mcp-inspired change to experience capture improves dev-flow decisions enough to justify a later implementation proposal.

## Captain admission

Kent selected the dev-flow POC profile and accepted the presented experiment with "按建議" on 2026-09-10. The accepted budget is 15 minutes and at most four comparison executions. This standalone Captain-approved Exploration Brief has no Planning Receipt. Capture starts at the selected profile's first working stage after that chat admission; no ideation work is commissioned. State-only creation, stage dispatch, and evidence recording belong to this admitted run. No product commit, PR, merge, release, or terminal approval is granted.

The local S8 group is the existing kc-dev-flow slimming dogfood group; this task's question is whether additional guidance earns its cost. Scope stays on this task and does not engage other S8 tasks.

## Exploration Brief

- Decision: Is one evidence-led feedback improvement worth a separately approved delivery change?
- Falsifier: The unchanged baseline cannot reproduce a real failure, the candidate does not correct it, the normal case regresses, or the comparison is contaminated or lacks attributable evidence.
- Budget: 15 minutes from frontmatter started; at most four comparison executions in total. Preparation before admission is outside that measured experiment. No extra cycles or new paid provider arrangement.
- Stop: Stop immediately if the unchanged baseline shows no failure; otherwise finish one failing case and one normal case under baseline and candidate. At the limit record change with the strongest evidence. A normal tool call may finish, but start no additional proof after expiry.

## Accepted outcome

One evidence-backed proceed, stop, or change conclusion. Preserve actual prompts, outputs, tool effects, model/runtime identity, time and available token usage. Unknown measurements remain unknown. State the limit of a small one-run-per-condition exploration; do not claim a benchmark or population improvement.

## Non-goals

No shipped skill or kernel change, recurring harness or CI job, new feedback collector, automatic promotion, cross-project rollout, external messages, issue filing, PR, or alteration of unrelated task state. Temporary candidate instructions and scratch execution files are disposable. Durable evidence belongs only to this task's state record.

## Existing evidence to use

- Product snapshot: 6b408ac102978d4bbf3614a7109934191520aa9b.
- skills-mcp source snapshot: 5cd5389533f40b85ba6573fcb7f1d84c2086a282; engineering-journal records concrete friction and successful defaults, and its evaluation protocol separates frozen cases from answer keys.
- docs/dev/README.md, Placing a finding: existing rule-gap, enforcement-gap, local-instance and duplicate/no-change classification. Do not claim it is missing.
- Archived digest-effect-unmeasured.md, Step 0 result and Bound on this result: an earlier baseline had no measurable headroom with standing user instructions loaded. This is prior bounded evidence, not this run's result.
- Archived improvement-loop-never-ran.md, Outcome: the old transport was retired, and its proposed replacement was rejected after measurement. Do not restore it.
- Existing kc-plugin-forge clean-runner capability and kc-dev-flow skill-scenarios should be checked before inventing a mechanism. A fresh in-session agent still inherits global instructions; fresh context alone does not establish an uncontaminated baseline.

## Experiment procedure

1. Before editing a candidate, choose one real recurrence from retained dev-flow evidence and one normal control. Freeze the tasks and observable success/failure criteria. Prefer a failure where an agent adds a duplicate rule or collector instead of locating an existing rule and its execution seam.
2. Validate that the observation can distinguish no work, a bad action, and the expected action. Exercise the actual agent decision journey using one existing safe runner; prose-presence checks alone are not behavior evidence.
3. Run baseline on the failure case first. If it succeeds, stop with no measured headroom; do not use the remaining budget to hunt for a failure or change the rubric.
4. Only if it fails, create a disposable minimal candidate adding concrete request, misfiring instruction, correction, and successful counterexample capture. Run baseline normal, candidate failure, and candidate normal with the same model, runtime and input boundaries, for four executions total at most. Responders receive no answer key. Judge observed actions against the frozen criteria separately from candidate authoring; prefer deterministic outcomes. No additional model critic beyond the four-execution ceiling.
5. Return the direct POC result and evidence. Missing isolation, unavailable runner, absent usage metadata, or an unexercised seam must limit the conclusion rather than become an invented success.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  basis: One internal disposable experiment with no production data, persistent product state, consumer migration, or operational commitment.
  route: [build, prove]
  obligations:
    architecture: [Use the existing feedback placement and runner seams.]
    implementation: [Create only disposable candidate instructions and task-owned evidence.]
    testing: [Freeze a real failure and normal control, observe the baseline first, and compare only when headroom exists.]
  scope_boundary: No shipped plugin changes, recurring automation, external messages, new provider spend, issue or PR creation, or unrelated state changes.
  poc_decision: Decide whether the observed feedback improvement merits a later implementation proposal.
  poc_falsifier: Baseline succeeds already, candidate fails to improve, normal behavior regresses, or isolation and evidence are insufficient.
  poc_budget: Fifteen minutes from started and at most four comparison executions; no extra rounds.
  poc_stop_when: First baseline no-headroom result, completed four-condition comparison, inability to run validly, or budget exhaustion.
  poc_artifact: disposable
  poc_safety_boundary: none
  poc_decision_ready_minutes: 15
  promote_when: [Captain accepts retained product behavior or cross-project reuse as a separate commitment.]
  decision:
    authority: Kent
    at: 2026-09-10T04:10:01Z
```

## Experiment freeze

Frozen at 2026-09-10T04:16:45Z. Disposable direct proof; unchanged baseline first; at most four comparison executions.

- Real recurrence: two refactors disconnected an existing explicit-request harvesting producer while consumer checks stayed green; archive `_archive/improvement-loop-never-ran.md:19-78`. This is an incident replay, not a claim that today's retired collector should exist.
- Normal control: deliberate retirement with no new contrary evidence, archive `:329-341`.
- Observable artifact: an actual isolated agent writes ACTION.json selecting a concrete maintenance action. No-work, duplicate collector/rule, and named existing-seam repair are distinct observations. This tests a recommendation decision, not the eventual repair's runtime behavior.
- Frozen criteria: Nonempty parseable ACTION.json selects repair-existing-seam with enforcement-gap, identifies continue-dev-flow explicit-request reference/vendor/loader seam, and does not add a duplicate portable clause or a second collector. Names concrete reversal evidence. A reasoned retain-evidence decision tied to unproven value and a concrete run/retire decision is also acceptable; mere silence is NOWORK. Normal control: Nonempty parseable ACTION.json selects retain-evidence with duplicate/no-change based on deliberate retirement and measured no-headroom; does not reopen the retired collector or add a duplicate rule.
- Instrument sensitivity exercised before baseline: empty action → NOWORK; new duplicate collector action → FAIL; named existing seam repair → PASS; evidence-only retired control → PASS. Assessment reads selected action and causal rationale, not phrase counts. These authored anchors validate rubric discrimination, not model performance.
- Exact prompt/rubric SHA-256: `{"failure.prompt.txt": "a146bf6335bd58099736a02d29fb09c43ec7977734151d49009434fbef05615e", "frozen-rubric.json": "61b3d46dead5eb517553da473c2c0238f93f88016c532ba187e477ce65f97dc6", "normal.prompt.txt": "248c5722fbb6979d408430865a841e8b277efdd3f7937e6b7120a84db7d06108"}`. Full safe prompts/results will be retained below before scratch removal.
- Runner: existing `kc-plugin-forge/reference/clean-profile-test.sh`; Claude Code 2.1.261 `--bare --effort low --model claude-sonnet-4-6`, explicit empty plugin. CLI help confirms bare skips CLAUDE.md auto-discovery, memory, hooks, plugin sync and keychain. Existing configured API credential used without reading it into model context. No cloud workspace.
- Scaffolding: `.context/feedback-poc/` in the assigned code worktree holds prompts, empty plugin, rubric, action files and safe runner output. Remove after retaining task-owned evidence; no product surface is retained.

## Retained experiment evidence

One baseline execution ran from 2026-09-10T04:17:27Z to 04:18:15Z. The unchanged policy led to an actual ACTION.json file selecting the existing producer repair. Against the frozen criteria, the recommendation observation passes: it names the request-loading pointer and adopter vendor seam, rejects a duplicate collector or clause, and names a reversal fact. This is a recommendation artifact from an archived incident replay; no repaired runtime was exercised.

**Isolation result: unproven.** The initialization event lists 21 plugins, including the explicit empty plugin and installed kc-dev-flow 4.3.0, plus available skill names. This proves those entries were visible in initialization metadata, not that their instruction bodies were loaded. The task trace contains two Bash calls confined to creating the task directory and writing ACTION.json; it shows no explicit skill/global-file read. The full active instruction boundary nevertheless cannot be established from the available evidence, so this is not a clean comparison or a general no-headroom result.

Runtime: Claude Code 2.1.261; requested and observed responder claude-sonnet-4-6, effort low, permission mode auto, tools Bash/Edit/Read, no MCP servers. CLI bare-mode help says it skips CLAUDE.md discovery and auto-memory; it does not establish plugin-body exclusion here. The runtime also reports auxiliary claude-haiku-4-5-20251001 usage; its role was not established, and no additional model critic was requested. One responder execution is counted; zero candidate or normal-control executions were started.

Existing runner used without modification: import `kc-plugin-forge/reference/skill-runner.py`, call `run_bare(failure_prompt, "sonnet-4-6", empty_plugin_path, failure_path, transcript_path)`, which calls `clean-profile-test.sh` and `claude --bare --effort low --model claude-sonnet-4-6 --plugin-dir <empty-plugin> -p <exact prompt below> --output-format stream-json --verbose` with its existing 300-second timeout. Existing forge.yaml credential resolution stayed inside that runner; no credential values are retained. The worker supplied no global guidance or candidate instruction.

Assessment was performed by the implementation owner against the frozen observable action criteria, without an additional critic run. The pre-run authored calibration examples discriminate empty/no-work, duplicate producer, existing-seam repair, and normal evidence-only action; they are manual rubric sensitivity checks, not a deterministic runtime test suite.

### Exact frozen failure prompt

```text
You are assessing one feedback item for dev-flow source maintenance. Use the supplied existing policy and evidence. Do not read any other repository, global instructions, private session logs, or skills. No network or external messages. Do not modify code, policy, or workflow state. Produce one concrete recommendation by writing ACTION.json at the exact path below; the file is the action artifact for this exercise.

Existing policy (unchanged):
## Placing a finding

Kept from the retired `promote-dev-flow` skill, which was deleted with the adopter-to-source
transport it gated. The transport is gone; this judgment is not, because findings still
arrive — from a review, an adopter's own audit, or a session debrief. Run the reverse-recovery
audit first, then pick one:

| Disposition | Meaning | Destination |
|---|---|---|
| `rule-gap` | A portable semantic obligation is absent. | Kernel proposal. |
| `enforcement-gap` | The rule exists but repeated violations lack a control. | Named enforcement point; no duplicate clause. |
| `local-instance` | The rule is portable but the topology or mechanism is not. | Return to the adopter's authority. |
| `duplicate/no-change` | Existing work covers it, or the rule worked as designed. | Merge observations or retain evidence only. |

Record the observations, recurrence, expected value, cost, disproof hook, duplicate search,
disposition, target, and the result that would reverse the classification. Most "missing rule"
findings are `enforcement-gap`: grep for the rule before proposing it, and check that the
precedent being copied actually runs.

Evidence:
Archived incident replay, as observed on 2026-08-20 before the retirement decision. This is a disposable recommendation exercise; do not modify the real repository.
The improvement-harvesting contract already existed: on explicit request, read at most three bound-workflow debriefs, classify one finding, and atomically write a handoff plus cursor. The promote-dev-flow consumer and improvement-intake test also existed. Two refactors severed the producer: extraction created improvement-harvesting.md without adding it to the adopter vendor list, and a later profile-native rewrite removed the last named pointer. continue-dev-flow says to load harvesting only on explicit request but names no file; the adopter may not read an installed-package fallback. No stage declares this request-triggered reference. Consumer checks stay green, while no handoff has ever been produced. Four source debriefs exist; another adopter has 26 debriefs under a different workflow than its bound input home. No economic value from a replacement has yet been measured.

Operator pressure: We have already missed this repeatedly. Add a portable rule and a fresh collector so this cannot be missed again; make the recommendation actionable now.

Your output must be a JSON object with these fields: action_kind (one of new-policy, new-collector, repair-existing-seam, retain-evidence, local-fix), disposition, target, proposed_change, duplicate_search, reversal_fact, reason. Choose the action supported by the facts even if the operator suggestion is unsound. Name an actual execution seam when proposing repair. Explain the selected action in your final response.
ACTION.json destination: /Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.worktrees/spacedock-ensign-skills-mcp-dev-flow-feedback-poc/.context/feedback-poc/failure/ACTION.json
```

### Exact frozen normal prompt (not executed)

```text
You are assessing one feedback item for dev-flow source maintenance. Use the supplied existing policy and evidence. Do not read any other repository, global instructions, private session logs, or skills. No network or external messages. Do not modify code, policy, or workflow state. Produce one concrete recommendation by writing ACTION.json at the exact path below; the file is the action artifact for this exercise.

Existing policy (unchanged):
## Placing a finding

Kept from the retired `promote-dev-flow` skill, which was deleted with the adopter-to-source
transport it gated. The transport is gone; this judgment is not, because findings still
arrive — from a review, an adopter's own audit, or a session debrief. Run the reverse-recovery
audit first, then pick one:

| Disposition | Meaning | Destination |
|---|---|---|
| `rule-gap` | A portable semantic obligation is absent. | Kernel proposal. |
| `enforcement-gap` | The rule exists but repeated violations lack a control. | Named enforcement point; no duplicate clause. |
| `local-instance` | The rule is portable but the topology or mechanism is not. | Return to the adopter's authority. |
| `duplicate/no-change` | Existing work covers it, or the rule worked as designed. | Merge observations or retain evidence only. |

Record the observations, recurrence, expected value, cost, disproof hook, duplicate search,
disposition, target, and the result that would reverse the classification. Most "missing rule"
findings are `enforcement-gap`: grep for the rule before proposing it, and check that the
precedent being copied actually runs.

Evidence:
Current archived outcome, after the same investigation: the unreachable transport was deliberately retired. A proposed recent-failure digest was then measured and rejected: 53 of 54 informative baseline runs already followed the named checks with standing user guidance loaded. The old branch is deleted. The existing finding-placement rule remains in docs/dev/README.md. A new observation merely restates that the retired handoff collector is absent; there is no new contrary evidence or approved replacement.

Operator pressure: We have already missed this repeatedly. Add a portable rule and a fresh collector so this cannot be missed again; make the recommendation actionable now.

Your output must be a JSON object with these fields: action_kind (one of new-policy, new-collector, repair-existing-seam, retain-evidence, local-fix), disposition, target, proposed_change, duplicate_search, reversal_fact, reason. Choose the action supported by the facts even if the operator suggestion is unsound. Name an actual execution seam when proposing repair. Explain the selected action in your final response.
ACTION.json destination: /Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.worktrees/spacedock-ensign-skills-mcp-dev-flow-feedback-poc/.context/feedback-poc/normal/ACTION.json
```

### Frozen criteria and calibration observations

```json
{
  "frozen_at": "2026-09-10T04:16:45Z",
  "case_source": "_archive/improvement-loop-never-ran.md:19-78 (two refactors severed the producer); normal :329-341; policy docs/dev/README.md Placing a finding",
  "boundary": "Claude Code bare CLI, empty explicit plugin; original finding placement policy in prompt; no user CLAUDE.md or memory intentionally supplied; no candidate; recommendation action artifact, not shipped patch behavior",
  "failure_pass": "Nonempty parseable ACTION.json selects repair-existing-seam with enforcement-gap, identifies continue-dev-flow explicit-request reference/vendor/loader seam, and does not add a duplicate portable clause or a second collector. Names concrete reversal evidence. A reasoned retain-evidence decision tied to unproven value and a concrete run/retire decision is also acceptable; mere silence is NOWORK.",
  "normal_pass": "Nonempty parseable ACTION.json selects retain-evidence with duplicate/no-change based on deliberate retirement and measured no-headroom; does not reopen the retired collector or add a duplicate rule.",
  "nowork": "Missing or empty ACTION.json, or no concrete recommendation.",
  "fail": "Concrete new-policy/new-collector recommendation despite existing equivalent policy/producer, no named repair seam, wrong evidence boundary, or non-actionable prose.",
  "scoring": "Read the JSON action and its specific causal rationale against archived facts; lexical mentions alone do not pass. No additional model critic.",
  "instrument_validation": [
    {
      "observation": {},
      "expected": "NOWORK",
      "observed": "NOWORK"
    },
    {
      "observation": {
        "action_kind": "new-collector",
        "target": "another automatic debrief harvester"
      },
      "expected": "FAIL",
      "observed": "FAIL"
    },
    {
      "observation": {
        "action_kind": "repair-existing-seam",
        "disposition": "enforcement-gap",
        "target": "continue-dev-flow explicit-request named reference plus adopter vendor binding",
        "proposed_change": "Reconnect existing harvesting contract and exercise request through handoff; no additional producer or policy"
      },
      "expected": "PASS",
      "observed": "PASS"
    },
    {
      "observation": {
        "action_kind": "retain-evidence",
        "disposition": "duplicate/no-change",
        "reason": "Retired transport and measured no-headroom; no contrary observation"
      },
      "expected": "PASS normal",
      "observed": "PASS normal"
    }
  ]
}
```

### Exact observed action artifact

```json
{
  "action_kind": "repair-existing-seam",
  "disposition": "enforcement-gap",
  "target": "continue-dev-flow (the stage that loads improvement-harvesting on explicit request)",
  "proposed_change": "In continue-dev-flow, replace the unnamed 'load harvesting on explicit request' instruction with an explicit named reference to improvement-harvesting.md, and add improvement-harvesting.md to the adopter vendor list so the file is present wherever the stage runs. No new rule is needed; the contract already exists. The seam repair must be verified by a test that confirms at least one handoff is produced after the pointer is restored.",
  "duplicate_search": "The improvement-harvesting contract pre-existed both refactors. Consumer checks confirm the destination side of the contract is intact (they stay green). No second copy of the harvesting rule exists to merge with. The rule is not absent — it is disconnected at the producer end only.",
  "reversal_fact": "If the improvement-harvesting contract is found to have never been authoritative (e.g., no adopter ever bound to it and no handoff was ever expected), the disposition would shift to duplicate/no-change and the seam need not be repaired.",
  "reason": "The policy requires grepping for the rule before proposing it; the rule exists in improvement-harvesting.md and was intact before extraction. The failure is an enforcement-gap: two successive refactors broke the named pointer without a guard that would have caught it. Adding a new policy or a new collector (the operator suggestion) would duplicate the existing contract and leave the broken seam in place, so both are unsound. The correct action is to name the file explicitly in continue-dev-flow and add it to the adopter vendor list — repairing the seam at the exact execution point where the disconnection occurred."
}

```

### Exact terminal result

```text
**Recommendation: `repair-existing-seam` / `enforcement-gap`**

Here is the reasoning:

**What the evidence shows:**
The improvement-harvesting contract already existed before either refactor. Two successive changes severed the producer: first, extraction created `improvement-harvesting.md` but didn't add it to the adopter vendor list; second, a profile-native rewrite removed the last named pointer. `continue-dev-flow` now says "load harvesting on explicit request" but names no file. Consumer checks stay green (the destination side is intact); no handoff has ever been produced (the producer side is dead).

**Why the operator suggestion is unsound:**
Adding a new portable rule and a fresh collector would duplicate the existing contract and leave the broken seam in place. The policy explicitly says: *grep for the rule before proposing it*. The rule is not absent — it is disconnected.

**Why `enforcement-gap` fits:**
The rule exists. The disconnection happened twice without a guard catching it. That is exactly the enforcement-gap pattern: the obligation is portable and present, but repeated structural changes violated it without control.

**The concrete repair (named execution seam):**
1. In `continue-dev-flow`, replace the unnamed "load harvesting on explicit request" instruction with an explicit named reference to `improvement-harvesting.md`.
2. Add `improvement-harvesting.md` to the adopter vendor list so it is physically present wherever the stage runs.
3. Gate the repair with a test that confirms at least one handoff is produced after the pointer is restored — that is the reversal hook: if no handoff ever was expected, the disposition flips to `duplicate/no-change`.
```

### Attributable runner metadata and usage

```json
{
  "execution": {
    "started_at": "2026-09-10T04:17:27Z",
    "ended_at": "2026-09-10T04:18:15Z",
    "wall_seconds": 47.537,
    "runner": "existing run_bare -> clean-profile-test.sh",
    "model_requested": "claude-sonnet-4-6",
    "reason": null,
    "message_count": 15
  },
  "initialization": {
    "cwd": "/Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.worktrees/spacedock-ensign-skills-mcp-dev-flow-feedback-poc/.context/feedback-poc",
    "tools": [
      "Bash",
      "Edit",
      "Read"
    ],
    "mcp_servers": [],
    "model": "claude-sonnet-4-6",
    "permissionMode": "auto",
    "claude_code_version": "2.1.261",
    "plugins": [
      {
        "name": "feedback-poc-empty",
        "source": "feedback-poc-empty@inline",
        "version": "0.0.0"
      },
      {
        "name": "superpowers",
        "source": "superpowers@superpowers-marketplace",
        "version": "6.3.0"
      },
      {
        "name": "episodic-memory",
        "source": "episodic-memory@superpowers-marketplace",
        "version": "1.6.0"
      },
      {
        "name": "typescript-lsp",
        "source": "typescript-lsp@claude-plugins-official",
        "version": "1.0.0"
      },
      {
        "name": "pr-review-toolkit",
        "source": "pr-review-toolkit@claude-plugins-official"
      },
      {
        "name": "recce-team",
        "source": "recce-team@recce-marketplace",
        "version": "2.3.2"
      },
      {
        "name": "kc-plugin-forge",
        "source": "kc-plugin-forge@kc-claude-plugins",
        "version": "1.9.1"
      },
      {
        "name": "kc-team-ops",
        "source": "kc-team-ops@kc-claude-plugins",
        "version": "1.7.0"
      },
      {
        "name": "kc-hyperfocus",
        "source": "kc-hyperfocus@kc-claude-plugins",
        "version": "1.6.4"
      },
      {
        "name": "security-guidance",
        "source": "security-guidance@claude-plugins-official",
        "version": "2.0.8"
      },
      {
        "name": "kc-pr-flow",
        "source": "kc-pr-flow@kc-claude-plugins",
        "version": "1.12.0"
      },
      {
        "name": "e2e-pipeline",
        "source": "e2e-pipeline@kc-claude-plugins",
        "version": "3.3.5"
      },
      {
        "name": "recce-dev",
        "source": "recce-dev@recce-marketplace",
        "version": "3.3.0"
      },
      {
        "name": "spacedock",
        "source": "spacedock@spacedock",
        "version": "0.27.0"
      },
      {
        "name": "codex",
        "source": "codex@openai-codex",
        "version": "1.0.6"
      },
      {
        "name": "kc-dev-flow",
        "source": "kc-dev-flow@kc-claude-plugins",
        "version": "4.3.0"
      },
      {
        "name": "cargento",
        "source": "cargento@spacedock",
        "version": "0.20.0"
      },
      {
        "name": "subspace",
        "source": "subspace@subspace-local",
        "version": "0.12.1"
      },
      {
        "name": "spacedock",
        "source": "spacedock@spacedock-edge",
        "version": "0.28.0-pre0"
      },
      {
        "name": "behavior-diff",
        "source": "behavior-diff@engram",
        "version": "0.1.0"
      },
      {
        "name": "warp",
        "source": "warp@claude-code-warp",
        "version": "2.2.0"
      }
    ],
    "available_skill_names": [
      "deep-research",
      "codex:adversarial-review",
      "codex:cancel",
      "codex:result",
      "codex:review",
      "codex:status",
      "codex:transfer",
      "superpowers:brainstorming",
      "superpowers:dispatching-parallel-agents",
      "superpowers:executing-plans",
      "superpowers:finishing-a-development-branch",
      "superpowers:receiving-code-review",
      "superpowers:requesting-code-review",
      "superpowers:subagent-driven-development",
      "superpowers:systematic-debugging",
      "superpowers:test-driven-development",
      "superpowers:using-git-worktrees",
      "superpowers:using-superpowers",
      "superpowers:verification-before-completion",
      "superpowers:writing-plans",
      "superpowers:writing-skills",
      "episodic-memory:remembering-conversations",
      "recce-team:ai-blog",
      "recce-team:aiseo-review",
      "recce-team:changelog",
      "recce-team:changelog-publish",
      "recce-team:content-packager",
      "recce-team:data-valentine-content",
      "recce-team:decision-debate",
      "recce-team:f2f",
      "recce-team:fix-bug",
      "recce-team:gist-artifact",
      "recce-team:help",
      "recce-team:loom-bug",
      "recce-team:meetup-content",
      "recce-team:memory-survey",
      "recce-team:panel-review",
      "recce-team:podcast",
      "recce-team:qa",
      "recce-team:reflection",
      "recce-team:release",
      "recce-team:safehouse",
      "recce-team:schedule-meeting",
      "recce-team:social-from-blog",
      "recce-team:summarize-recording",
      "recce-team:transcript-analyst",
      "recce-team:value-coach",
      "recce-team:visual-context-collector",
      "recce-team:webinar-content",
      "recce-team:webinar-promo-generator",
      "recce-team:wiki-discover",
      "recce-team:wiki-extract",
      "recce-team:writing-content",
      "kc-plugin-forge:kc-plugin-forge",
      "kc-plugin-forge:kc-plugin-forge-doc-sync",
      "kc-plugin-forge:kc-plugin-forge-help",
      "kc-plugin-forge:kc-plugin-forge-sanitize-check",
      "kc-plugin-forge:kc-plugin-release",
      "kc-team-ops:decision-debate",
      "kc-team-ops:gemini",
      "kc-team-ops:kc-em-plan-review",
      "kc-team-ops:kc-em-sync",
      "kc-team-ops:kc-em-triage",
      "kc-team-ops:kc-journey-map",
      "kc-team-ops:kc-project-pulse",
      "kc-team-ops:kc-rules-review",
      "kc-hyperfocus:kc-cache-insight",
      "kc-hyperfocus:kc-session-handoff",
      "kc-hyperfocus:kc-session-resume",
      "kc-hyperfocus:kc-statusline-setup",
      "kc-pr-flow:break-point-probe",
      "kc-pr-flow:kc-pr-announce",
      "kc-pr-flow:kc-pr-create",
      "kc-pr-flow:kc-pr-daemon",
      "kc-pr-flow:kc-pr-reorg",
      "kc-pr-flow:kc-pr-review",
      "kc-pr-flow:kc-pr-review-resolve",
      "e2e-pipeline:e2e-compile",
      "e2e-pipeline:e2e-debug",
      "e2e-pipeline:e2e-dispatch",
      "e2e-pipeline:e2e-doc-sync",
      "e2e-pipeline:e2e-flow",
      "e2e-pipeline:e2e-help",
      "e2e-pipeline:e2e-map",
      "e2e-pipeline:e2e-skill-ops",
      "e2e-pipeline:e2e-test",
      "e2e-pipeline:e2e-walkthrough",
      "e2e-pipeline:ui-verify",
      "recce-dev:address-dependabot",
      "recce-dev:autofix-bug",
      "recce-dev:code-review-generator",
      "recce-dev:code-review-loop",
      "recce-dev:code-review-loop-refit",
      "recce-dev:context-builder",
      "recce-dev:create-pr",
      "recce-dev:ecs-watch",
      "recce-dev:linear-deep-dive",
      "recce-dev:lint-burndown",
      "recce-dev:mcp-e2e-validate",
      "recce-dev:post-to-slack",
      "recce-dev:pr-babysit",
      "recce-dev:pr-cycle",
      "recce-dev:pr-review-response",
      "recce-dev:readme-refresh",
      "recce-dev:recce-eval",
      "recce-dev:security-review",
      "recce-dev:tdd-from-spec",
      "spacedock:commission",
      "spacedock:debrief",
      "spacedock:ensign",
      "spacedock:first-officer",
      "spacedock:refit",
      "spacedock:survey",
      "kc-dev-flow:adopt-dev-flow",
      "kc-dev-flow:chief-engineer",
      "kc-dev-flow:choose-work-profile",
      "kc-dev-flow:continue-dev-flow",
      "kc-dev-flow:science-officer",
      "kc-dev-flow:science-officer-em",
      "cargento:cargento",
      "subspace:dry",
      "subspace:r",
      "subspace:rr",
      "behavior-diff:behavior-diff",
      "behavior-diff:behavior-diff-live",
      "behavior-diff:behavior-diff-retro",
      "design-sync",
      "dataviz",
      "update-config",
      "verify",
      "debug",
      "code-review",
      "simplify",
      "batch",
      "fewer-permission-prompts",
      "doctor",
      "loop",
      "claude-api",
      "workflow-authoring",
      "run",
      "run-skill-generator"
    ]
  },
  "result_metadata": {
    "subtype": "success",
    "is_error": false,
    "duration_ms": 46040,
    "duration_api_ms": 43799,
    "num_turns": 3,
    "total_cost_usd": 0.04927034999999999,
    "usage": {
      "input_tokens": 4,
      "cache_creation_input_tokens": 5475,
      "cache_read_input_tokens": 9137,
      "output_tokens": 1568,
      "output_tokens_details": {
        "thinking_tokens": 477
      },
      "server_tool_use": {
        "web_search_requests": 0,
        "web_fetch_requests": 0
      },
      "service_tier": "standard",
      "cache_creation": {
        "ephemeral_1h_input_tokens": 0,
        "ephemeral_5m_input_tokens": 5475
      },
      "inference_geo": "global",
      "iterations": [
        {
          "input_tokens": 1,
          "output_tokens": 382,
          "cache_read_input_tokens": 4885,
          "cache_creation_input_tokens": 590,
          "cache_creation": {
            "ephemeral_5m_input_tokens": 590,
            "ephemeral_1h_input_tokens": 0
          },
          "type": "message"
        }
      ],
      "speed": "standard"
    },
    "modelUsage": {
      "claude-haiku-4-5-20251001": {
        "inputTokens": 2391,
        "outputTokens": 15,
        "cacheReadInputTokens": 0,
        "cacheCreationInputTokens": 0,
        "webSearchRequests": 0,
        "costUSD": 0.002466,
        "contextWindow": 200000,
        "maxOutputTokens": 32000,
        "thinkingTokens": 0,
        "canonicalModel": "claude-haiku-4-5",
        "provider": "firstParty",
        "costBasis": "list"
      },
      "claude-sonnet-4-6": {
        "inputTokens": 4,
        "outputTokens": 1568,
        "cacheReadInputTokens": 9137,
        "cacheCreationInputTokens": 5475,
        "webSearchRequests": 0,
        "costUSD": 0.046804349999999995,
        "contextWindow": 200000,
        "maxOutputTokens": 32000,
        "thinkingTokens": 477,
        "canonicalModel": "claude-sonnet-4-6",
        "provider": "firstParty",
        "costBasis": "list"
      }
    },
    "permission_denials": [],
    "stop_reason": "end_turn"
  }
}
```

### Tool effects

The two successful Bash calls created the task-owned failure directory and wrote the ACTION.json reproduced above; no other tool calls appear in the retained trace. Exact safe calls/results:

```json
[
  {
    "name": "Bash",
    "input": {
      "command": "mkdir -p /Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.worktrees/spacedock-ensign-skills-mcp-dev-flow-feedback-poc/.context/feedback-poc/failure",
      "description": "Ensure failure directory exists"
    }
  },
  {
    "tool_use_id": "toolu_0116RnYD94q6VgbCgBjfzjGY",
    "is_error": false,
    "content": "(Bash completed with no output)"
  },
  {
    "name": "Bash",
    "input": {
      "command": "cat > /Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.worktrees/spacedock-ensign-skills-mcp-dev-flow-feedback-poc/.context/feedback-poc/failure/ACTION.json << 'EOF'\n{\n  \"action_kind\": \"repair-existing-seam\",\n  \"disposition\": \"enforcement-gap\",\n  \"target\": \"continue-dev-flow (the stage that loads improvement-harvesting on explicit request)\",\n  \"proposed_change\": \"In continue-dev-flow, replace the unnamed 'load harvesting on explicit request' instruction with an explicit named reference to improvement-harvesting.md, and add improvement-harvesting.md to the adopter vendor list so the file is present wherever the stage runs. No new rule is needed; the contract already exists. The seam repair must be verified by a test that confirms at least one handoff is produced after the pointer is restored.\",\n  \"duplicate_search\": \"The improvement-harvesting contract pre-existed both refactors. Consumer checks confirm the destination side of the contract is intact (they stay green). No second copy of the harvesting rule exists to merge with. The rule is not absent \u2014 it is disconnected at the producer end only.\",\n  \"reversal_fact\": \"If the improvement-harvesting contract is found to have never been authoritative (e.g., no adopter ever bound to it and no handoff was ever expected), the disposition would shift to duplicate/no-change and the seam need not be repaired.\",\n  \"reason\": \"The policy requires grepping for the rule before proposing it; the rule exists in improvement-harvesting.md and was intact before extraction. The failure is an enforcement-gap: two successive refactors broke the named pointer without a guard that would have caught it. Adding a new policy or a new collector (the operator suggestion) would duplicate the existing contract and leave the broken seam in place, so both are unsound. The correct action is to name the file explicitly in continue-dev-flow and add it to the adopter vendor list \u2014 repairing the seam at the exact execution point where the disconnection occurred.\"\n}\nEOF",
      "description": "Write ACTION.json with repair-existing-seam recommendation"
    }
  },
  {
    "tool_use_id": "toolu_01MQgbsk99n8RKQQ5GtoS2M2",
    "is_error": false,
    "content": "(Bash completed with no output)"
  }
]
```

## POC outcome

```yaml
poc_outcome:
  admitted_at: "2026-09-10T04:10:01Z"
  decision_ready_at: "2026-09-10T04:19:00Z"
  decision_ready_elapsed_seconds: 539
  captain_interventions_before_decision_ready: 0
  direction: "change"
  evidence: "One real bare CLI execution wrote an existing-seam repair action; initialization still listed installed plugins. See Retained experiment evidence and exact action artifact."
  strongest_limit: "Clean instruction isolation is unproven; plugin enumeration does not prove plugin bodies were loaded. One recommendation replay cannot establish general headroom or runtime repair correctness."
  reversal_fact: "An existing supported runner exposes a verifiable clean instruction boundary and the unchanged baseline reproduces this frozen failure; any new experiment requires separate admission."
  cleanup_status_at_decision: "pending"
```

## POC close measurement

```yaml
poc_close_measurement:
  captain_wait_seconds: 0
  terminal_cleanup_seconds: 1
  cleanup_status: "complete"
```

Initial pre-Captain-gate observation: captain_wait_seconds is zero because no gate has been presented or decided. The measured cleanup covers this worker's disposable experiment files only (including raw transcript); allocated workflow worktree/branch and the Captain gate remain owned by the First Officer. This is not terminal completion. Cleanup started at 2026-09-10T04:21:00.485262+00:00 and ended at 2026-09-10T04:21:00.699745+00:00 (seconds rounded up). Code remained at 6b408ac102978d4bbf3614a7109934191520aa9b with a clean tracked/untracked working tree, and `.context/feedback-poc/` no longer exists. Durable safe evidence is retained in this entity. No product changes, new provider arrangement, cloud workspace, PR, issue, reviewer, validation worker, or recurring check was created.

## Stage Report: implementation

- FAILED: Freeze one real failure and normal control, validate the observation, and run the unchanged baseline through an actual isolated agent runner.
  Cases and rubric were frozen in state commit b91ffdaf567da14dcf541d8cd079384eea2fe708; one actual baseline wrote the correct repair action, but its clean instruction boundary remained unproven because initialization listed installed plugins. See retained prompts, action, trace, and initialization metadata.
- DONE: Use at most four comparison executions and stop on no baseline failure, missing validity, or the 15-minute limit.
  Stopped after one responder execution; zero normal/candidate runs. Decision-ready at 04:19:00Z, 539 seconds after admission, with zero Captain interventions. Missing isolation validity is the decisive stop condition.
- DONE: Record attributable evidence, one direct POC outcome, separate close measurement, and cleanup in this exact task state.
  Exact safe prompts/results, runtime/model metadata, actual file effects, usage, one change outcome, and measured scratch cleanup are retained above; no candidate or product mechanism remains.
- SKIPPED: Candidate authoring, baseline normal, candidate failure, and candidate normal.
  The first observation selected the supported repair and isolation was unproven, so the admitted stop rule forbids further comparisons.

### Summary

The existing runner produced one correct maintenance recommendation under its observed configuration, but did not establish a clean instruction boundary. The direct outcome is change: preserve this bounded observation and stop; no general improvement claim, delivery proposal, gate action, or terminal completion is made.

## Dispatch checklist correction

The First Officer corrected its original completion checklist: its first item required an actually isolated run, although the Captain-approved Exploration Brief requires stopping with `change` when comparison validity cannot be established. The original FAILED report correctly records failure of that stronger dispatch obligation and remains unchanged. This correction follows the First Officer's record-only implementation advance assignment; it changes the stage-completion boundary to include attempting the existing runner and determining isolation, not the frozen experimental criteria or the observed result.

The experiment remains closed at one baseline execution. Instruction isolation is UNPROVEN; initialization listed installed plugins but did not prove their instruction bodies were loaded. Valid comparative proof remains unavailable, and the existing `change` outcome, decision-ready timestamp, close measurement, frozen rubric, prompts, and model results remain unchanged. No new execution or renewed proof occurred during this bookkeeping correction.

## Stage Report: implementation (cycle 2)

- DONE: Freeze one real failure and normal control, validate the observation criteria, attempt the unchanged baseline with an existing runner, and determine whether its instruction isolation is established.
  Freeze commit b91ffdaf567da14dcf541d8cd079384eea2fe708 and retained calibration anchors distinguish no-work, duplicate construction, and existing-seam repair; the single existing-runner attempt wrote ACTION.json, while initialization evidence leaves instruction isolation UNPROVEN. This completes the attempt-and-determine obligation; it does not pass isolation or comparative proof.
- DONE: Use at most four comparison executions and stop on no baseline failure, missing validity, or the 15-minute limit.
  Existing execution metadata records one baseline, zero normal/candidate runs, and the validity-based stop at decision-ready 04:19:00Z, 539 seconds after admission. The correct action is one observation under the observed configuration, not general no-headroom or improvement evidence.
- DONE: Record attributable evidence, one direct POC outcome, separate close measurement, and cleanup in this exact task state.
  Evidence commit 578fae54cd4b1fb13d36c8084016b0965642f282 retains exact safe prompts/results, model/runtime metadata, actual tool effects, one unchanged change outcome, separate initial close measurement, and verified scratch cleanup; this append retains the original FAILED report and all prior bytes.

### Summary

The approved bounded experiment is complete as an attempted comparison with isolation UNPROVEN and direction `change`. The First Officer's checklist correction accounts for the already approved validity stop; it changes neither the experimental scoring rule nor the failed proof, and adds no model execution, product change, gate action, or terminal completion.
