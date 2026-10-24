# Engineering reviewer 1: kc-adr-tools-with-dev2-copy, before the ideation gate

Verdict: adjust. Nothing the Captain approved is withdrawn, and no Material finding holds the gate; the gate presentation should put D1's three costs beside D1, and the two writing.md lines are the answer to the check D1 ordered, not a known limit.

```yaml
engineering_reviewer_report:
  question: Do Captain Amendments 1 and 2 and rulings D1 to D4 withdraw anything he approved, does the cycle-2 design add anything he did not rule, is D5 framed fairly, and is there a Material finding before the ideation gate?
  revision: task file at state commit b64361b3 (cycle 2); package sources at origin/main fd630b2a (kc-dev-flow-2 0.28.0, kc-adr 0.1.1)
  conclusion: >
    No withdrawal. The only gate approval (backlog, 2026-10-23 18:26 +0800) was over state rev a26efd42, which already held
    Amendments 1 and 2. Amendment 1 narrowed his earlier 10-22 chat 「可以」 in his own words: the numbering script stays in dev2,
    and a sync script plus a CI byte compare replaces "CI copies before each release". The Scope bullet and the title ("CI-synced")
    still carry the earlier wording; that is stale text, not a live conflict. D1 to D4 were ruled while the ideation gate was open,
    so they are bound at that gate, not amendments, and the file records them that way (workflow.md § Captain amendments).
    Cycle 2 adds no scope beyond D1 to D4. It does add three consequences of D1 that he has not seen beside D1.
  material_evidence:
    - "Backlog briefing index.json: artifact uri git-root://state/a26efd42.../kc-adr-tools-with-dev2-copy.md; `git show a26efd42:` lists `### Amendment 1` and `### Amendment 2`; resolution at 2026-10-23T10:26Z."
    - "Lint exemption reproduced: origin/main archive with kc-adr/skills/read-adr copied to kc-dev-flow-2/skills/read-adr; lint-skills.py printed the four FAILs the design names (Invocation; adr_lint.py and number_guards.py named without <package>/scripts/; <package> without a Package root line)."
    - "lint_tree requires `Invocation: kc-dev-flow-2:<skill>`; kc-adr's SKILL.md cannot carry that line and stay true for kc-adr, so a byte copy cannot pass this check. The exemption is forced by D1 plus byte identity, not chosen."
    - "Compensating checks are in the same required job: marketplace-parity.yml has `pull_request:` with no `paths:` (its own comment says so), runs `Validate skill frontmatter`, and branch protection lists `version parity (plugin.json / marketplace.json / codex / README)` (gh api, 2026-10-23)."
    - "read-adr description: 77 words (`wc -w`); SKILL.md 775, writing.md 457, prefix.md 141; implementation principles.md 703. All match the design."
    - "kc-adr writing.md: 'The reserver's path is written against kc-dev-flow-2 0.28.0. Read version in <package>/.claude-plugin/plugin.json; if it differs, still use the file and report ...'. Under dev2, <package> resolves to dev2 itself."
    - "kc-dev-flow-2/skills/implementation/principles.md: 'The implementation worker writes the record into the candidate'; its ADR paragraph names only the template and adr_lint.py. The kc-adr template's `**Protects:** none` carries no instruction, and the synced linter accepts `none`."
    - "Local install (~/.claude/plugins/installed_plugins.json): kc-adr@kc-claude-plugins is already installed beside kc-dev-flow-2."
  risk_tradeoff: >
    All changes are reversible text and CI-step edits. The durable obligations are the SYNCED_SKILLS exemption (read-adr is then
    checked only by the byte compare and skill-frontmatter-lint) and the two-plugin PR shape that D4 makes permanent until
    kc-adr-dev2-sharing-better-way lands. The cheapest fix for the two writing.md lines is a kc-adr text edit. Under D4 it can ride
    the implementation PR, once the kc-adr session agrees.
  recommendation: adjust
  confidence: high on question 1; medium on question 2 (whether workers follow any pointer is unmeasured)
  disproof_condition: >
    Any of these would change the recommendation. A gate briefing for backlog whose artifact lacks Amendment 1 would turn
    question 1 into a withdrawal. A `paths:` filter on marketplace-parity.yml, or the parity context missing from protection,
    would turn D3 and AC-3 into a hold. A live dev2 worker session that follows writing.md without the report noise would retire F2c.
  authority_boundary: >
    The Captain owns the ideation gate and whether D1 still stands at these costs. The kc-adr session owns kc-adr's text. FO owns
    the gate presentation and the routing. This report is advisory: it grants no state change, scope change or merge.
```

## Findings

**F1. Nothing approved is withdrawn; D1 to D4 are correctly gate-bound.** The 10-22 「可以」 said kc-adr owns "the ADR part of numbering" and that "CI copies them". Amendment 1 changes both, but it is his own 「ADR 工具要改用 kc-adr 那邊轉述的縮小版」, and the backlog approval came after it, over a seed that contained it. The Scope bullet and the title still use the 10-22 wording. A later reader may trip on that, but no approved commitment is lost. Every other Scope item is kept: one install, adopter README paths unchanged, the two-host copied-directory test run first, the reservation owner named (dev2).

**F2. D1 was conditional, and its three costs are the evidence for that condition. Present them beside D1, not as unruled side effects.** His words were 「除非有更好的做法…或是，除非這個 read-adr 技能對 dev2 沒用」.
- a. Lint exemption: forced, not a design choice (see evidence). A narrow named set, plus a negative test (AC-6), is the right shape. It needs no ruling of its own, but he should see that the folder leaves dev2's own lint.
- b. +78 words per session for every dev2 user. On this machine kc-adr is already installed, so the Captain's own sessions get a second identical listing (156 words). This is the price of D1; show the number with it.
- c. The two writing.md lines are the answer to the check D1 itself ordered ("whether its text names kc-adr paths that a byte copy cannot carry"). The design files them under "Known limits (not decisions)", which undersells them. The version line is not occasional. The copy can only ship in a dev2 release after 0.28.0, so from its first release every dev2 worker that follows writing.md reports "written against 0.28.0, found X". That is a standing false alarm in reports FO reads. It also stales kc-adr's own text on every dev2 release, independent of this task. Recommended route: FO asks the kc-adr session to make both lines host-neutral before the sync (for example, drop the version pin, and say `${CLAUDE_PLUGIN_ROOT}` is this plugin's root, which is kc-dev-flow-2's only when this copy ships inside it). Under D4 that edit can ride the implementation PR.
- Consumer evidence is thin and should be said plainly. The one dev2 consumer found is design-director's "ADR folder" section, and it already degrades to `adrs_read: unavailable`. The other two consumers the ruling named (the AGENTS.md pointer, new-work-checks-what-exists-first) were not found. With D2, the copied skill gains a second purpose: carrying the Protects rule. That purpose only works through D5 (F3).

**F3. D5 is fair and is not a re-run of D2, with one asymmetry to fix and one coupling to state.** It is not a re-run because D2 forbade hand-writing the rule; a pointer holds no rule text, AC-5's grep still passes, and read-adr's own "One home" bullet prescribes pointers. The asymmetry: "If you say no … the rule's reach to workers is unmeasured, not proved" implies that yes proves it. It does not: no AC checks a worker following the pointer (AC-9 counts words only, and no live session ran). The coupling: the implementation worker writes the ADR. Without D5 it gets the `**Protects:** none` label from the template and the linter accepts `none`, so nothing in its path asks it to list files or plant pointers. D2's premise, that the rule "arrives with the copied skill", reaches the worker only through D5 or a chance load from the skill description. State that D2 and D5 are coupled, per the one-decision rule's exception. A cheaper variant: put the pointer into the existing ADR sentence ("…in the ADR format of … `references/adr-template.md`") instead of adding a new sentence.

**F4. D4 contradicts a repo-wide rule the design does not name; the release behavior is untested.** Root `CLAUDE.md` on origin/main: "A feature PR touches only its plugin's files (`<plugin>/**`)". D4 makes every kc-adr tool change a two-plugin PR, and the implementation PR also touches `scripts/` and `.github/`. The compare's failure message already tells the author to commit both plugins, so nothing breaks without a CLAUDE.md line. Name the exception in the Batch overlap and the PR body, and let Kent decide whether CLAUDE.md gets a line. Separately, D4's "released with the next dev2 version" relies on release-please bumping both components for a single-scope squash title. The design says "not run here". AC-8 proves install propagation with hand-bumped sandbox versions, not release-please attribution. Record that as a residual or test it with the pinned release-please fixture that version-parity-check.sh already runs.

No Material finding holds the ideation gate. D3 and AC-3's "runs on every PR" claim checks out against the workflow file and branch protection.
