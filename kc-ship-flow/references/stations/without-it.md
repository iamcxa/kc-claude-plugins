# without-it station

**Enforcing script:** `kc-ship-flow/scripts/without-it.sh <sha> <command> <removed-variant>`

**Input:** a candidate `<sha>`, one self-contained `<command>` shell line, and one self-contained
`<removed-variant>` shell line that reverts the candidate change.

**Output:** exit 0 when the retained run passes and the removed run fails; the retained/removed exit
codes are logged for the caller.

**Refusal:** exit 1 when the retained run itself fails, or when the removed run also passes (the
command does not distinguish the two variants); exit 2 on a usage error.

`<command>` runs with `LINEAR_API_KEY`, `GH_TOKEN`, `GITHUB_TOKEN`, `CONDUCTOR_API_KEY`,
`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `CODEX_API_KEY` stripped from its environment; `PATH`,
`HOME`, and `TMPDIR` are kept. This is a partial isolation only — see `references/placement.tsv`
`c2e920c86922` for the residual (temp-HOME/no-network isolation is not checked by this script).

Placed segments (`references/placement.tsv`): `173b015e4a8a`.
