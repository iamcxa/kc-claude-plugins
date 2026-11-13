# Merge-up scope stop

The merge of origin/main 46e9d0ed4bb86889022457adcdf656965dc97e73 into product HEAD 455846c6d30d4ab650c1c4503bc591722231586d is unresolved. Six conflicts were observed; four paths are outside the approved design, so the dispatch's stop instruction applies. No manual conflict resolution, tests, acceptance replays or merged-candidate claim follows.

Conflicts: kc-dev-flow-2/scripts/{dispatch_stage.py,pr_watch.py,scratch.py,test_dispatch_stage.py,test_pr_watch.py,test_scratch.py}. Only pr_watch.py and test_pr_watch.py are approved design files; ADR 0081 is the third approved file and has no conflict. Every conflicting hunk is left unresolved pending FO direction. The in-progress merge also stages incoming main changes; those are automatic merge results, not worker-authored scope expansion.

merge.log records the authorized merge attempt; unmerged-index.txt records Git's three stages for each conflict; conflicts.patch preserves all conflict hunks; merge-refs.txt records HEAD, origin/main and MERGE_HEAD in that order. product-status.txt records the resulting tree. task-read-before-report.json supplies the required pre-append total_lines=554. The dispatched 0.39.1 role guard exits 0 with `budget: Budget: 1 implementation and 3 validation cycles; spent implementation 1, validation 2`.

The initial sandboxed merge failed before starting because ORIG_HEAD.lock was outside the writable root. The identical authorized local merge was then run with approved escalation and reached the recorded conflicts. No configuration, remote, push, rebase, held-task file or other worker's state path was changed.

Scratch created: none. Exact paths removed: none. No /tmp PR text was created or touched. The product merge is intentionally left in progress, not aborted or committed. No fresh check or test passes are claimed; earlier results stay bound to their earlier source bytes.
