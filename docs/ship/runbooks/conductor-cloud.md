Non-normative runbook

This page applies only to a First Officer that dispatches build workers into Conductor cloud
workspaces and reads them back through the `conductor` CLI. It is this repository's own runtime
record, not a kc-dev-flow contract: an adopter running workers locally, on a Hermes runner, or on
another host is not covered by it and must not treat these sentences as requirements.

A dispatch message to a cloud build worker carries no bootstrap or download line: the Conductor WAF
blocks a dispatch message containing a `curl | tar` bootstrap line, and the worker's image already
preinstalls `kc-dev-flow` and `spacedock`, so no dispatch message needs to fetch and unpack them.

`asciinema` and `script(1)` both hang without a pty, which cloud build workers do not have — see
`references/stations/e2e-cli.md` for the stdout-log evidence format that constraint produces.

The First Officer reads a worker's transcript through `conductor sql` against
`session_transcripts_view`, not `conductor session message --after`: that CLI truncates its JSON
response at 64 KB, which cuts off a long Evidence block, and its `--after` cursor rejects a sent
message's id, which breaks polling from the FO's own last message — see
`references/stations/worker-transcript.md` for the script this host limitation motivated.

Placed segments (`references/placement.tsv`): `105937aee006`, `557d72a24417`, `57898e58e8ab`,
`c30183386509`, `fd20ac2b4540`.
