# Interview round 3: the design director (2026-10-28)

Asked by: the dev2 package FO, under the Captain's ruling of 2026-10-26 (「由你直接問」). Prompted by the Captain (chat, 2026-10-28): 「現在有沒有需要手動訪談其他fo？特別是哪時候派設計總監，哪時候 FO 自己看可以兼顧嚴謹跟效率？或是怎樣可以加快設計總監腳步，例如減少 reasoning 程度，或是限制時間？」

## Records first

A Claude sonnet subagent scanned five adopter state checkouts and their Claude Code transcripts (2026-10-28; working files in /tmp/ddscan, not kept). FO re-ran the run-time medians from its inv3.json and they matched; its total of 6.3 h recomputed as 7.26 h of wall time over 160 runs.

- 160 design director runs, 2026-10-19 to 10-28: web 14 tasks, kc-paseo-plugins (project-env) 22, relay 8, v0 1, qnow free-form 1.
- Model: 158 runs Claude sonnet 5.5 (the declared tier), 2 qnow runs Opus 5.5.
- Median wall time by pass: 1a 96 s, 1b 88 s, 2a 133 s, 2b 60 s, 3 about 313 s (2 runs). Pictures are read one per model turn; generation is about 85% of wall time in 1a and 2a.
- Share of stage time, one task (web sidebar-head): 6.4 of 65.7 min of ideation, 3.6 of 21 min of validation.
- Ideation findings (last review per task): 485; 31% fixed or turned into criteria, 63% declined by the author, the rest decisions. Declines overruled by the director: 24 of 181 rulings.
- Built-screen review (2a), last run per task, findings that changed something: web 6 of 63, relay 1 of 11, project-env 0 of 24.
- Not measurable from records: whether FO, the author or the validator had already raised the same finding.

## Questions sent

To the web, relay and project-env FOs, each anchored on that repo's recorded events:
1. One run that found what nobody else had, and one that added nothing.
2. Were the declined findings mostly noise, or real points fair to defer?
3. If FO could skip the director, for which tasks, and for which must it always run?
4. What slowed you most: the run, the decline round, or the repair cycles its findings caused?

## Answers

### subspace-web and v0 FO (Paseo 295b873d), 2026-10-28

1. Found new: web-serves-formats-list validation 2026-10-23 (chevron-less phone toggle); app-frame-contrasts-with-document ideation 2026-10-28 (8 findings, 2 fixed, 5 into criteria; the undrawn-states list behind AC-8 believed to come from it, yaml not re-read). Added nothing: sidebar-head-stays-level-after-send validation 2026-10-28 (4 MINOR, all identical on main, declined and upheld); frame-reaches-window-bottom validation round 2 (no findings). Missed: frame-reaches-window-bottom validation round 1 pass 2a did not see a 14 px edge fade over the scroll thumb; the validator found it by measuring pixels.
2. Mostly real but not the task's (base build "identical on main"), plus a few taste calls; fair to defer. Few pure-noise declines seen; not counted.
3. Skip for test-only or CI repairs, for validation rounds with product bytes unchanged since the last pass 2a, and for Visible change: none. Always run at ideation when a screen is new or changes, and the first pass 2a of a ui change on the real page. "Built screen matches the approved preview" is a weak skip reason: matching is what 2a establishes.
4. The run is cheap. The cost is the decline round's bookkeeping (design_surfaces needs a single `preview:` path; a decline check fails if the latest review does not list the decline; declines carried as prose), then re-runs after a redraw (most of review-page-polish-on-the-real-page's 44 min believed to be repeated 1a after redraws; split not known).

### kc-paseo-plugins (project-env) FO (Paseo 8b2c2fc2), 2026-10-28

1. Found new: project-env-docs-site ideation cycle 2, 2026-10-28 (ideation-3.yaml MAJOR: nothing told a new teammate how to sign in to the 1Password CLI; author, FO and validator had missed it; became Install steps 3a to 3c); pick-repository finding 1 (no way back after adding a repo, became AC-2); docs-site findings 3 and 7 (host-look, led the Captain to change theme). Added nothing: project-env-vault-change-repoints-refs built-screen review 2026-10-25 (2 MINOR, declined as already ruled); project-env-built-in-agent-notice built-screen review 2026-10-26 (4 MINOR, all declined).
2. Mostly fair to defer, not noise: host components the plugin cannot change (SettingsRow, SettingsSelect, the host's Back line), earlier Captain rulings, things scoped out. Pure taste rare. Each still costs a written decline and a 1b/2b ruling.
3. Skip for wording the Captain already worded, a repair cycle touching no client file (already skipped docs-site validation-2 built review), and a built screen whose pictures match the approved previews with a logic-only diff. Always run for a new screen or screen state, anything public (the docs site), and any picture the Captain sees for the first time at a gate.
4. The run is not the cost; the decline round and its bookkeeping are (writing declines, 1b/2b rulings, preview-path fixes for design_surfaces.py, overruled declines turned into fixes, criteria or decisions). Its findings caused about two extra cycles, both judged worth it. Wall time per round not measured.

(relay pending: its FO was busy at send time)
