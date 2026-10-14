# Task to story backfill proposal (read-only research, 2026-10-14)

Source: journey map `origin/main:docs/journey/spacedock-review.yaml`; tasks from each `origin/spacedock-state/<workflow>` branch (active and `_archive` task files only). Nothing was edited.

## Summary

| Repo / workflow | Tasks | Already mapped | Proposed story | Infra | No-story | Unclear |
|---|---|---|---|---|---|---|
| subspace-relay / dev2 | 49 | 15 | 20 | 12 | 2 | 0 |
| subspace-relay / dev2-poc | 8 | 3 | 4 | 1 | 0 | 0 |
| subspace-v0 / dev2 | 12 | 1 | 11 | 0 | 0 | 0 |
| subspace-web / dev2 | 22 | 2 | 15 | 3 | 2 | 0 |
| **Total** | 91 | 21 | 50 | 16 | 4 | 0 |

Counts: "Proposed story" excludes already-mapped tasks (their story is kept). A story is "covered" if an existing or proposed task points at it.

| Release id | Stories | With at least one task | Stories with no task |
|---|---|---|---|
| second-opinion (Release 2.0a - Land what is built: publish from the TUI, comment on the web, collect) | 19 | 4 | `share-document`, `confirm-owner-tui`, `publish-to-review-domain`, `open-shared-link`, `know-comment-identity-web`, `open-shared-artifact-tui`, `know-comment-identity-tui`, `read-artifact-web`, `web-feedback`, `read-artifact-tui`, `terminal-feedback`, `comment-across-browsers`, `confirm-sent-tui`, `reopen-original`, `see-feedback` |
| pairing (Release 2.1 - My agent's link opens as mine; sign up to keep it) | 6 | 6 | - |
| owner-decides (Release 2.2 - The paired owner decides on the web) | 4 | 3 | `verdict-closes-the-round` |
| owner-mode (Release 2.2 · owner mode - See every comment, keep my name, choose what to send) | 5 | 3 | `owner-keeps-name-and-comments`, `web-choose-comments` |
| owner-account (Release 2.2 · account - A home page and a real sign-out) | 4 | 3 | `decision-names-account` |

Notes:
- Stories covered only by tasks from several repos are counted once.
- `env-overridable-daily-quota` and `verify-web-bundle`, `see-the-link-has-expired` have no release in the map; they appear in no release row.
- Review of existing mappings: relay-dev2/publish-admission: existing release agent-front-door but map says second-opinion-later; relay-dev2-poc/agent-front-door-learnability: existing release agent-front-door but map says second-opinion-later

## subspace-relay / dev2

| Workflow | Slug | Status | Completed | Title | Existing | Proposal | Reason | Conf |
|---|---|---|---|---|---|---|---|---|
| dev2 | one-share-link | done | 2026-09-24 | One share link: /r/{s} serves the TUI download and the Web Room; /room/ is removed | - | `one-link-only` | "One share link: /r/{s} serves the TUI download and the Web Room" matches card "Paste the link my browser shows and have it work" | medium |
| dev2 | env-overridable-daily-quota | done | 2026-09-24 | Daily per-device limits can be overridden by environment; briefings default to 100 | - | `env-overridable-daily-quota` | Title names the same daily-limit override as the card (the card has release null) | high |
| dev2 | multi-document-room-picker | done | 2026-09-24 | A Room whose package holds several documents lets the reviewer choose one | - | `read-artifacts` | "lets the reviewer choose one" document matches card "Switch between the review's files" | medium |
| dev2 | preview-blob-cleanup | done | 2026-09-24 | A closed pull request's deploy-preview blobs are removed | - | infra | Removes closed-PR deploy-preview blobs; no reviewer-visible outcome | high |
| dev2 | multi-document-one-round-trip | done | 2026-09-25 | A several-document Room opens in one server round trip | - | `arrive-reading` | "opens in one server round trip" matches card "Arrive at a document, not a prompt" | medium |
| dev2 | room-view-get-removal | done | 2026-09-25 | The Room handler keeps only the paths a request can reach | - | infra | Removes unreachable handler paths | high |
| dev2 | room-in-page-error-style | done | 2026-09-28 | Room errors that leave the page usable share the notice card's style | - | `in-page-errors-consistent` | "Room errors ... share the notice card's style" matches card "Errors while commenting look like every other Room error" | high |
| dev2 | owner-link-and-account | done | 2026-10-07 | My agent's link makes me the owner, and signing up keeps it on any browser | - | `auto-pair-from-link`, `sign-in-to-pair`, `result-marks-owner` | Outcome: opens the CLI link and is owner, signing up keeps it on any browser, agent tells owner feedback apart; cards "Open the link my CLI prints and I am the owner", "Sign up with WorkOS from that page", "The result says which feedback came from me" | high |
| dev2 | one-entry-account-menu | done | 2026-10-07 | One entry: the first screen asks owner or anonymous, and an account menu holds sign-out | - | `first-screen-owner-or-anonymous`, `name-follows-account` | "the first screen asks owner or anonymous" and a signed-in person keeps their account name; cards of the same names. Sign-out/switch part overlaps switch-any-account, which workos-signout covers | high |
| dev2 | device-binding-read | done | 2026-10-07 | rr can rely on the relay to say whether its device is bound | - | `browser-agent-identity` | "rr can rely on the relay to say whether its device is bound" supports card "My device becomes one way into my account"; mostly plumbing | low |
| dev2 | remove-pairing-code | done | 2026-10-07 | The relay drops the pairing-code flow nothing calls | - | infra | Drops the unused pairing-code flow | high |
| dev2 | anonymous-can-sign-in | done | 2026-10-08 | A reviewer who chose anonymous can still sign in later | - | `first-screen-owner-or-anonymous` | "A reviewer who chose anonymous can still sign in later" extends the first-screen owner-or-anonymous card | medium |
| dev2 | openapi-route-coverage | done | 2026-10-08 | Every device-authenticated relay route is in the OpenAPI, and a test refuses one that is not | - | infra | OpenAPI coverage and a refusing test | high |
| dev2 | one-identity-entry | done | 2026-10-09 | One place in the Room shows who I am | - | `one-identity-entry` | Title "One place in the Room shows who I am" equals the card | high |
| dev2 | room-anchor-context | done | 2026-10-09 | Room comments carry quote context from the Web draft | - | `repeated-text-comment-lands` | "Room comments carry quote context" so "a comment on repeated text is unique" matches the card | high |
| dev2 | owner-decision-record | done | 2026-10-09 | The relay stores a signed-in owner's decision for the agent | - | `decide-as-paired-owner`, `decision-to-agent-and-relay` | "stores a signed-in owner's decision for the agent" matches cards "Decide on the web as the paired owner" and "My decision goes back to my agent and is recorded on the relay" | high |
| dev2 | live-web-notice | done | 2026-10-10 | The Room tells me when a newer Web is live and offers a reload | - | `show-app-version` | "tells me when a newer Web is live and offers a reload" matches card "Show the current version number ... so after an update I can tell which version I am on" only partly | medium |
| dev2 | font-and-width | done | 2026-10-10 | The Room keeps my font across reviews and my wide reading view across a redraw | - | `keep-font-choice`, `wide-reading-view` | "keeps my font across reviews and my wide reading view" equals the two cards | high |
| dev2 | decision-panel-host | done | 2026-10-12 | The Room hands the owner's decision from the Web panel to the relay | - | `decide-as-paired-owner`, `decision-to-agent-and-relay` | "hands the owner's decision from the Web panel to the relay" matches both decision cards | high |
| dev2 | close-race | done | 2026-10-12 | A comment sent at the moment the owner decides is refused, not stored after the close | - | `see-briefing-closed` | "No submission is stored ... after its owner's decision" enforces card "Learn the owner has decided, so the link takes no more comments" (release advisory-and-close) | medium |
| dev2 | close-race-copilot | done | 2026-10-12 | Two decisions racing leave nothing behind, and the docs state who wins a same-instant tie | - | `see-briefing-closed` | "A refused decision stores nothing even when two decisions race" is the same closing guarantee | medium |
| dev2 | review-ui-specs-both-shells | done | 2026-10-12 | Relay's browser specs pass on both the current and the next Web shell | - | infra | Tests only | high |
| dev2 | publish-admission | done | 2026-10-12 | Only admitted devices can publish a share | `agent-front-door/publish-without-binary` | `publish-without-binary` (keep) | Already set by the FO; kept. Task is a parked record; the card is the closest | - |
| dev2 | agent-review-identity | done | 2026-10-13 | An agent's comment is kept as an agent's, with its declared name, harness and model, beside an unchanged review result | `agent-front-door/agent-reviews-from-link` | `agent-reviews-from-link` (keep) | Already set by the FO; kept | - |
| dev2 | review-ui-consistency-relay | done | 2026-10-13 | One sent signal in the Room: relay stops drawing its own after Web takes it over | - | `confirm-sent-web` | "One sent signal in the Room" matches card "See that my Web feedback was sent"; the task is a consistency cleanup | low |
| dev2 | review-ui-dialogs-specs-both-shells | done | 2026-10-13 | Relay's Room specs answer either Web's discard prompt: the browser confirm or the shell dialog | - | infra | Tests only | high |
| dev2 | agent-front-door | done | 2026-10-13 | Given only a share link or review.spacedock.md, an agent learns how to give review feedback | `agent-front-door/get-started-page` | `get-started-page` (keep) | Already set by the FO; kept | - |
| dev2 | owner-sees-all-feedback | done | 2026-10-13 | As the owner I read every reviewer's comments in the Room and decide with them | `owner-mode/owner-sees-all` | `owner-sees-all` (keep) | Already set by the FO; kept | - |
| dev2 | front-door-flag | done | 2026-10-13 | The agent front door is off unless a deploy turns it on, so staging can dogfood it while production does not serve it | `agent-front-door/get-started-page` | `get-started-page` (keep) | Already set by the FO; kept | - |
| dev2 | comment-admission | done | 2026-10-13 | Comments on a share are bounded, so a link holder cannot flood the store or the owner's results | `agent-front-door/agent-reviews-from-link` | `agent-reviews-from-link` (keep) | Already set by the FO; kept. Also serves limits-by-standing (later) | - |
| dev2 | owner-sees-all-feedback-room | done | 2026-10-13 | The owner's Room shows everyone's comments and builds includes from them, once Web draws the list | `owner-mode/owner-sees-all` | `owner-sees-all` (keep) | Already set by the FO; kept | - |
| dev2 | device-route-room-gate | done | 2026-10-13 | A comment reaches a Briefing only through a Room its owner keeps open, and a retry never spends a second slot | `agent-front-door/agent-reviews-from-link` | `agent-reviews-from-link` (keep) | Already set by the FO; kept | - |
| dev2 | limit-observability | done | 2026-10-14 | The relay counts its own limits: every refusal is logged and a daily line reports how close real traffic came | `agent-front-door/get-started-page` | `get-started-page` (keep) | Already set by the FO; kept. Weak fit: outcome is relay limit logging, not an agent front-door card; consider infra | - |
| dev2 | owner-sees-all-feedback-page | done | 2026-10-14 | The owner's Room page lists everyone's comments and sends includes from them, once relay reads the sign-in mark in production | `owner-mode/owner-sees-all` | `owner-sees-all` (keep) | Already set by the FO; kept | - |
| dev2 | agent-front-door-publish | backlog | - | Given only review.spacedock.md, an agent wanting to publish is pointed at installing Spacedock Review | `agent-front-door/get-started-page` | `get-started-page` (keep) | Already set by the FO; kept. Alt: install-publish-skill (install funnel) | - |
| dev2 | close-race-slot-log | backlog | - | Research: a numbered slot log so nothing can commit after the owner's decision, even across a crash | - | `see-briefing-closed` | Research behind the same "no comment after the owner's decision" guarantee | low |
| dev2 | dev-secrets-wrapper | backlog | - | A relay worker reaches a development secret only through one wrapper backed by a 1Password vault | - | infra | Worker secret tooling | high |
| dev2 | device-route-after-decision | validation | - | A decided Briefing takes no more feedback from the device route either | `agent-front-door/agent-reviews-from-link` | `agent-reviews-from-link` (keep) | Already set by the FO; kept. Alt: see-briefing-closed (a decided Briefing takes no more feedback) | - |
| dev2 | inbox-home | backlog | - | After signing in, a home page lists my reviews and manages my devices | `owner-account/inbox-home` | `inbox-home` (keep) | Already set by the FO; kept | - |
| dev2 | limit-telemetry-posthog | implementation | - | Relay's refusal and daily traffic lines also reach PostHog, so their history outlives the function log | - | infra | Sends refusal and traffic lines to PostHog; operator-only | high |
| dev2 | others-highlights-in-author-colour | backlog | - | Other reviewers' comments are highlighted in the document in their author's colour, and a card scrolls to its passage | - | `others-highlights-in-author-colour` | Title matches the card word for word | high |
| dev2 | owner-link-spec-hosted | backlog | - | The owner-link spec reads its control comment back on a hosted relay | - | infra | Test code only | high |
| dev2 | product-feedback-channel | backlog | - | A reviewer can send feedback about Spacedock Review itself | - | no-story: a reviewer can send feedback about Spacedock Review itself (Captain ruled it is not a journey story) | Task body quotes the Captain: feedback about the product is a different concept from a briefing | high |
| dev2 | review-ui-room-asks-through-shell | ideation | - | The Room asks its three questions through the shell, and the link pages wear Web's stylesheet | - | no-story: relay dialogs and link pages look like Web's | UI consistency; no card describes it | medium |
| dev2 | signed-in-specs-run | validation | - | The signed-in browser specs run somewhere, and the owner's comment flow passes on Web 0.2.21 | - | infra | Test scheduling | high |
| dev2 | spacedock-install-beta | validation | - | One command installs Spacedock with Review and Compass, and the Recce team runs it as a beta | `agent-publishes/install-publish-skill` | `install-publish-skill` (keep) | Already set by the FO; kept | - |
| dev2 | staging-limits-every-context | backlog | - | Every staging context the release gates use has the anonymous limits they need | - | infra | Release-gate configuration | high |
| dev2 | staging-pin-read-retry | backlog | - | A release does not fail when GitHub answers the staging pin with a stale ref | - | infra | CI workflow fix | high |
| dev2 | workos-signout | backlog | - | Signing out ends the WorkOS session, so switching account works for every sign-in method | `owner-account/switch-any-account` | `switch-any-account` (keep) | Already set by the FO; kept | - |

## subspace-relay / dev2-poc

| Workflow | Slug | Status | Completed | Title | Existing | Proposal | Reason | Conf |
|---|---|---|---|---|---|---|---|---|
| dev2-poc | pairing-owner-poc | done | 2026-10-02 | A browser pairs with my CLI device and opens my shares as the owner | - | `auto-pair-from-link` | "a browser pairs with my CLI device and opens my shares as the owner" is the code-based POC of card "Open the link my CLI prints and I am the owner, with no code to type" | medium |
| dev2-poc | account-owns-device | done | 2026-10-05 | Sign up once, and any browser I sign in on is my device's owner | - | `sign-in-to-pair`, `browser-agent-identity` | "any browser I sign in on is my device's owner" equals card "Sign up with WorkOS from that page, so any browser I sign in on is the owner" | high |
| dev2-poc | device-binding-read | done | 2026-10-07 | A device can ask the relay whether it is bound to an account | - | `browser-agent-identity` | Same task as relay dev2 device-binding-read (POC) | low |
| dev2-poc | agent-front-door-learnability | validation | - | A fresh agent given only a URL publishes, hands me the owner link, and collects feedback | `agent-front-door/publish-without-binary` | `publish-without-binary` (keep) | Already set by the FO; kept | - |
| dev2-poc | agent-front-door-skill-install | validation | - | One prompt and a URL install Review as a skill that a later session uses on its own | `agent-front-door/set-up-on-recommendation` | `set-up-on-recommendation` (keep) | Already set by the FO; kept | - |
| dev2-poc | agent-reviews-from-link | validation | - | Any agent given only a share link comments as itself, with its model, as a guest | `agent-front-door/agent-reviews-from-link` | `agent-reviews-from-link` (keep) | Already set by the FO; kept | - |
| dev2-poc | hosted-readback-empty | validation | - | Find why a comment sent on a hosted preview never reads back | - | infra | Diagnosis of whether a spec or product loses a comment on a hosted preview; no stated outcome of its own | low |
| dev2-poc | owner-link-and-mark | validation | - | My agent's link opens as mine, and my agent can tell my feedback from others | - | `auto-pair-from-link`, `result-marks-owner` | "My agent's link opens as mine, and my agent can tell my feedback from others" | high |

## subspace-v0 / dev2

| Workflow | Slug | Status | Completed | Title | Existing | Proposal | Reason | Conf |
|---|---|---|---|---|---|---|---|---|
| dev2 | quote-anchor-projection | done | 2026-10-10 | Quote anchors: one defined text projection with shared conformance cases | - | `repeated-text-comment-lands` | Shared anchor cases so a quote resolves uniquely; contract work behind card "A comment on repeated text lands where I left it" | medium |
| dev2 | rr-feedback-owner-mark | done | 2026-10-11 | rr feedback shows which feedback came from the owner | - | `result-marks-owner` | "rr feedback shows which feedback came from the owner" equals card "The result says which feedback came from me, the owner" | high |
| dev2 | rr-owner-link-and-binding | done | 2026-10-11 | rr prints my owner link, and can show and undo my device's binding | - | `auto-pair-from-link`, `browser-agent-identity` | "rr prints my owner link, and can show and undo my device's binding" | high |
| dev2 | install-gives-2-1 | done | 2026-10-11 | Installing subspace gives my agent Release 2.1 | - | `install-publish-skill` | "Installing subspace gives my agent Release 2.1" (rr skill so the agent can publish) matches card "Install the review skill so my agent can publish" | medium |
| dev2 | agent-reads-decision | done | 2026-10-12 | My agent reads the decision I made on the web | - | `decision-to-agent-and-relay` | "My agent reads the decision I made on the web" matches card "My decision goes back to my agent" | high |
| dev2 | rr-reads-cross-result-includes | done | 2026-10-13 | rr reads a decision that includes another reviewer's earlier comment in the same Briefing | - | `decide-on-reviewer-feedback`, `decision-to-agent-and-relay` | rr reads a decision that includes another reviewer's comment; cards "Read reviewers' comments in the Room and decide with them" | medium |
| dev2 | decide-after-remote-feedback | backlog | - | After taking remote comments in, the owner decides in the TUI | - | `return-to-original-decision`, `select-feedback-to-accept` | "After taking remote comments in, the owner decides in the TUI" matches card "Use or decline the advice, then return to my decision" | medium |
| dev2 | remote-comment-include | implementation | - | The owner chooses which remote comments to include, as local review already does | - | `select-feedback-to-accept` | "The owner chooses which remote comments to include" matches card "Select which feedback to accept" | high |
| dev2 | remote-review-waits-and-acts | validation | - | After a remote publish the agent waits for the owner's decision by itself, and acts on it | `owner-decides/decision-to-agent-and-relay` | `decision-to-agent-and-relay` (keep) | Already set by the FO; kept | - |
| dev2 | render-rules-projection | validation | - | Project strikethrough and CriticMarkup in Review & Gate v1 §6, and an image as no text | - | `single-tilde-strike`, `criticmarkup` | v0 half of web-render-rules: strikethrough and CriticMarkup projection | high |
| dev2 | w-caller-question | backlog | - | /w takes the agent's own review question | - | `identify-needed-decision` | "/w takes the agent's own review question" ~ card "Know what I need to decide about this material"; on hold | low |
| dev2 | w-local-review-end-to-end | validation | - | /w local review, end to end | - | `read-single-markdown`, `open-local-review`, `annotate-material`, `send-feedback-to-agent` | "/w local review, end to end": reads a Markdown file, opens locally, annotates, returns feedback; web-parity cards | high |

## subspace-web / dev2

| Workflow | Slug | Status | Completed | Title | Existing | Proposal | Reason | Conf |
|---|---|---|---|---|---|---|---|---|
| dev2 | w-plain-file-feedback | done | 2026-09-24 | Web shell produces /w's plain-file feedback | - | `send-feedback-to-agent`, `annotate-material` | "Web shell produces /w's plain-file feedback" matches card "Send my feedback back to the agent" | medium |
| dev2 | composer-number-flaky-second-selection | done | 2026-09-29 | Composer numbering test fails intermittently after a second selection | - | infra | Flaky test | high |
| dev2 | web-selection-anchor-context | done | 2026-10-08 | Web selections carry prefix and suffix, and pass the shared anchor cases | - | `repeated-text-comment-lands` | Selections carry prefix and suffix so a repeated-text comment lands | medium |
| dev2 | web-comment-comfortably | done | 2026-10-08 | Comment without fighting the page (Release 2.2d) | - | `comment-popup-on-select`, `comment-by-keyboard`, `comment-box-grows`, `panel-click-highlights` | "Comment without fighting the page (Release 2.2d)"; the body lists these four cards | high |
| dev2 | web-identity-card | done | 2026-10-08 | The reviewer card is the Room's one identity control (Release 2.2) | - | `one-identity-entry` | "The reviewer card is the Room's one identity control" | high |
| dev2 | web-bundle-version-notice | done | 2026-10-09 | Show the running Web version, and ask for a reload when a newer one is live | - | `show-app-version` | "Show the running Web version, and ask for a reload" equals the card | high |
| dev2 | web-wide-view-and-font-memory | done | 2026-10-09 | Widen the document and keep my font choice (Release 2.2c-1) | - | `wide-reading-view`, `keep-font-choice` | Title and body name both cards | high |
| dev2 | pair-gate-follows-relay-production | done | 2026-10-10 | The paired release gate tests against the relay production runs, without a re-pin per relay release | - | infra | Release-gate pinning | high |
| dev2 | web-owner-decision-panel | done | 2026-10-10 | The signed-in owner decides in the review shell (Release 2.2) | - | `decide-as-paired-owner`, `decision-to-agent-and-relay` | Body names both stories | high |
| dev2 | decision-panel-uat-polish | done | 2026-10-11 | Decision Finish that does not wrap, a composer without the quote box, and an obvious sent signal | - | `decide-as-paired-owner` | UAT polish of the owner decision panel | medium |
| dev2 | finish-sheet-redesign | done | 2026-10-12 | A Finish sheet, as the terminal review's Finish screen, replaces the decision footer | - | `decide-as-paired-owner` | The owner finishes a review on a Finish sheet; a redesign of the decision step | medium |
| dev2 | finish-sheet-backdrop-blur | done | 2026-10-12 | The page behind the Finish sheet is blurred, not only dimmed | - | `decide-as-paired-owner` | Visual polish of the same Finish sheet | low |
| dev2 | review-ui-consistency | done | 2026-10-12 | Every review surface looks like one product: inventory, then the shell supplies what relay draws itself | - | no-story: every review surface looks like one product | Cross-surface UI consistency; no card describes it | medium |
| dev2 | part-switch-loading | done | 2026-10-13 | Choosing another document shows it is loading until the new one is drawn | - | `read-artifacts` | "Choosing another document shows it is loading" relates to card "Switch between the review's files" | medium |
| dev2 | loading-tray-stays-opaque | done | 2026-10-13 | The phone feedback tray stays opaque while another document loads | - | `read-artifacts` | Polish of the same document switch on a phone | low |
| dev2 | review-ui-dialogs-and-stylesheet | done | 2026-10-13 | The shell draws every dialog, asked for by name, in the page's theme, and publishes /web/ui.css | - | no-story: shell dialogs in the page theme and /web/ui.css | UI consistency slice B; no card describes it | medium |
| dev2 | owner-sees-all-feedback | done | 2026-10-13 | A Briefing's holder sees everyone's feedback, can include it in the decision, and sees who wrote each card | - | `owner-sees-all`, `author-mark` | Existing mapping story owner-sees-all; body also builds the author mark on each card | high |
| dev2 | holder-panel-header-and-polish | implementation | - | The holder's feedback panel says what its list shows, refreshes on demand, and is polished | `owner-decides/decide-as-paired-owner` | `decide-as-paired-owner` (keep) | Already set by the FO; kept | - |
| dev2 | others-highlights-in-author-colour | backlog | - | Other reviewers' comments are highlighted in the document in their author's colour, matching the card's mark | `owner-mode/others-highlights-in-author-colour` | `others-highlights-in-author-colour` (keep) | Already set by the FO; kept | - |
| dev2 | web-draw-figures | backlog | - | Draw a document's figures in the Room and the terminal (Release 2.2c-3) | - | `rich-document-visuals` | Body names story rich-document-visuals | high |
| dev2 | web-render-rules | implementation | - | Render single-tilde strikethrough, CriticMarkup and figures as written (Release 2.2c-2) | - | `single-tilde-strike`, `criticmarkup`, `rich-document-visuals` | Body names all three stories | high |
| dev2 | webkit-on-release-pr | backlog | - | WebKit runs the browser suite on every release pull request | - | infra | CI browser matrix; related evidence for comment-across-browsers but a CI-only task | medium |
