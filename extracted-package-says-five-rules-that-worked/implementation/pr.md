Title: docs(workflow): say five rules that worked by hand, each once, where its reader loads it

The package's workflow text now says five rules that were followed by hand and worked, each once in the section its reader loads: a first report to the Captain within about ten minutes; elapsed and budget minutes on every task message; a stop before a third dispatch in one stage, naming the shared assumption, with the default of keeping results and reporting remaining work; relayed words are not a ruling; each criterion's `Verified by:` links the run made during design.

## Finding, not a fix

The word lint counts `references/sd/workflow.md` alone: +86 words there. What the First Officer loads grows by 34, because the peers extension (-14) and the dev skill (-38) lose copies of lines the new text now carries. The lint's raise step is +86 and its captain field quotes the Captain's word 「那句話放回去，接受 FO 多讀 34 字。」, which is the 34.

Per reader (`wc -w` over the First Officer file list; `spacedock dispatch show-stage-def | wc -w` per stage), base 7e0f9c2 to candidate:

| Reader | Base | Candidate | Change |
| --- | --- | --- | --- |
| Workflow text (lint) | 6113 | 6199 | +86 |
| First Officer | 11722 | 11756 | +34 |
| Ideation worker | 694 | 724 | +30 |
| Implementation worker | 1371 | 1398 | +27 |
| Validation worker | 1525 | 1552 | +27 |

## Which branch

Candidate: branch `five-rules-restore-default`, commit 17a4ff1 (three commits on base 7e0f9c2: cff6d61, 728cb8d, 17a4ff1). Not proposed: branch `five-rules` (cff6d61), which is +21 for the First Officer but loses one behaviour the base had: in the fresh-reader scenario where a third dispatch is refused, its answer brings neither the kept results nor the remaining work (0 of 3 runs; base 3 of 3). The restored sentence brings both back (3 of 3).

Also in this change: `OUTCOMES.zh.md` outcome 四 now says both halves of the rule are in the package text.

## Known limits

- The three worth answers at a budget hold appear in no arm, base included, because they exist only in script output the reader files do not hold. The base shows no such behaviour to lose, and the candidate shows none to gain.
- The readers were single runs per role on a smaller model and an older Claude Code on the clean host (claude-sonnet-5-5, Claude Code 2.1.311), files given explicitly and no skills. Only the lost-and-restored scenario was repeated (three runs per arm). Run-to-run variation, other hosts, other stage workers and live behaviour under load are not shown. The worker scenarios were not run on the candidate: the restored sentence is in Schema, which no stage definition inlines.
- The word lint counts the workflow text alone, so its +86 is not the reader's growth; the First Officer's +34 is.

## Not done

No test asserting the text contains words, no new script, no change to the three profiles. The first-report trace for the scoreboard is not built; minutes to the first report stay not recorded. roborev not run: this repository is not covered by the review daemon.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
