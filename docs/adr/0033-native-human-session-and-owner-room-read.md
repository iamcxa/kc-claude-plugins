# 0033. Keep native human sessions and owner room reads within existing authority

Date: 2026-10-22

## Status

Accepted

## Context

The accepted native account shortcut and logout/re-entry design needs real authority
and real current-room data. The foundation already has human sessions, ordinary
member grants, app logout, protected operator channels and local/provider entry.
An operator label does not identify the unique deployment owner. Invitation and
removal UI/API and one-command deployment remain accepted design, outside this
bounded runtime delivery.

## Decision

**Words:** 「可以，接受這版設計，照最新版 dev2 正式實作帳號捷徑與登出／重新登入流程，補齊實際操作驗證。既有畫布資料、agent 權限與並發規則不動，Cloudflare 維持免費方案，正式部署、啟用與合併前再讓我確認。」 — Kent, 2026-10-22

**Options considered:**
- Reuse native menu/dialog seams and existing human entry/logout; bind one verified owner through the protected operator boundary and expose only current-room reads.
- Infer ownership from an operator role, label, email or room creation.
- Deliver the entire invitation/removal/deployment proposal in this slice.

**Recommended:** Reuse existing authority with an immutable exact owner binding and a shared guarded current-room read destination.

Create only the accepted owner logical metadata key in the existing metadata table:
schema version, backend, exact member/issuer/subject, initialization operation and
time. The protected operator must supply an active server-verified human session
matching that exact identity. Creation is atomic and cannot replace another binding.
No browser route forwards operator commands. Owner read checks the active session,
original sign-in, backend, member, registered current room and current grant inside
the existing adapter transaction. Missing or invalid binding fails closed.

My account and the room menu open the same native destination. It states that
membership is viewable and invitations/removal are unavailable. Ordinary members
manage their own account/agents and cannot read the owner list. Native controls do
not change agent scopes, generations, grant expiry or full-record concurrency.

Confirmed logout preserves pending local draft versions before closing the canvas,
aborts client activity, then uses the existing context/CSRF app logout. Same-session
tabs stop via a scoped origin-local notification. Unknown replies stay unknown and
are not replayed; reload cannot reopen private content without an explicit entry
action. Login cancellation invalidates late replies. Re-entry uses existing adapters
and current room admission, never cached ownership or automatic draft replay.
Provider re-entry preserves the original event/deadline; no global provider logout
or promise of a fresh code is added.

## Consequences

The runtime feature is default-off. Local tests use synthetic identities and
provider evidence; no production credentials, provider settings or personal canvas
data are required. Existing records are not rewritten and no canvas format, SQL
migration or table is added. The owner record is authority and cannot be rolled
back by disabling the UI or restoring an old metadata snapshot. Owner transfer,
recovery, invitation intents, recipient proof, grant/removal mutations and the
single-command deployment remain later work. Formal activation, deployment and
merge still require Kent's confirmation.
