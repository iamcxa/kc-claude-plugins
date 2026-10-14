---
name: observe-merged
description: kc-dev-flow-2 first-officer step: the learn observer check before pr-merge records a merged PR
---

# Observe a merged PR before its sentinel

Copied unchanged from kc-dev-flow-2 `references/sd/mods/observe-merged.md`. This file has no merge hook, and its name sorts before `pr-merge.md`: Spacedock runs a point's hooks in filename order. `<package>` is the `Package root:` line of `kc-dev-flow-2:dev`.

## Hook: startup

Run the idle hook below.

## Hook: idle

Do nothing unless this README's `extensions:` lists `learn`. For each task whose `pr` is a bare reference, read the PR the way the `pr-merge` startup hook below does. For each one that is MERGED, before that hook records its sentinel, run `python3 <package>/scripts/observer_check.py <state> <slug>` and follow its exit as `<package>/extensions/learn/EXTENSION.md` ("FO step") says. On exit 1 or 2 leave that task out of the `pr-merge` hook below until a later pass shows exit 0.
