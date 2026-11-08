# Implementation evidence

Candidate: b36fbeeec3a6699c0a82a021dc4ee0142410f6c8
Base: 139feeaee7ce037a0c6535568cd6bd103155cbae
Product branch: spacedock-ensign/observer-lists-unasked-merges

The four product files are pinned by SHA-256 in identity.json. The local candidate is committed; product publication, Draft PR creation, RoboRev, hosted CI, validation and merge remain with FO.

- replay-live.log is the actual GitHub replay, exit 1 as expected for eight record gaps. It reports 54 carried of 82.
- snapshot.py replays the saved ideation PR input against committed local state refs. It checks every AC-1 set and isolates #727 before and after a head change. It does not refresh the remote.
- mutate.py creates empty temporary directories, runs Python with -B and PYTHONDONTWRITEBYTECODE, runs all 17 baseline tests, and requires each of five deliberately broken implementations to fail its behavioral test. A release-removal replay also exposes #707.
- observer-candidate-final.md is the unedited native observer report after verification of the committed candidate; observer-base.md is the published 0.35.0 native control. base-control.json binds that control's skill bytes to the published tag. observer-candidate.md is an earlier preparatory run.
- recount.py independently renders the landed line forms over window-manifest.json's exact 54 archive revisions. The counter uses the saved 92-PR fixture and simulates earlier verbatim reports chronologically: median +60, maximum +320 words; without collapse maximum +422. This is the approved line-form simulation, not a measurement of every word in a live model's full report. The manifest avoids date-only Git filters whose time-of-day changes the corpus.
- suite-summary.json and suite/ hold the 27 successful local commands, including 1,199 unittest cases with 11 skips. The dispatch replay used the 0.27.2 CLI with installed 0.27.3 plugin files; it does not substitute for hosted CI's pinned installation.
- acceptance/ and acceptance.log are the successful fresh-shell run. The harness was corrected to pin the original window corpus after a date-only filter selected 56 instead of 54 windows across midnight; product bytes did not change.
- doc-impact.json lists only kc-dev-flow-2/README.md; unaffected: its instruction to run the named CI test commands remains accurate because the new test is wired into that workflow.
- pr.md mirrors /tmp/impl-observer-lists-unasked-merges-pr.md for FO. Cost per PR was not measured; the existing path triggers and job are unchanged.

Reproduce the deterministic checks in a fresh shell, supplying the absolute code checkout, state checkout, installed kc-dev-flow-2 package and an output directory:

```bash
bash --noprofile --norc <this-folder>/acceptance.sh <code-root> <state-root> <package-root> <output-directory>
```

For a fresh live provider read, run the candidate's merge_audit.py against the task and revision specified in AC-1. Its state-ref fetch is the sole intended Git write. The deterministic harness deliberately uses the saved GitHub input; it does not claim a new live query.
