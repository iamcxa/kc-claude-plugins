# Merge resolution

Fetched origin first; main was abe8c08ea2716e5f1c046823082e122759703b87. The repair commit 2cdad4c44 was followed by merge commit 2f454b7bd, with first parent 2cdad4c44 and second parent abe8c08ea2716e5f1c046823082e122759703b87. No rebase, squash, amendment or product push.

1. pr_watch.py import hunk: retained the branch's scratch import and main's readme_extensions import. The shared extension reader and owned scratch namespace both remain available.
2. pr_watch.py merged-PR hunk: retained the branch's unconditional MERGED branch and scratch_lines call before the learn-extension condition. Then retained main's --readme workflow/README.md on the observer_check subprocess. The printed post-merge observer command also retains main's --readme argument. Thus cleanup still prompts with learn disabled, while detached-state observer/learning uses the actual workflow README.

Only pr_watch.py had textual conflict markers. test_pr_watch.py auto-merged: main's detached-state/readme/archive/extension-list tests and missing-worktree-as-fact test remain alongside the branch's older/current/archived/merged scratch tests. Commit 4be5fe99f extends the existing merged-scratch test to a detached state checkout, executes the printed observer command with --readme, and then disables learn and confirms scratch cleanup still prompts without an observer/pr-merge line. Removing either the merged cleanup or the printed README argument is rejected by the test.

merge-conflicts.patch retains the two original conflict hunks; merge-resolution.patch retains the actual combined merge diff. All imported non-design-file changes are the explicitly authorised origin/main merge, not additional repair edits. Relative to that main commit, only the original six scripts/tests and authorised ADR 0079 differ.
