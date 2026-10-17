# 0019. A prod task's ideation runs one security review that the design check enforces

Date: 2026-10-17

## Status

Accepted

## Context

A prod-profile task on a sibling repository passed ideation, implementation and validation with no security question. When the Captain asked at the validation gate whether publishing an OpenAPI file was safe, a read-only `kc-pr-flow:tob-security-reviewer` run found two Medium findings no stage had raised: a prompt-injection path in a document agents act on, and unbounded comment writes. The package's `references/profiles/prod.md` asks FO to select security obligations "when evidence or risk warrants it" and no stage binds a reviewer, so the selection by judgment never fired. The Captain's amendment 2 changed the first design (an opt-in extension reviewing at two gates) into a review that always runs at prod ideation; the validation-gate review is a separate backlog task.

## Decision

**Words:** 「照這樣做」 — Captain, 2026-10-16, chat, answering 「照這個做嗎？」 (「整理成第 2 號修正指示：1. prod 任務在設計階段一定跑安全審核，發現的問題寫進設計和驗收條件。有專案自己的安全清單就一起交給審核員。2. 驗收關的審核另開任務，同時做三種模型的比較，用量測結果決定預設模型和推理等級。」); D1 to D3 accepted as recommended at the ideation gate approval (「准」, 2026-10-17)

**Options considered:**
- the ideation worker dispatches `kc-pr-flow:tob-security-reviewer` unchanged on every prod design, writes one disposition line per finding, and the existing `design_surfaces.py check` that FO already runs before `gate prepare` refuses a prod design at ideation without a review that ran or a finding without a disposition (chosen)
- an opt-in `security` extension that FO reads and dispatches at two gates (the first design; withdrawn by amendment 2, wrong carrier for "always": it is opt-in and read by FO)
- a new security reviewer agent in this package — not chosen: `kc-pr-flow:tob-security-reviewer` exists and fits
- D1 focus file: the one path `.claude/agents/security-reviewer.md` (chosen); a README key naming the path — not chosen, one more adopter setting
- D3 model: the agent's declared Sonnet until the validation-gate task's three-model measurement reports (chosen); a stronger model now — not measured

**Recommended:** the first option, D1 the single path and D3 Sonnet, as the Captain accepted.

`skills/ideation/profiles/prod.md` carries the review step and the reviewer brief. `design_surfaces.py check` on a task whose frontmatter is `profile: prod` and `status: ideation` requires a `Security review:` line naming a `tob_security_review` report inside the task folder, a `Security focus file:` line, and one `Security finding <n>:` line per `severity:` entry in the report, each a declared `AC-<id>`, `declined: <reason>` on a MEDIUM or LOW finding, or `Needs decision: <text>`. `not run` is an error: a missing reviewer holds the stage and is never recorded as clean. D2, relay's v1 sentence "Specialists are risk-selected, not convened", is narrowed by relay's own FO in relay; this package edits no relay file.

## Consequences

Every prod design gets one reviewer run (120,562 to 142,076 tokens on one public-surface design, 55,856 on one with no exposure, measured on Sonnet) and the worker writes a disposition per finding. FO reads 12 more words at the ideation gate of a prod task and none elsewhere. The check proves a disposition exists, not that the criterion answers the finding; the Captain reads the pairing at the gate. The report is model output on a design that reads no code not yet written. An adopter without kc-pr-flow holds every prod ideation. Reopen if the validation-gate task's measurement favours another model, or if a worker pairs findings with criteria that do not answer them.
