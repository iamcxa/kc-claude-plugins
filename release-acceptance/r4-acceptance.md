# QNow RELEASE 4 acceptance walk (hosted staging), 2026-10-10

Target: https://qnow-staging.netlify.app at origin/next 7d72636379584eb0304660de722a404f3affc3d5 (R4 code confirmed deployed: brandName/shopActive on /api/bookings, the invitations accept route, the profile entry, the antd sign-in card). Walked by a fresh worker with Playwright and the repository's Clerk testing-token helper. Screenshots in this directory.

## Result per R4 story (6)

| Story | Result |
|---|---|
| onboard-through-operator-api | not reachable on staging: the operator API needs QNOW_OPERATOR_SECRET; scripts/with-dev-secrets.sh exports only the four Clerk variables; unauthenticated calls answer 401 (route deployed, secret set on staging) |
| add-branch-to-tenant | not reachable on staging (same reason); staging has one branch, /api/shops/demo-branch-2 answers 404 |
| office-header-shows-phone | works, one-branch form only |
| one-person-several-branches | not reachable on staging: needs a second branch and a manager; staging seeds only a reception and a technician |
| accept-branch-invitation | not reachable on staging: no manager or operator can create an invitation; the accept route is deployed (404 INVITATION_NOT_FOUND for an unknown id) |
| bookings-tab-lists-visited-shops | works, one-branch form only |

R4's proof line 「一位店長在兩間分店間切換，各看各的預約」 cannot be performed on staging. The multi-branch behaviour is proven only by local specs that plant rows directly in the database.

## Cross-story findings

- C-1: no product path on staging to a second branch or a manager. ADR 0027 lists the qnow-staging operator secret among the secrets moved to the vault, but with-dev-secrets.sh does not export it and no op:// reference names it. The shop map's onboarding note 「兩支腳本都要直連資料庫」 is stale since onboard-through-operator-api exists.
- C-2 (defect, not an R4 change): the owner app's tab-bar icons are hollow squares on staging. The Ionicons font URL under /app/assets/__node_modules/.pnpm/@expo+vector-icons@15.1.1…/Ionicons.*.ttf answers 200 text/html (the app's HTML page) instead of the font; document.fonts reports ionicons: error. Production not checked.

## Observations (worked, but may confuse a first-time user)

O-1 one-branch profile panel shows a single checked branch row; O-2 one-branch 預約 tab shows a bare card; O-3 at 390 px the office header hides the role; O-4 signing in from 我的預約 lands on 預約 (as in R3); O-5 the office refused page does not say whom to ask; O-6 one browser session is shared by /office and /app; O-7 a direct /office/staff link gives 權限不足 with no menu link.

## Staging data created

Clerk user +15555550172 (owner 「R4驗收甲」) with one pending booking on 2026-10-16 09:00 (id b5699be6-ed99-470e-b86e-2cc42c5ec4a3); sign-ins as +15555550102, +15555550113, +15555550171. No operator write; nothing deleted.

## Update, same day: with the operator secret (opt-in via `QNOW_OPERATOR_SECRET=op://qnow-dev/qnow-staging-operator/secret scripts/with-dev-secrets.sh`)

All six R4 stories work end to end on staging (supersedes the four "not reachable" rows above). Branches 大安 (demo-branch-2) and 松山 (demo-branch-3) were created through the operator API; the proof line 「一位店長在兩間分店間切換，各看各的預約」 works for manager +15555550173 between 大安 and 松山; invitations, the manager's two-step add, 確認, the revoke case and the 預約 tab with two and three branches all work.

New cross-story findings:
- C-3: the seeded 信義 has no manager and no product path gives it one; manager stories on 信義 stay untestable on staging.
- C-4: switching branch from a sub-page reloads to the home list (the page the manager was on is lost).
- C-5: a first-time number whose only access is an invitation lands on a page headed 「此號碼沒有店家權限」, with the invitation below 登出.
- C-6: a manager added directly by rule 1 sees no notice of the new branch (not proven absent; checked about 4 s after load).
- C-7: the manager's staff list shows an invited person as 待綁定, with no 邀請中 state.
- C-8: a cold office load shows 「目前沒有資料」 for about 1 s; branches whose name starts with the brand read 「QNow 示範車廠・QNow 示範店・大安」 in invitations.
- C-1 stands as a documentation gap (the opt-in line is not in the repo); C-2 (icon font served as HTML) is unchanged.

Staging data added: branches 大安 (branch 29d3d294-7b00-56f9-864e-485f69281054) and 松山 (branch 286e7e22-6cf6-5131-8bef-2e2c94cd9ace), both open; +15555550173 manager at both; +15555550174 技師 at 大安; +15555550102 also 技師 at 大安; +15555550113 also 接待 at 大安; bookings by +15555550172 at 大安 (2026-10-15 10:00, id f344f1f0-42e0-44c1-ba76-9c60a5cd5f33) and 松山 (2026-10-14 11:00). Nothing deleted.
