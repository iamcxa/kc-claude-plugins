feat(kc-dev-flow-2): add optional operator feedback interviews

Adds the optional `fo-feedback` extension for a maintainer to interview known adopting First Officers every three completed batches. Each enabled extension gets four questions in one message; the round template retains unavailable respondents, missing evidence, uncertain sends and disagreements with the independent observer. Findings follow existing backlog and Captain decisions.

The package README lists the optional extension, adoption offers it unchecked with explicit prerequisites, and this repository opts in through `docs/dev2/README.md` frontmatter. Package template defaults, runtime hooks, scripts, versions and CI are unchanged. Captain amendment 1 replaces the per-rule/single-send and historical-wrapper requirements; the state index links the three original interviews, preserving their 13 respondent sections.

Captain amendment 2 moves the original AC-2 verbatim into its superseded-text record and replaces it with AC-9. The live three-batch cadence will be shown at the first due round, rather than before merge. The Captain requested early targeted interview round 4 across the five known First Officers, covering one or two extensions with about ten bundled sends and no test agents. That round still owes the operational interview, source-comparison, recovery and actual reading evidence found missing in validation; fixture replays do not discharge it.

Evidence and limits:
- Local fixture replays do not read the policy text. They check their explicit inputs and assertions, and continued passing when validation inverted that text; they do not establish that a First Officer follows the extension, adoption or transport procedure.
- Historical byte preservation and extension-tier parser checks are separate bounded evidence. Prior implementation recorded repository lint and 45 existing lint tests passing, ADR/number/design/whitespace checks passing, and no additional affected documents.
- The repair reruns repository package lint, task design-surfaces and dispatch-record checks. It verifies that only the adopted README extension line changes and that the original AC-2 moves verbatim with task frontmatter preserved.
- Prior bounded reading corpus: opted-in startup +599 words; ordinary idle, archive and merge +0; first Paseo due round 3,356 fixed instruction words plus variable data; adoption +97 words once. These are corpus measurements, not an attended reading trace or a total-model-context claim. Actual operational reading evidence remains owed by round 4.
- RoboRev previously exited 3 because its daemon was not running. FO owns RoboRev, hosted CI on the new exact head and updating this existing PR body; this repair worker makes no GitHub API call. CI cost per PR was not measured; no trigger changed.

Delivery remains held at validation pending the operational evidence and independent recheck. PR #745 merges after #744, whose completed-batch rule it reads; #744 is stacked on #743. No review request, ready action or merge is authorized to this worker. Preserve sibling edits to `references/sd/adoption.md` when integrating.
