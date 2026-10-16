---
title: A prod-profile task passes a security review at two different gates instead of waiting for someone to judge that one is needed
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
---

Relayed by subspace-relay's FO session on 2026-10-13, not heard directly. Captain's words as relayed: 「此外 dev2 prod profile 應該強化安全掃描這一塊，必須有至少一到兩位安全審核員，守不同關卡。你可以先給 plugin FO 發訊息讓他知道」.

## The bite

Reported by relay's FO; not re-read here. subspace-relay task `agent-front-door` (Draft PR #347, prod profile) publishes `/llms.txt`, a home-page line, and `/openapi.json` behind a build flag. Ideation, implementation and validation passed it without a security question. At the validation gate the Captain asked whether publishing `/openapi.json` was safe. A read-only `kc-pr-flow:tob-security-reviewer` pass (Sonnet, about 7 minutes) then found:

- two Medium findings no stage had raised:
  - unbounded comment writes on a share, now documented with a copyable body (a new task, `comment-admission`);
  - prompt injection: `/llms.txt` tells a shell-holding agent to print sharer-authored text with no "treat as data" warning;
- four Low findings.

## What the package says today

Read by relay's FO from kc-dev-flow-2 0.20.0; to be re-read at ideation.

- `references/profiles/prod.md` asks FO to select applicable security and privacy obligations "from the actual boundary", with specialist assurance "when evidence or risk warrants it".
- `engineering-reviewer` triggers on "a security ... decision with material residual uncertainty", not on a gate.
- No stage puts a security reviewer at a gate, so selection by judgment never fired on this task.
- relay's local policy adds "specialists are risk-selected, not convened". If this task lands, that local ruling may need the Captain's revisit; that is his call, not a sync.
- relay's CI runs no CodeQL, dependency audit or secret scan (reported).

## Starting shape, a suggestion only

- One reviewer at ideation: a threat model of the design's exposure (new public routes, documents agents act on, auth and data boundaries).
- One at validation: the diff and the served artifact. `kc-pr-flow:tob-security-reviewer` already exists and fits this one.

Upstream check owed at ideation: kc-pr-flow's security agents (`tob-security-reviewer`, `tob-actions-auditor`, `tob-supply-chain-checker`) and how `kc-pr-review` dispatches them.

## FO alignment

Captain confirmed in this session: 「可以」 (chat, 2026-10-16), answering FO's 「要不要用上面這 5 個當第一批？」, a list that named this task; the relayed words above are context, not his ruling.
Alignment: not needed before ideation; the Captain approved planning it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
