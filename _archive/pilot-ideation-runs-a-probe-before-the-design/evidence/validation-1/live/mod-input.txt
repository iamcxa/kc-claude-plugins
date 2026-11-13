`<package>` is the `Package root:` line of `kc-dev-flow-2:dev`.

## Hook: startup

1. Run the idle hook below.

## Hook: idle

1. Run `python3 <package>/scripts/pr_watch.py tasks <workflow dir>`.
2. Do each `next:` line it prints, in order.
3. After the `pr-merge` hook, do each `after pr-merge:` line it printed.
