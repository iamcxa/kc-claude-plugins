# 0032. Enroll only an explicitly resolved private member

Date: 2026-10-20

## Status

Accepted

## Context

Immutable bootstrap cannot enroll a new person after initialization. The private
operator needs an exact existing-room grant without a pending-invitation format,
public administration route, automatic signup, member reenable or new action roles.
Provider identity discovery and the recipient's signed application login are separate
checks. Local synthetic evidence cannot establish real provider behavior.

## Decision

**Words:** 「可以，接受這個首次加入流程，開始管理指令的本機實作與測試，維持預設關閉。Cloudflare 維持免費方案，既有畫布資料與並發規則不動，用量明細只留本機，正式啟用與合併前再讓我確認。」 — Kent, 2026-10-20

**Options considered:**
- Resolve the exact tenant identity, explicitly confirm existing rooms, then atomically enroll through the private operator boundary.
- Add pending invitations or silently grant on the first login.
- Require the recipient to export a token or operate a terminal.

**Recommended:** Resolve the exact tenant identity and explicitly confirm the complete grant through the private operator command.

Use authenticated same-account discovery, pinned issuer/application/audience/origin
and the configured one-time-password provider. The users-list ID is only a lookup
ID; only the authenticated last-seen `user_uuid` is the candidate subject. Preserve
the original human event and fourteen-day maximum. Missing, ambiguous, stale or
unsupported proof refuses without a grant. If there is no prior identity, ordinary
email-code login happens first; the existing unbound refusal is followed by explicit
operator enrollment and another ordinary login. The latter must independently
verify the signed subject against live identity before issuing a session.

Create the ordinary member, identity index, exact room set and existing security
audit inside the current adapter transaction. Reuse all existing formats. Scan
retained membership/history even when an index is missing. Exact generation-one
current state is a read-only no-op; changed/disabled/revoked/inconsistent history
conflicts. Never choose another ID to bypass history. Lost replies remain unknown;
inspect exact state without automatically resending the mutation. A local receipt
is evidence, not replay authority or a persistent server schema.

## Consequences

The command is default-off and restricted to the owning Node control channel or
separate Cloudflare private service. Ordinary browser and agent credentials gain no
administration. Node local-owner entry refuses remote-email enrollment. Enabling
the command does not change provider policies, existing canvas data, concurrency,
bootstrap, session/family revocations or room capabilities. Disabling it stops new
enrollments but does not undo committed grants; use separately approved existing
revocation operations and retain tombstones. Real enrollment, provider observation,
activation, publication and merge require their own authority. Actual provider field
behavior, original subject correlation and Free-plan usage remain unverified here.
