# Amendment 4 evidence

The candidate remains 455846c6d30d4ab650c1c4503bc591722231586d on Draft PR #856. No product file, product commit, PR text or PR metadata changed in this round. The Captain's answer and the exact bound from his approved question are saved with each case. NP-3 in the task now points at these commands and outputs.

## Run and interpret

`count-held-words.py --help` lists every input. Python 3.11, PyYAML, git, wc and Spacedock 0.27.2 are required. Create an empty scratch root, then run the three exact commands in commands.json; for a fresh replay choose a new root for --scratch. Outputs are written to the supplied task evidence directory. The script uses -B and imports the unchanged candidate formatter. It creates valid Held sections only in scratch copies; no actual held task is edited.

The one-task case selects one real held row from the native query. The current case uses all fourteen native rows. The larger case is 100 fabricated formatter rows, twenty per each of the five configured workflow stages. Its terminal done rows exercise grouping only; they do not claim a terminal task can natively be held. The larger case checks the maximum stage overhead of this five-stage workflow, not an arbitrary workflow with more stages.

one.log, current.log and larger.log save the three observed results; the corresponding fact.txt files preserve exact output. measurements.json gives the counts and configured stages; commands.json records each command, exit and saved log. Every case uses wc -w and agrees with Python whitespace counting. The fixed portion measures 15 words, plus one word per stage and one per task: the one-task result is 17/21, fourteen is 32/34, and the five-stage hundred-task result is 120/120. The zero-task case is covered by the unchanged existing unit tests and is not a new case in this round.

`check-bound.py FACT_FILE TASK_COUNT` is the fresh-process acceptance oracle. falsifiers.json records all three real inputs accepted (exit 0) and one-word-over-bound mutations rejected (exit 1). The mutated counts are 22/21, 35/34 and 121/120. These mutate evidence, not product source. Source identity is hash-verified against the first implementation round in source-identity.json.

Existing related tests and source mutations are retained from implementation/ and independently rerun in validation/ at these identical source bytes. They were not rerun here because no product code changed. Only the word-bound rejection is repaired by this evidence and task-definition update. Local package checks are retained in the named log files. Publication, hosted CI, the second validation verdict, and actual Held body edits remain FO-owned; CI cost was not measured and CI configuration is unchanged.

Evidence is committed before cleanup. cleanup.json records the exact scratch path removed; the old /tmp PR text file is absent at the cleanup check and was not created, changed or removed by this worker in this round. The older formula's rejection and earlier reports remain history; the complete new implementation report supersedes them for amendment 4.
