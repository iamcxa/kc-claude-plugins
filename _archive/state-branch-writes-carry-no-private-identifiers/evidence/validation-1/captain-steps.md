# Acceptance replay

No visual surface changes. Run from the assigned PR 871 product worktree root at `d2d5bec640f0a61d3e044877b8443cdfdc03faa7`, with a clean product tree. Requires Python 3, Git, the installed `spacedock` on PATH, this public state checkout and its retained implementation evidence, and the owner's identifier list at `${XDG_CONFIG_HOME:-$HOME/.config}/kc-dev-flow-2/identifiers.tsv`. The list is read by path only; no entry is printed or copied.

```sh
python3 ../../docs/dev2/.spacedock-state/state-branch-writes-carry-no-private-identifiers/evidence/validation-1/acceptance.py \
  "$PWD" ../../docs/dev2/.spacedock-state "$(command -v spacedock)" \
  /tmp/dev2/kc-claude-plugins-3042bb224e995ded/state-branch-writes-carry-no-private-identifiers/validation-1
```

The script performs four steps in one command:

1. Check the exact candidate and clean product tree. Expected: `1 PASS`.
2. Run a real dispatch, special-role prompt and sealing over 256 KiB; scan committed and pushed bytes, then compare seven historical folders. Expected: `2 PASS`; the one known historical digest mismatch remains, with no newly broken digest.
3. Run real refused and accepted pushes, no-hunk and path repairs, unguarded detection and state/product isolation. Expected: `3 PASS`.
4. Run the ADR check since the recorded base, requiring 0087, and remove throwaways. Expected: `4 PASS`, exit 0.

This replay installs hooks only in throwaway clones, whose remotes are local. It covers neither live installation nor commit-metadata identity, private-list completeness, platform timing or merge authority. It does not rerun all regression tests or the independent extended attack matrix. Historical evidence is read in place, never rewritten. If the sampled state corpus has changed, compare it with `acceptance-acceptance.json` before interpreting a failed count assertion.

After FO records the result and retains needed output, run the dispatched `scratch.py close` command for `validation-1` to remove the empty dispatch scratch parent created by a later replay.
