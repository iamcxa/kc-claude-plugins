# Engineering reviewer 1: design-director-runs-ui-design-review, ideation

Verdict: adjust. The design withdraws nothing the Captain approved. It adds one refusing check at validation that it does not name as a decision. The Captain's list of upheld declines relies on an FO behaviour that the recorded briefings do not show. The replay supports a narrower claim than the summary makes. D-1 asks for a hand trial that has already been run, and it does not say that the Captain's own complaint stays closed under this design.

```yaml
engineering_reviewer_report:
  question: >
    Do Amendment 1 and the backlog gate resolution survive into the ideation design
    unwithdrawn and without unnamed additions; does the replay support the duty-wording
    claim; is an Amended paragraph on ADR 0022 sound; are D-1 to D-4 framed fairly?
  revision: >
    Task file design-director-runs-ui-design-review.md in the dev2 state checkout
    (worktree HEAD c27e7659), its replay/ and intake/ folders, backlog briefing
    a26c4da3; package source kc-dev-flow-2 0.27.0 cache and origin/main e1f43044.
  conclusion: >
    All approved items are present: the named role on sonnet; no decline closes without
    a director ruling; upheld declines listed for the Captain, who keeps the final say;
    two passes with hand-forward; host-component declines checked against the
    declaration; a replay now and a replay of the shipped agent in AC-7. Nothing is
    withdrawn. Four changes are needed before the gate. First, name the validation
    refusal as a decision and close its preview-file hole. Second, prove that the
    upheld list reaches the gate material. Third, bound the replay claim to "a second
    sonnet check with the declarations", not "the wording". Fourth, reframe D-1 around
    the hand run that already exists and around critique row 1. ADR route: an Amended
    paragraph is an accepted form here, but it is undersized for this change.
  material_evidence:
    - Ruling tally of replay/out/*.yaml is 31 overruled, 18 decision and 21 upheld (70). run2-rulings.tsv has 39 rows with 4 disagreements. Both match the design.
    - All 7 prompts carry "treat the two declaration files above as the declaration path for every host component", which waives the path rule. The task body does not state this waiver.
    - The critique ux-review-r1.5/index.html (read-only) grades rows 1 to 4 blocking. The measurement maps 1, 2 and 4 to per-task findings that were raised and declined. Row 3 needed a running app.
    - Past paseo ideation briefings (_archive/*/review/ideation/briefing-1/index.json) carry a question and a one-line summary. None carries checker output.
    - workflow.md Gate content puts "FO includes the checker's output" in the same sentence as "a non-zero exit means the gate is not presentable".
    - adr_lint.py checks sections, status and the Words/Options/Recommended labels. It does not parse Amended paragraphs. ADRs 0002 and 0004 hold Amended paragraphs. ADR 0019 (ideation security review) left the validation review to a separate ADR, 0021.
  risk_tradeoff: >
    Everything here is reversible: prose plus a script check, on one release. The
    durable risks are a validation refusal the Captain did not choose, and a promise
    he did approve ("listed for him") that could fail silently. Cheapest fix for both:
    name the validation check as D-5 (or tie it to the 「可以」 words explicitly), and
    extend AC-3 so the upheld lines must appear in the ideation briefing that FO
    prepares.
  recommendation: adjust
  confidence: medium
  disproof_condition: >
    (a) A no-wording control run of the 7 prompts falls outside 10 to 35 upheld, or
    reaches 2 or fewer of the 5 rows. The wording-specific claim would then stand.
    (b) The Captain reads 「可以」 as accepting a refusing check at every pass.
    Finding 1 would then dissolve. (c) FO's chat presentation, not the briefing
    record, is shown to carry exit-0 checker output. Finding 2 would then weaken.
  authority_boundary: >
    The Captain owns D-1 to D-4, any new D-5, and the ADR route. FO owns the
    alignment record and gate prepare. This report is advisory and changes no state.
```

## Findings

### 1. Approved scope is intact, but the validation refusal is an unnamed addition and has a hole

What the Captain approved at validation was that the director "reviews screenshots of the built screen" (Amendment 1 point 3; backlog question "two passes"). The design turns this into a hard refusal, `built screen review not run` (AC-6). Under that check, 4 of the 7 past paseo validations would have failed (measurement intake). This is a new gate at a stage that ADR 0022 does not cover. It sits in a table row and is not a decision for the Captain.

The check also has a hole. It requires only that the report's `preview:` names "a screenshot file present in the task folder". The ideation previews (`design/*.png`) are already in that folder, so a validation report that points at an ideation picture passes without any built screen. Fix: require a file that is not one of the task's `Preview:` paths (or require a separate folder), and add that mutant to AC-6.

One smaller unnamed policy: at validation "a MINOR is Polish unless those fields say otherwise". Recorded MINOR declines are where the measured loss happened (70 of 93), and this default lets a MINOR drop at validation with no second look.

### 2. The Captain's list rests on an FO behaviour the record does not show

The design says "FO already includes the checker's output in the gate material, so the Captain's list needs no README rule." In `workflow.md` that clause shares a sentence with the non-zero-exit case. The upheld lines print on exit 0. The archived ideation briefings for these same paseo tasks hold no checker output, only "Ideation design for … in the task file". AC-5 proves that the checker prints the lines. AC-3 proves that a run prints them. No criterion proves that they reach the gate. This is the one approved promise ("listed for him at the design gate") whose delivery is untested end to end. Fix: extend AC-3 so the prepared ideation briefing must contain every `upheld decline <n>:` line. Otherwise state the README rule it needs and the word cost of that rule.

### 3. The replay supports "a second sonnet check with the declarations moves declines". It does not support "the duty wording does".

The counts are verified (31/18/21, and 35 of 39 agree). Three limits are not stated or not weighed:
- **No control arm.** The baseline is "no second check". The treatment adds three things at once: a second reviewer, the host `.d.ts` files, and the wording. Between 15 (strictly prop, slot or `children`) and 28 (any mention of the declaration) of the 31 overrules cite the declaration, so the files may be doing most of the work. AC-7's falsifier names a no-wording agent, but that agent was never run. With 10 to 35 upheld as the bound, a plain "check these declines against the declarations" prompt could land inside it, so AC-7 cannot tell the wording apart from the mechanism. The research intake itself finds no evidence that role wording changes what a reviewer notices.
- **Undisclosed waiver.** Every prompt waived the `<Name> at <path>` rule. Real authors wrote no paths, so under the shipped wording the 37 of 70 declines that cite a host component (the measurement's keyword count) would start as `decision` until authors adopt the form. The 31/18 split, and the Load paragraph, describe compliant authors.
- **"5 of 9" is soft at the edges and empty in the blocking class.** Robust: #5, #9b, #10. Row #4 goes to the same owner the author named (T5); only its printing as Needs decision changes. Row #12 is reached through a secondary finding while its primary stays upheld. None of the four blocking rows reaches a fix. Precision (whether the 31 overrules are right) is not graded.

None of this blocks the build: the Captain approved the check structure, not a particular wording. The fix is to restate the claim at its true scope, disclose the waiver, and run the no-wording control in AC-7 (about 619k tokens at the replay's own measure).

### 4. ADR 0022: an Amended paragraph is an accepted form, but undersized here

For: Amended paragraphs on 0002 (three) and 0004 are precedent, the topic is the same, and adr_lint does not object.

Against:
- The change reverses an option 0022 explicitly rejected ("a new agent or extension — not chosen").
- It replaces the chosen option's agent and its "reads no other file" rule.
- It moves decline authority away from the worker.
- It adds a validation-stage refusal, which 0022 never covered. The repository's nearest precedent split ideation (0019) from validation (0021).
- The reopen clause it cites ("a bite recurs that the review did not name") does not literally fire: the review named 10 of 14, and the defect is in disposition.
- adr_lint cannot check an Amended paragraph. `--since` passes on 0022's old `**Recommended:**` line, so AC-9's falsifier ("exits 1 on a malformed Amended paragraph") is false.
- A new record would get lint-enforced Words, Options considered (wordings A/B/C, the dropped astra helper, D-1) and Recommended lines.

Suggestion for the author to weigh: a new ADR for the decline authority and the validation pass, with a one-line Amended pointer in 0022. At minimum, replace AC-9's falsifier with one that can fail.

### 5. D-1 is framed unfairly in two ways

First, a premise correction for the question as posed. Per-task reviews did see three of the peer's four blocking problems (rows 1, 2 and 4, all at MINOR) and the authors declined them. Only row 3 (the resize that loses the draft) was outside every brief.

Second, the design's own table shows that row 1 is the Captain's own complaint (「我按 broswe 沒料到…」) and that the new wording upholds its decline in both runs. This fact is in a table row and in "Reading". It is not in the PRFAQ or in D-1. The Captain should read at the top that the approved design would not have caught the complaint that prompted it, and that of the four blocking rows only #4 moves, and only to a decision.

Third, D-1 recommends "run it once by hand first … and decide from what it finds". That trial has already run: the r1.5 critique is an operated, whole-screen walk on an isolated Paseo, and it found four blocking problems after six task gates had passed. The live question is whether that walk becomes a stage, and whether it belongs to this task or to release-acceptance. The release-acceptance collision rests on other tasks' tables and was not read; the design should say so. D-2 to D-4 are framed fairly. D-4 should note that an author can route every `overruled` ruling to `Needs decision`, and nothing bounds that load.

## Notes (not findings)

- Line 59 and the Summary say `## FO alignment` has no `Result:` line, but line 50 now has one. That stale text is headed for the gate.
- The figure "23 of 31 overrules cite a prop, slot or children" depends on what counts as a citation: 15 under the strict reading, 28 under the broad one. Give the definition, or give the range.
