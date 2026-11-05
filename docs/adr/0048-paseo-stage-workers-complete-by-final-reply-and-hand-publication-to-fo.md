# 0048. Paseo stage workers complete by final reply and hand publication to FO

Date: 2026-11-02

## Status

Accepted

## Context

Four Claude stage workers dispatched through Paseo's command-line route were
told to send completion to `main`, which resolved to themselves and was refused.
One ended without a signal and the Captain asked about the stalled work nine
hours later. The task worker-completion-reaches-fo-on-paseo records the probes:
Paseo's create_agent callback delivers the worker's final reply on finish, and
also reports errors and permission holds. The command-line spawn has no callback.
ADR 0042 limits the publication handoff to Codex workers through Paseo.

## Decision

**Words:** 「可以」 — Captain, chat, 2026-11-02, at the backlog sitting.

**Asked:** 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」
FO had stated 「工作者完成時要確實通知到 FO」 and 「排第一」.

「照建議」 — Captain, chat, 2026-11-02, at the ideation sitting.

**Asked:** 「決定：五張設計進實作、Gemini 這張停在這裡，四個決定都照建議嗎？要改哪件直接說。」
The accepted completion recommendations were D1, registration in the same shell
command as dispatch build, and D2, keeping the rule only in the listed paseo
extension with the workflow word budget unchanged.

**Options considered:**
- Use create_agent with notifyOnFinish true, final-reply completion, same-command
  workspace registration and the listed extension boundary (chosen).
- Keep command-line spawn and arm callbacks with a second send_agent_prompt,
  adding a message and dispatch record for every new worker.
- Put the completion rule in the shared workflow, increasing every adopter's
  reading load and requiring a workflow word-budget rise.

**Recommended:** The first option, including D1 and D2, as the Captain accepted.

**Protects:**
- `kc-dev-flow-2/scripts/dispatch_records.py` — the final-reply completion line is accepted only when the workflow README lists paseo.

This widens ADR 0042 to Claude workers: every stage worker dispatched through
Paseo in a workflow listing paseo follows the extension's local-commit handoff;
FO owns publication and local review under the applicable authority. No new
push, PR, ready or merge grant is created.

Spawn through create_agent with notifyOnFinish true and an explicit modeId.
Place the worker by an explicit matching workspaceId. When dispatch build
creates the worktree, chain its registration onto the same shell command so
create_agent is the next host action; a failed registration holds dispatch.
Replace the main-recipient scope line with the extension's final-reply line.
The worker ends with the Done line as its reply and sends nothing itself.
A finished callback starts verification; a reply without Done, an error or a
permission hold does not complete the stage. FO never answers the worker's
permission on its behalf. Non-Paseo dispatch retains its existing main line.

## Consequences

The listed extension grows from 713 to at most 819 words; the shared workflow
and its budget stay unchanged. Workflows without paseo do not gain the rule.
FO retains report verification, independent validation and publication duties.
Real-FO callback and placement evidence remains necessary on the candidate;
unit tests cannot establish native delivery. Registration failure leaves a
stamped dispatch to hold and reconcile. Revisit if callbacks fail to reach FO
or the supported placement route cannot preserve immediate spawn order.
