---
name: watch-and-learn
description: kc-dev-flow-2 first-officer steps: record and watch each open task PR, check the head before the merge ask, run learn after the archive
---

# Watch the PR, then learn

Copied unchanged from kc-dev-flow-2 `references/sd/mods/watch-and-learn.md`. Its name sorts after `pr-merge.md`: step 5 needs the archive that the `pr-merge` startup and idle hooks perform. This file has no merge hook: the implementation stage opens the Draft PR, and with `pr` set `merge guard` arms none. `<package>` is the `Package root:` line of `kc-dev-flow-2:dev`.

## Hook: startup

Do steps 1 to 4, then step 5 for each task the `pr-merge` startup hook archived.

## Hook: idle

Do steps 1 to 4, then step 5 for each task the `pr-merge` idle hook archived in this pass.

1. Record. For each task whose `pr` is empty and that has a `worktree`, take its branch (`git -C <worktree> branch --show-current`) and its code repository as the `pr-merge` startup hook resolves it. When that branch has a PR in any state (`gh pr list --repo <owner/repo> --head <branch> --state all --limit 1 --json number`, newest first), run `spacedock status --workflow-dir <dir> --set <slug> pr=<owner/repo>#<N>`, then `spacedock state commit <slug> --workflow-dir <dir>`.
2. Watch. For each open task PR run `python3 <package>/scripts/pr_watch.py add <owner/repo>#<N>`, with the flags the "Watch" line of each listed reviewer extension names; repeating it is safe. Keep one `python3 <package>/scripts/pr_watch.py wait` running in the background: start it unless one started in this session has not exited.
3. Read an exit. A `wait` exit names the change. Act on it as this README's Delivery authority and Extensions sections say: mark ready where CI skips drafts, read each listed reviewer, report a conflict or failing CI to the Captain. A merge needs nothing here; the next idle pass runs `observe-merged`, then `pr-merge`.
4. Check the head. Before the `gate prepare` that asks for merge, run `python3 <package>/scripts/delivery_gate.py check <task> --pr <owner/repo>#<N> --text-file <question and summary>`. Exit 1 or 2 holds the ask; show the Captain what it printed.
5. Learn, only where this README's `extensions:` lists `learn`; otherwise skip this step. Run `python3 <package>/scripts/observer_check.py <state> <slug>` once more and follow the learn extension's "FO step" for exit 1, then run `kc-dev-flow-2:learn` for the slug. Present learn's notice, then the observer report, in one message.
