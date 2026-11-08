# Independent engineering review: unattended browser default

```yaml
engineering_reviewer_report:
  question: Does PR 810 support making Paseo the default for local browser checks a worker runs with nobody watching?
  revision: 90192bb64db4614de9a7a94cc782ee5fa44748db
  base: 139feeaee7ce037a0c6535568cd6bd103155cbae
  conclusion: Narrow the default to attended pages, including human verification during login; retain the limits and fallback guidance. The evidence does not support requiring an unattended worker to try Paseo first.
  material_evidence:
    - The motivating QNow login walk was attended; the base already routes that category to Paseo where the extension is listed.
    - The first unhinted worker selected Paseo but completed screenshots and interaction through the repository adapter after Paseo failures.
    - The successful second run explicitly named Paseo tools and provided time for the Captain to bring the tab to the front.
    - The final visibility sentence states a condition but supplies no demonstrated unattended way to establish it.
  risk_tradeoff: Narrowing avoids an unsupported first attempt and possible human-intervention dependency, while foregoing a common unattended Paseo default that might work on other hosts. Keep useful attended-use guidance; no runtime repair is indicated by this review.
  recommendation: adjust
  confidence: high
  disproof_condition: A fresh worker, given the candidate dispatch pointer without tool hints, completes the real screenshot and click check without a person opening or focusing its browser, using a supported documented way to satisfy visibility and recording cleanup and tool provenance.
  authority_boundary: The Captain retains the scope and acceptance decision; the First Officer retains orchestration, publication, review gates and cleanup. This report changes neither the task nor its acceptance criteria.
```

Reviewed on 2026-11-08. This is a read-only assessment of the supplied artifacts, not a new browser run or a replacement validation verdict.

## Evidence locations and revision boundary

All citations below name a file and an exact, searchable phrase, without line numbers.

- Product checkout: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-browser-checks-use-paseo-browser`. Product paths below are relative to this checkout. Its branch is `spacedock-ensign/worker-browser-checks-use-paseo-browser`; its HEAD matches the candidate above, and its working tree was clean when inspected.
- Task record: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/worker-browser-checks-use-paseo-browser.md`.
- Task folder: the same path without `.md`. Paths beginning `implementation/`, `validation/` or `review/` are relative to that folder.
- Base citations were read with `git show` at the full base revision above. Both recorded browser runs name `20eb8255daf0f1267a8c0dd16daf0705a7cf82ba`. Comparing that commit with the final candidate shows only the added visible-tab sentence in `browser.md`; the `kc-journey-map` product bytes are unchanged. Neither run is a fresh execution of the final guide.

I read both saved prompts, both complete saved activity payloads, both reports including the first report's correction, the validation report, and the task's Scope, FAQ, design and acceptance clauses. I inspected the four saved before/after images. The activity payloads abbreviate some shell commands and do not expose every raw tool response; error details and visibility results are therefore attributed to the workers' reports, cross-checked against the recorded call sequences and images. I did not independently attest the historical server process or dependencies.

## 1. The stated bite is an attended authentication case, already covered in kind by base

The task record's Scope says: **"on qnow staging and production, headed agent-browser stayed stuck on Clerk's Cloudflare Turnstile twice and the Captain's manual pass in that window failed too; the Paseo browser passed it and covered a full walk the Captain watched live."** Clerk is the login service; Cloudflare Turnstile is its human-verification challenge. This was QNow, the adopter application, on staging and production with the Captain present. It was not an unattended localhost canvas check. The record explicitly attributes it to the QNow First Officer's **"first-hand report, 2026-11-06, not re-run here"**; this review does not convert that report into a new reproduction.

Base `kc-dev-flow-2/extensions/paseo/EXTENSION.md`, under Human terminals and pages, already says: **"For an attended terminal or page in a workflow listing paseo, FO and workers use Paseo when available."** It also directs **"each worker needing human interaction"** to that section and says **"Preserve sign-in and confirmation boundaries"**. Thus the base already routes the motivating *category* to Paseo, conditional on extension adoption and availability.

That condition matters: the task record's FAQ says QNow had already changed its browser rule **"without listing paseo"**, and its design says **"only kc-claude-plugins dev2 lists paseo"**. Those are the task's recorded adopter facts, not a new live audit of QNow. Under those facts, base does not automatically govern QNow, and the proposed package default does not fix that adoption gap either. The task also excludes **"editing any adopter's AGENTS.md"**. It would be inaccurate either to claim base already applied to that particular QNow workflow or to justify a general unattended default as necessary to route an attended page in a workflow that already lists Paseo.

## 2. Candidate requires a Paseo-first route; run 1 demonstrates selection and fallback, not unattended completion

Candidate `kc-dev-flow-2/extensions/paseo/EXTENSION.md` adds: **"For a local browser check you drive yourself, first read extensions/paseo/browser.md under your Package root."** The new guide then says: **"For a local browser check you drive yourself, use Paseo's browser tools (`mcp__paseo__browser_*`) unless the repository's own instructions name another tool for that check."** This applies without anyone watching. It preserves repository-specific tool instructions and unchanged CI; it is a written instruction, not a mechanical enforcement gate.

The guide acknowledges **"Tabs open in the background"**, yet now requires **"Keep the tab visible in the Paseo app for screenshots and clicks."** If tools are missing or cannot perform a step after the workaround, it says **"use the repository's supported adapter for that step"** and **"A step no browser ran is reported as not run, never clean."** The fallback is useful and prevents a failed Paseo step from being presented as successful. It does not establish why a worker without an audience should be required to enter that route first, or how that worker makes the page visible.

Run 1's `implementation/claude-prompt.txt` copies the scope-note pointer, then asks the worker to **"renders its journey board and that one existing control responds to a real click"**. The actual check request does not name a browser tool. In `implementation/claude-activity.json`, the worker says **"I'll read the browser.md file"**, then records opening and snapshotting a Paseo tab, four screenshot calls, a DOM evaluation, a ref-based click attempt and closing that tab. Its report, `implementation/claude-report.md`, records **"isActive=false"** and concludes **"The default Paseo browser path did NOT complete the check."**

The report's appended correction is decisive for the count: **"The actual count is four `mcp__paseo__browser_screenshot` calls, all failed, none produced an image"**. It records three `screenshot_no_frame` results and one 15-second timeout; evaluation and clicking also timed out. The saved activity independently contains four `[Take screenshot]` entries. Its worker observation **"I'm checking whether there's any way to activate it, and I don't have a tool for that"** is evidence of this worker's capability gap, not proof that every Paseo host lacks an activation method.

The same report says **"Open, screenshot, click, screenshot, snapshot | agent-browser CLI (session wbc-claude) | all ok"**. The saved images show the journey board and then its Story map page-selector menu open. The activity records the change and closing the fallback session. This is evidence that the candidate induced the initial Paseo choice and the fallback completed this local check. It is not evidence that Paseo completed it unattended. The report's explanation that the tab never painted is an observation; background throttling as the root cause remains a hypothesis.

**Under base:** Human terminals and pages would not trigger for a worker checking alone, and the scope-note quote has no browser-guide pointer. The task record's design itself says that section **"covers attended pages only"** and the package has **"no agent-browser or Chrome for Testing rule"**. Base therefore leaves the tool choice to repository guidance and available adapters; it does not require a failed Paseo attempt before using the documented `agent-browser` adapter. Base `kc-journey-map/README.md` lists **"`agent-browser` on PATH"** for **"PNG export"** and **"`.tldr` export"**. That is a supported dependency, not a general mandate for every interactive check. The precise base counterfactual is consequently *could use that adapter directly*, not *a base worker was observed doing so* or *base forces agent-browser*. No base-run comparison was supplied.

## 3. Narrow the default and keep the useful limits

**Supported option: narrow.** Retain Paseo for attended pages, including logins where a person performs verification, subject to the existing Human terminals and pages conditions. Keep the four original limits and their workarounds, plus the observed visibility caveat and honest fallback reporting. Do not require a Paseo-first attempt for unattended local checks.

The positive evidence is real but bounded. `implementation/attempt-2/claude-prompt.txt` says **"the Captain has this workspace open"**, **"Your first browser action MUST be browser_new_tab"**, and **"so he can bring the tab to the front"**. It also explicitly forbids fallback. The activity records two waits, visibility evaluation, a snapshot, two screenshots and **"minimap toggle at @e34"** for the minimap click. The report records **"visibilityState \"visible\""**, and the before/after PNGs show the minimap opening. That supports Paseo operation in the arranged foreground setting; it does not test self-selection or establishing visibility without human help.

The independent `validation/report.md` correctly says **"the only unhinted run failed the Paseo screenshot/click path; the only complete Paseo run had explicit tool instructions"** and marks the fourth acceptance criterion, the unhinted complete walk, **"NOT MET AS WRITTEN"**. My additional judgment is about suitability of the default: even an unhinted *attended* rerun would not establish the unattended behavior asked about here. The validator's statement **"base has no self-driven worker pointer/guide"** establishes that the route is new; absence of that route does not establish its necessity for an attended-login bite or its fitness for unattended checks.

### Concrete proposed text changes, not applied

In `kc-dev-flow-2/extensions/paseo/EXTENSION.md`, replace only the new final sentence of the Workers through Paseo scope-note quote with:

> Before using Paseo's browser tools, read extensions/paseo/browser.md under your Package root.

In `kc-dev-flow-2/extensions/paseo/browser.md`, replace the opening sentence quoted in answer 2 with:

> For attended pages, follow EXTENSION.md's Human terminals and pages; repository instructions take precedence. Unattended checks use the repository's supported adapter without a required Paseo attempt.

Keep the existing CI sentence, workspace/host placement, cleanup, fallback/reporting paragraph and all limit bullets. This makes the guide conditional on actual Paseo use and removes the unsupported first attempt without introducing a universal agent-browser mandate. The attended-page reference includes the base's sign-in and human-confirmation boundaries; it is not an instruction to automate or bypass a human-verification challenge.

The four original limits remain: keyboard/input-method interference and native value-setting workaround; React Native web buttons and fresh snapshot refs; long JavaScript evaluation and start/store/poll workaround; untested signature drawing with a trial and adapter fallback. Their provenance remains the task's reported observations and limited ideation probe. These runs did not reproduce all four, and the signature case must remain explicitly untested.

Changing the default also changes the approved proposition and fourth acceptance criterion. The First Officer should present this recommendation for the Captain's decision and route any authorized revision through the existing workflow. Do not silently rewrite the task, waive its current criterion, or count the two runs as one qualifying run. The validation report's **"responsibility for the hinted rerun is FO's"** should remain attributed accordingly; no implementer failure or runtime repair is inferred.

### Tradeoff and what remains unsettled

Keeping the broad default would make the observed unsuccessful first route the normal entry for unattended checks, with retries, fallback work or a possible request for someone to focus the tab. The final visibility sentence documents that dependency but does not demonstrate a way for an unattended worker to satisfy it. Dropping the whole change would lose useful attended-use limits and reporting guidance. Narrowing is the cheapest credible alternative: preserve those additions without extending the default beyond the supported case. Its cost is foregoing a standardized unattended Paseo route that may work in other environments.

The evidence does not settle whether another host, a supported automatic focus mechanism, or a later browser implementation can complete the same task unattended; whether visibility alone caused the first failure or guaranteed the second success; whether Paseo is generally better for authentication; or whether Codex workers can complete the canvas check merely because a tool-list probe succeeded. It supplies neither comparative reliability rates nor a measured time/cost advantage. The local canvas has no Clerk/Turnstile login. The second run proves a focused local interaction, not a reproduction of the original QNow authentication result.

A fresh, unhinted, genuinely unattended run that satisfies the final guide's visibility condition without human intervention would change this recommendation for the demonstrated host. Broader default claims would still need appropriately scoped evidence. No such run is authorized or performed by this review. The decision and any rerun remain with the Captain and First Officer; current approval, publication, retained browser/server cleanup and live task status are not cleared by this report.
