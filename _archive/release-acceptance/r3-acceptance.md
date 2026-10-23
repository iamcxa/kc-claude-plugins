# QNow RELEASE 3 acceptance walk (hosted staging), 2026-10-09

Target: https://qnow-staging.netlify.app at origin/next 6d8e119eb42a6461d1fbcb23c513faeacbfe4f48. Walked by a fresh worker with Playwright (Clerk testing token via scripts/with-dev-secrets.sh). Screenshots in this directory.

## Result per R3 story (9)

| Story | Result |
|---|---|
| new-customer-enters-name | works |
| new-customer-adds-plate | works |
| search-brand-model-or-add | works |
| returning-customer-picks-saved-vehicle | works (O-1) |
| owner-leaves-note | works |
| confirm-own-profile | works (X-2 is the known gap story owner-app-knows-brand) |
| see-booking-vehicle | works (X-1) |
| see-booking-note | works (X-1) |
| reset-uat-database | not reachable on staging (operator script that resets staging; not run) |

R3 goal (name, vehicle, note from owner to both office lists) works end to end; values match field for field.

## Cross-story findings, with FO triage

- X-1 (defect, new): at 1280 and 1366 px, with the sider open, the 待確認預約 table's 價格 and 操作 columns are outside the visible area with no visible scroll bar, so 確認 cannot be seen without sideways scrolling; one booking with long typed brand/model and a long note pushes it out at 1920 too. Screenshots: office-recep-01-home.png, office-recep-08-width-1366.png, office-recep-10-long-1920.png. Routed to task office-layout-batch.
- X-2 (known gap): the 帳號 tab shows the name field only after this browser opened a shop link. This is journey story owner-app-knows-brand (gap, after go-live per Captain 2026-09-29).
- X-3 (not a defect): the 帳號 tab passes the phone through maskPhone (apps/qnow-app/app/(tabs)/account.tsx), which masks +886 numbers only; the +1 test numbers display whole.
- X-4 (by design): renaming does not change earlier bookings; a booking keeps its own name copy (ADR 0028).

## Observations (worked, but may confuse a first-time user)

- O-1: with two or more saved cars none is preselected and 送出預約 is disabled with no hint.
- O-2: saving the name in 帳號 gives no confirmation; an empty field enables 儲存.
- O-3: signing in from 我的預約 lands on the 預約 tab (journey gap signed-out-link-keeps-destination).
- O-4: /app with no shop visited has no way in (journey gaps open-app-without-qr, pick-nearby-shop).
- O-5..O-9: brand picker order, size chips without heading, plate checked only on submit, pre-R3 rows show 未登記, office table on a 390 px phone.

## Not tested

reset-uat-database; a human passing Turnstile; real SMS and production; native apps and mobile browsers; a pre-R3 office build (X-1 as a regression is not proven); non-R3 paths.

Staging data left: Clerk users +15555550170, +15555550171; demo bookings 10/10 and 10/12-10/15 at 09:00 (10/10 and 10/14 confirmed).
