# 0037. Workers check shared work and return to FO early

Date: 2026-10-27

## Status

Accepted

## Context

The Captain asked workers to understand their place in a cooperating team, check
prior work and ownership, and ask the First Officer (FO) early. The task
worker-knows-the-team-and-asks-early records the original request, the revised
design and ideation gate attempt 2. Interview feedback added named records,
required-check feasibility before dependent work, terminal handback without a
mid-run channel, and the prohibition on answering worker/reviewer permissions.
Dispatch facts already reaches the three worker stages and the two derived POC
stages through their context selectors; peers supplies the FO-facing half.

## Decision

**Words:** 「要開。我覺得這一張跟peer有點關係，不只是讓他們知道有其他人在，他們也要知道目標是合作完成任務，所以要主動去思考，是不是有人做過是不是有人遇過，是不是有其他人在忙，特別是什麼時候應該提早問fo」 — Captain, chat, 2026-10-26.

「要注意接手的不見得是codex但是重點是它要知道它在一個大流程的環節內，交棒是為了完成更遠大的目標，不是盲目努力完成不可能的目標」 — Captain, chat, 2026-10-26.

「全准」 — Captain, chat, 2026-10-27; ideation gate attempt 2, recorded
2026-10-26T17:06:03.756936Z.

**Asked:** 「需要你決定：第 7 批三張任務的設計（其中兩張已經照第 2 輪訪談修過），要不要一起批准進入實作？我建議全部批准，每一題都照我的建議。」 The accepted recommendations put the revised 144-word Team bullet in Dispatch facts, raise the workflow budget from 5421 to 5565, and keep the broader upstream/decision check as a separate following task.

**Options considered:**
- One shared Team bullet, the explicit +144 budget step, and the broader upstream/decision task following separately (chosen).
- Merge the broader task into this delivery, enlarging the capability and ADR audit.
- Decline the reading-cost increase and return for a smaller design or an evidenced equivalent cut.
- Duplicate the rule in stage skills or change upstream ensign scaffolding, adding separate instruction homes or ownership work.

**Recommended:** The shared Team bullet, explicit 5421-to-5565 rise and separate following task; the Captain accepted the revised design's recommendations.

**Protects:**
- `kc-dev-flow-2/scripts/lint-skills.py` — the +144 workflow-budget step, Captain quote and loaded moments.

Dispatch facts carries the worker collaboration rule. Workers read the named
prior reports, linked sibling tasks/PRs and relevant workflow records before
substantial work or another failure attempt. They return checked evidence and a
specific need to FO early when ownership, authority, required-check feasibility
or the target blocks progress. They pause dependent work with an effective
mid-run channel; without one they end the turn with findings and the question.
They do not answer their own or reviewers' permission requests, message peers or
change another owner's work. Existing approval and validation-independence
boundaries remain in force; FO coordinates the next authorized action.

The +144 words are read at FO startup/resume and each fresh or reused stage
context load by FO and its worker. ADR 0020's equality check accounts for this
increase; the added text stays in the shared README rather than moving its cost
into another instruction surface.

## Consequences

The shared text reaches fresh and reused workers through existing transport.
It increases each full README or stage-context load by 144 words; the specified
startup trace rises from 5863 to 6007. Warm lifecycle passages are unchanged.
Instruction delivery proves neither compliance, savings nor host parity; native
behavior replays and independent validation remain distinct evidence duties.
A no-channel handback needs an FO follow-up. Normal release and separately
authorized README sync carry this text to adopters while retaining customization;
installing a package alone does not update an adopted README. Revisit the rule if
behavior evidence shows its instructions cannot be followed on a supported host.
