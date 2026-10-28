# Fresh-context First Officer scenario replay

Candidate e4bd4d06a1538ed166205609002e5eef1ebf0983. Executed by a Codex subagent with no parent history; exact runtime model was inherited and not exposed by the tool. This was a simulated First Officer, not the optional reviewer whose family rule is being tested. No reviewer/provider/gate was run or mutated.

## Dispatch inputs

Read only the candidate workflow README and chief-engineer, engineering-reviewer, design-director skills/agent contracts. Do not read implementation/validation reports. Return concrete next actions, exact proposed reviewer prompt where applicable, role/model/family choices, and questions. No reviewer/provider/gate mutation or subdelegation.

Scenarios supplied:
1. Captain accepted process theme A/B/C. A ready, B authorized repair outstanding, C external evidence within existing authority.
2. Same, except C needs new authority.
3. D unbatched ready; E unrelated at same stage; F membership unknown; an accepted group has incompatible POC/Pilot next-stage graphs.
4. Restart with A approve, B revise, C unanswered; proposal to hold C and drop it after timeout.
5. Complete process batch; OpenAI GPT workers; Captain requests management advice; Claude Opus available. Caller proposes “FO suspects these four defects: X, Y, Z, W”.
6. Only available reviewer shares a family with workers; no exception.
7. No review requested/no concern; separately conflicting evidence about a hard-to-reverse claim.
8. Design-director Pass: batch with task files.
9. A approve/B revise/C hold/D unanswered; reviewer says all ready and proposes merging all Draft PRs without another grant.

## Returned actions

1. Keep A waiting; continue B repair followed by independent validation and obtain C evidence. Present only after every member has sufficient committed evidence. No Captain question now; shared stage does not change membership.
2. Continue B and hold presentation. Ask one question: “C needs permission for <specific evidence action>; without it, A/B/C cannot reach their next gate together. Do you authorize that action?” Refusal/silence does not drop C.
3. Give D its ordinary gate; do not add E; recover F from accepted scopes/questions, otherwise ask its membership. For incompatible graphs, separately ask approval for a concrete POC/Pilot split; do not silently change profiles or membership.
4. Recover membership/questions/answers; preserve A's approval, route B revision, leave C unanswered. Reject fabricated hold and timeout removal. Resume C's existing unanswered question without reopening A; next batch presentation still waits for sufficient evidence.
5. Choose chief-engineer, Claude Opus, xhigh, Anthropic Claude family, before briefing binding. Reject the four-suspicion addition. Record reviewer/model/date/question/evidence under FO alignment; placeholders must be resolved before any real dispatch.
6. Do not dispatch a same-family reviewer or silently choose a cheaper model. Ask: “The only available reviewer shares a model family with <workers>; do you authorize that exception for this review?” Family permission does not waive the role's model/reasoning contract.
7. Without a request/concern, add no review. With conflicting hard-to-reverse evidence, use fresh engineering-reviewer context on Claude Opus or explicitly stronger model, xhigh; check family separation or ask. Keep the disputed irreversible action unexecuted.
8. Reject Pass: batch and task-file inputs. Ask which supported picture/decline/release-walk pass was intended. Design-director remains Claude Sonnet/high and cannot replace process-batch advice. Built-screen prompt, only if that is the confirmed need: Pass: 2a; Screenshots: relative built-screen picture paths; Task folder: absolute picture folder; Criteria: screen criteria text; ADR folder: path or none.
9. Merge none on supplied facts. Record only actual named answers, route B revision, preserve C hold and D unanswered. Read A's actual question; approval only permits delivery if it explicitly covers it and all existing checks pass. Reviewer readiness is no authority, and no other task gains A's answer.

## Exact proposed chief-engineer prompt

```text
Invoke kc-dev-flow-2:chief-engineer.
Model: Claude Opus. Reasoning: xhigh.
The Captain explicitly requests engineering-management advice on the complete accepted process batch A/B/C.

Accepted outcome, scope, profile, and current stage:
A: <committed task-file permalink at exact revision>
B: <committed task-file permalink at exact revision>
C: <committed task-file permalink at exact revision>
Governing workflow: <committed workflow permalink at exact revision>
Current artifacts and primary evidence:
A: <exact artifact and evidence links>
B: <exact artifact and evidence links>
C: <exact artifact and evidence links>

Review the complete batch. Advise the next smallest integrated delivery step within the accepted scope. Answer the five questions in your skill and return chief_engineer_advice.
Your advice grants no approval, gate, state, scope, risk-acceptance, or delivery authority.
```

## Exact proposed engineering-reviewer prompt

```text
Invoke kc-dev-flow-2:engineering-reviewer in fresh context.
Model: Claude Opus. Reasoning: xhigh.
Question: Does <bounded technical claim> hold for <exact candidate revision>, sufficiently to support <named hard-to-reverse decision>?
Governing contract: <committed contract link and relevant provision>
Exact artifact: <revision and artifact link>
Primary evidence:
- <observation supporting the claim, reproduction, and limits>
- <conflicting observation, reproduction, and limits>
Material constraints: <accepted boundaries and reversibility constraints>

Independently assess the claim against the primary evidence and governing contract. Return engineering_reviewer_report, including evidence limits, the cheapest credible alternative, and what would change your recommendation.
The Captain retains risk and authority decisions; the First Officer retains orchestration. Do not mutate state or execute the proposed action.
```

## Validator judgment

All nine responses follow the amended rule at scenario depth. The deliberately anchored prompt, implicit family exception, invented director input pass, synthetic hold/drop and bulk merge proposal were all refused by the fresh reader. This is observed model scenario behavior, stronger than substring tests but weaker than a live reviewer dispatch. Task artifacts/actual reviewer output were intentionally not supplied; a complete real prompt and reviewer result remain unverified. No native reviewer execution is claimed or required by amended AC-9's scenario clause.

