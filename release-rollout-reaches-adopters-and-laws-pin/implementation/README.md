# Implementation evidence

Candidate: `a1a35a714510683a44a2ac5ec02241e7cb354f80`.
Base: `e8664a72b0f904e5dda3c391d52ab3abaca876b4`.

`checks.json` indexes check exits, mutations, word counts and the live summary.
The full live output is retained at the /tmp path in `live-summary.json`, because
it contains unlisted private repository names. No list is committed here.
The two manual implementation reads do not replace the validator's own two picks.
qnow's absent workflow is expected: FO confirmed Captain-authorised removal at
`dce0a96c0`, after the design trial.

Run the mutation and byte-comparison controls without bytecode caches:

```sh
python3 -B prove.py /absolute/path/to/the/candidate-worktree
```

The runner copies scripts into fresh temporary directories and writes its logs
beside itself; it neither mutates the supplied candidate nor calls real GitHub.
`rollout-tests-before.log` records nine new behavior tests failing on the base;
`rollout-tests.log` records 17 passing tests on the candidate. The original six
single-README test methods are byte-for-byte retained.

Word counts use the same saved text spans for Python split and a separate `wc -w`
recount: Post-merge heading through Commit conventions; complete release skill;
Observe adopters through EOF; the installation paragraph; complete workflow README.
These explicit spans give the release document subtotal 778 -> 897 words; the
live report adds 112 words for 11 listed rows, plus four terminal-only unlisted
lines whose words are excluded from the public record. Startup, idle on open/merged
PRs, after archive and merge-ask inputs are unchanged; each delta is zero.
The complete shared workflow remains 5939 words and the single-README fixture
output remains 12. Installation is 70 -> 95 words. Off-package FO prompts are
not counted. `word-counts.json` names every unchanged compared input.

No replay of model behavior is claimed: this slice adds a human-operated reporting
step exercised through fake gh and live read-only gh; existing dispatch prose and
outputs do not change. Hosted CI cost per PR is not measured; no CI trigger or job
was added or changed.
