Title: docs(workflow): say five rules that worked by hand, each once, where its reader loads it

The package's workflow text now says five rules that were followed by hand and worked, each once in the section its reader loads: a first report to the Captain within about ten minutes; elapsed and budget minutes on every task message; a stop before a third dispatch in one stage, naming the shared assumption; relayed words are not a ruling; each criterion's `Verified by:` links the run made during design.

## Finding, not a fix

The word lint counts `references/sd/workflow.md` alone: +73 words there. What the First Officer loads grows by 21, because the peers extension (-14) and the dev skill (-38) lose copies of lines the new text now carries. The lint's raise step is +73 and quotes the Captain's 「接受」; the 21 is the figure he accepted. Per reader (`wc -w` over the First Officer file list; `show-stage-def | wc -w` per stage): First Officer 11722 → 11743; ideation worker 694 → 724; implementation and validation workers 1371 → 1398 and 1525 → 1552.

## What this branch is

Branch `five-rules`, base 7e0f9c2, candidate cff6d61. Branch `five-rules-restore-default` (728cb8d) is the same plus the Default sentence at an overrun, +13 words (First Officer +34, workflow text +86): the fresh-reader S6 scenario showed that removing it drops "keep results, report remaining work" (0 of 3 runs without it, 3 of 3 with it). It is above the 21 words the Captain accepted, so it needs his word before it can be used.

Also in this change: the package's word-budget step gains the raise step above; `OUTCOMES.zh.md` outcome 四 now says both halves of the rule are in the package text.

## Proof and limits

A fresh reader per role (First Officer, ideation worker) at base and candidate, same prompt and model, in files-only mode on a clean host: the candidate's answers state each of the five rules and quote its new sentence; the base answers differ on the first-report, minutes, third-dispatch, half-time-box and criterion-link scenarios and are the same on relayed words. Judging is left to the validator. One reader per role and one run each: run-to-run variation, other hosts, other stage workers and live behaviour under load are not shown. S6 was repeated three times per arm for the one difference found. The three worth answers at a budget hold appear in no answer in either arm; the reader files do not hold the script that prints them.

## Not done

No test asserting the text contains words, no new script, no change to the three profiles. The first-report trace for the scoreboard is not built; minutes to the first report stay not recorded. roborev not run: this repository is not covered by the review daemon.

## without-it unanswered

- The restored Default sentence (variant branch only): kept only if the Captain accepts +13 words; without it S6 loses "keep results, report remaining work".

🤖 Generated with [Claude Code](https://claude.com/claude-code)
