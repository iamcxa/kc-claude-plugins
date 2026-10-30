# 0046. Confirmed Paseo transport permits peer asks without optional extension selection

Date: 2026-10-30

## Status

Accepted

## Context

Interview round 004 found five First Officers (FOs, workflow coordinators) asking
Paseo peers while their workflows did not list the optional paseo extension.
Qnow's Captain-directed question had no compliant outbound path. ADR 0038 chose
optional listing for new asks; required peers already carried incoming replies.
The task peers-paseo-rule-matches-practice holds the interview replay, revised
design and ideation gate records for the Captain's decision.

## Decision

**Words:** 「准」 — Captain, chat, 2026-10-30, joint batch-11 ideation sitting;
recorded in the task's ideation gate at 2026-10-30T09:31:39.460058Z.

**Asked:** 「決定：六張全照建議，同意放寬 Paseo 規則和真實測試，並授權改完直接進實作？要改哪張直接說。」
The accepted revise asks relax the listing prerequisite for confirmed Paseo
transport, record that reversal in a new ADR and require a real two-agent ask,
reply and notice plus quiet-send failure visibility at validation. FO approved
the bounded revised design at 2026-10-30T10:00:12.835097Z under that grant.

**Options considered:**
- Permit asks and replies through confirmed Paseo transport without listing
  paseo, retaining peer authority and routing boundaries (chosen).
- Keep ADR 0038's listing prerequisite and list paseo in each affected adopter,
  adding selection work and enabling its worker procedure.
- Keep listing for routine asks with a Captain-named one-off exception, leaving
  two permission paths and a restriction inconsistent with observed practice.

**Recommended:** Transport-based permission without an adopter listing campaign
or named-ask exception, with one owner for Paseo status wording and native
ask/reply/notice and failure-visibility proof before validation passes.

**Protects:** none

This ruling supersedes only ADR 0038's optional-listing prerequisite for outbound
Paseo peer asks. Required peers owns the Paseo binding for confirmed transport;
non-Paseo peers keep their binding. Preserve stamped identity, confirmed area,
original human authority, source checks, the five-minute busy-peer ceiling and
the requested-running-reply exception. Messages confer no action authority.

Routine peer asks, requested replies and information-only notices request
explicit steering and disable completion callbacks through peers' binding.
Match explicit sourced replies to their question once; receipts and silence are
not answers. Notices request no acknowledgement. Preserve the specifically
recorded callback choice when an explicit return route is unavailable. Quiet
mode must not hide errors or permission holds: unavailable or failing native
proof holds acceptance and returns the policy to FO, without a host repair,
watcher, polling service or automatic default change.

ADR 0035's required learn/peers defaults and optional extension selection remain.
Listing paseo selects ADR 0042's worker publication/local-review handoff;
peer messaging does not activate it. The fo-feedback extension retains its own
selection, maintainer, anchor, cadence and question grant, with an available peer
transport rather than a redundant paseo listing prerequisite. Worker completion
notifications and Spacedock's dispatch, gates and task state remain governed by
their existing contracts.

## Consequences

Omitting paseo no longer opts a repository out of confirmed-Paseo peer asks.
Incoming-only readers of the whole peers file read more text. The policy is prose,
not a send interceptor; steering can still fall back to interruption after an
unknown capability or status race. No zero-interruption guarantee is made.
One task owns the Paseo status pointer; peer-status-reaches-fresh owns shared
current-fact checks and its separate evidence. The authorized native validation
must distinguish hidden errors/holds from unresolved exchanges before quiet-send
acceptance; a safe failure route being unavailable is missing proof, not success.
Reopen on that failure or a requested host, notification, worker or authority
change. No adopter edits, version bump or measured runtime/CI saving is claimed.
