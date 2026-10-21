# Preview: the kc-decision-log read path, as a CLI you can run

DISPOSABLE. This is a throwaway sketch of the proposed `read` and `effective` commands so the design can be operated before anything is built. It is not the product, it is not a base for the implementation (the implementation copies and rewrites the prototype, per the task scope), and it reads only fictional data it creates itself.

Needs: node 24, git, python3. Uses no network and no private file. Run from this folder:

    ADR_LINT=<package root>/scripts/adr_lint.py node run.mjs --transcript transcript.txt

`run.mjs` builds a fictional repository `example/mira-decisions` in a temp folder (native `docs/adr` layout; D0, D1 supersedes ADR 0003, D2 adds a file that is not UTF-8, and D3 on a side branch off D1 adds a record with two Decision key lines; branch `main` ends at D2), runs the CLI 62 times in separate processes, and checks each exit code and field against expectations written by hand in `run.mjs`. Digests are checked against `git cat-file blob <commit>:<path>` hashed separately. The last step runs the real `adr_lint.py` on the D1 tree and compares which files it flags. Human-mode refusals go to stderr and JSON envelopes to stdout; the transcript marks stderr. Where a run shows only some JSON fields the transcript says so; run 20 shows an `effective` JSON answer in full, and the usage errors are runs 38-44. The full output is `transcript.txt`; the same run is reproducible (commit dates are fixed).

Result on 2026-10-21: all 62 runs and the lint comparison matched. Two commands you can try by hand after a run (take D0, D1 and the clone path from the top of `transcript.txt`; `cli.mjs` needs a config file of the shape in the design):

    node cli.mjs read      --config <file> --binding mira --commit <D0> --id 0003 --format human
    node cli.mjs effective --config <file> --binding mira --commit <D1> --id 0003 --format human

## Four runs from the transcript

Effective at D1 for the record D1 superseded (run 19, human): the answer for this record comes first.

    Status         Superseded by 0004
    Resolution     NOT EFFECTIVE: superseded; the ruling in force is ADR 0004   (chain 0003 -> 0004)
    Ruling ADR     0004 (same commit)
    Ruling path    docs/adr/0004-reports-are-daily.md
    Ruling digest  sha256:<64 hex>

Effective for a healthy record in a folder with an unreadable file (run 59, human): unresolved, in plain words, with the file named.

    Resolution     UNRESOLVED: a file in the ADR folder cannot be read, so no ruling can be confirmed (view_has_unreadable_record)
    Blocking       docs/adr/0015-not-utf8.md

Expected digest from D0 compared at D1 (run 8, human, stderr, exit 4):

    REFUSED digest_mismatch
      expected       sha256:<64 hex>
      actual         sha256:<64 hex>
      reference      docs/adr/0003-reports-are-weekly.md

`--require-effective` on a superseded record (run 24): the same answer is printed and the exit code is 6; on the ruling in force (run 26) the exit code is 0.

## Mutations: does each check have teeth?

Each row changes one line of a copy of `cli.mjs` and reruns `run.mjs` (own verification script, not kept here). "Caught" means the run exited non-zero and printed a mismatch. Run numbers are in `transcript.txt`; a first pass of this table on 2026-10-21 reported the CRLF row as not caught because the mutation script's pattern had not matched, which the second pass corrected.

| Mutation | Result |
| --- | --- |
| decoder drops the BOM (`ignoreBOM: false`) | caught, by the lint comparison only (lint flags the BOM file, the preview then does not) |
| decoder substitutes invalid bytes instead of refusing | caught (run 55) |
| `localeCompare` instead of byte order | caught (run 62) |
| caller's `GIT_*` variables kept | caught (run 54: a decoy `GIT_DIR` makes the repository check fail) |
| one bad record blocks every `effective` | caught (14 runs) |
| two Accepted under one key ignored | caught (run 14) |
| short commit accepted | caught (runs 31, 46, 47) |
| repository identity not checked | caught (runs 34, 49) |
| expected-digest comparison skipped | caught (runs 6, 8, 23) |
| unreadable record does not block `effective` | caught (run 58) |
| an Accepted record with a malformed or doubled key line does not block `effective` | caught (run 60) |
| no skip list | caught (run 62) |
| digest of an NFC-normalised string instead of raw bytes | caught (9 runs; the fixture has a decomposed character) |
| duplicate numbers pick the first file | caught (run 52) |
| `--require-effective` ignored | caught (runs 24, 25) |
| a human refusal written to stdout instead of stderr | caught (9 runs) |
| CRLF to LF normalisation removed | caught (19 runs): the CRLF record's `**Decision key:**` line then fails the key pattern, which blocks every `effective` answer |

## What this preview does not show

Codex or Claude plugin loading, the read-only skill, a real-size ADR folder (it reads 15 fictional ADR files), colour or terminal width (output is plain text, identical on a pipe), any private repository, or lint parity beyond these fixtures. Not exercised: how a Codex skill finds the package root, and whether Codex can run Node 24 against the clone.
