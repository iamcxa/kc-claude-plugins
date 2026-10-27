# 0039. A resolved thread does not clear a Codex finding on the same head

Date: 2026-10-27

## Status

Accepted

## Context

The Codex reader previously let a later no-issues result clear a finding on the
same pull request head. The correction landed in iamcxa/kc-claude-plugins pull
request #728, merge d8e9204bfae64ab4a76ec1a2ef0357a2b8fc7b44. Its ideation
also settled whether a person's resolved mark on a GitHub review thread clears
that finding. The archive observer found this enduring ruling had no ADR.
This record preserves that ruling; it does not introduce a new review policy.

## Decision

**Words:** 「全准」 — Captain, chat, 2026-10-27 (Asia/Taipei).

Verbatim gate resolution reason:

> Captain 「全准」 (chat, 2026-10-27) answering 「需要你決定：第 7 批三張任務的設計（其中兩張已經照第 2 輪訪談修過），要不要一起批准進入實作？我建議全部批准，每一題都照我的建議。」; accepts FO's recommendations

Source: `spacedock-state/dev2:_archive/codex-reader-same-head-unresolved.md`
at state commit `3e25da97432fb22a1a6a7da973730e7c829f3619`,
ideation attempt `gate-attempt:codex-reader-same-head-unresolved-ideation-1`,
resolution `resolution:spacedock:codex-reader-same-head-unresolved:ideation:1`,
recorded at `2026-10-26T17:05:57.33005Z` (2026-10-27 in Asia/Taipei).
The accepted recommendation is D1 under that task's
`## Unresolved decisions for the Captain`; the following rule is a description
of the accepted recommendation, not additional words attributed to the Captain.

**Options considered:**
- A person's resolved mark does not clear a finding on an unchanged head; the
  finding holds until the head moves or the First Officer records its disposition
  in the gate summary (chosen).
- Read GitHub review-thread resolution and let it clear the same-head finding;
  not chosen. The archived design observed no such consumer and this required
  another GraphQL call, pagination and an additional failure path.

**Recommended:** the first option, as D1 recommended and the ideation gate accepted.

**Protects:**
- `kc-dev-flow-2/extensions/codex/codex_review.py` — `state()`, selecting held findings before later no-issues evidence.

A person's resolved mark on a GitHub thread does not clear a Codex finding on an
unchanged head. A later no-issues receipt on that same head does not clear it
either. The reader continues to report the finding and its evidence id.
A new head is read afresh. The First Officer may decline a finding in the gate
summary only under the existing review-disposition rules; that disposition does
not change the reader's verdict. Material findings still require repair or a
Captain waiver, and reviewer P1 findings still require repair and revalidation
or the Captain's recorded waiver, as ADR 0004 requires. ADR 0010 governs
nonblocking findings from round three. Resolving a thread alone grants no waiver.

## Consequences

A finding someone marks resolved on GitHub can still read as findings on the
same head, so the First Officer must record the permitted decline in the gate
summary or move through the existing repair or Captain-waiver route. The reader
adds no thread-resolution request, and a repeated clean receipt does not create
a new round when the deciding evidence id is unchanged. This record does not
prove a code repair, provider behavior or future agent compliance. Revisit only
through a new Captain ruling if an actual use case needs thread-resolution state
to change the reader's verdict.
