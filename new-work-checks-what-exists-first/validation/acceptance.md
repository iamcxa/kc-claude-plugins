No visible UI change. Requires the clean assigned code worktree at the pinned head, saved task evidence, Python 3, Git, ripgrep, the named package installation and network access for reservation refresh.

Run exactly:

    bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/new-work-checks-what-exists-first/validation/acceptance.sh

Four steps: pinned identity/export; candidate-versus-base routing and scope; repository lint/design parsing; ADR 0083 and fresh number reservations. Each prints STEP N PASS; final line starts ACCEPTANCE PASS, exit 0. Observed output is acceptance.log, from the exact fresh-shell run.

The script creates its own export with mktemp and removes that exact resolved path with an EXIT trap. It references no previous scratch. It does not resolve missing cold behavior, rerun private sources, or establish merge, release or adoption.
