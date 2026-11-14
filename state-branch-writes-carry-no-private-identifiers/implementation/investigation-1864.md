# Review 1864: both High findings reproduced

Candidate `0c68231ca9147a9833846b47a36e2fc27846cf66` remains unchanged and unpublished. These findings block the earlier readiness conclusion; no fix is applied or authorized by this investigation.

The probe ran 22 hook-boundary cases against the candidate, using invented identifiers and independent throwaway clones/remotes. Both direct scans and real Git commit/push commands were exercised. `results.json` pins before/after HEAD, status and both relevant source hashes; `commands.json` retains command arguments and observed exits.

## Finding 1: changed text can yield no scanned bytes

Confirmed in `kc-dev-flow-2/scripts/state_guard.py:223`: `added_bytes()` checks whether the new blob is UTF-8/NUL-free, then assumes Git will emit hunks. Git can classify the pair as binary because of its size configuration, a global attribute, or the old blob. No hunks means the current parser returns empty bytes, so the new listed literal is missed.

| Input | Git diff | Scanned bytes | Commit exit | Push exit | Identifier reached remote |
|---|---|---:|---:|---:|---|
| small-utf8-control | hunk | 41 | 1 | 1 | false |
| configured-size-threshold | binary | 0 | 0 | 0 | true |
| path-specific-binary-attribute | hunk | 41 | 1 | 1 | false |
| global-binary-attribute | binary | 0 | 0 | 0 | true |
| old-nul-new-utf8 | binary | 0 | 0 | 0 | true |
| new-nul-control | binary | 49 | 1 | 1 | false |
| old-utf16-new-utf8 | binary | 0 | 0 | 0 | true |
| new-latin1-nonutf8-control | hunk | 44 | 1 | 1 | false |

The size case sets `core.bigFileThreshold=64` in the throwaway clone; both text blobs exceed 64 bytes. The normal default large-file threshold was not exercised. `*.txt -diff` did not reproduce in this blob-object invocation; `* -diff` did. The NUL and encoding failures require the old blob to contain NUL or UTF-16 and the new blob to be ordinary UTF-8 with the listed literal. A new NUL blob or new Latin-1/non-UTF-8 blob with the ASCII literal is already scanned whole and correctly refused.

**Acceptance affected:** AC-1 public committed bytes and AC-3 rejection of a push adding a listed identifier. The normal supported candidate workflow is a First Officer/adopter saving state with `private-slug=refuse`; the observed harm is that the local remote receives the listed literal. This is candidate-only proof, not an incident claim about the released package or live branch.

**Smallest proposed fix:** in `added_bytes()`, return empty immediately when the two object ids are equal, then retain current gzip/binary handling. For differing object ids, return the full new blob when the patch has no hunks; otherwise return parsed added lines. The equal-id rule also preserves rename compatibility for finding 2. Add real commit and pre-existing-unpushed-commit/push cases in `test_state_guard.py` for the configured threshold, global binary attribute, old-NUL/new-text and old-UTF-16/new-text; retain ordinary text/new-binary controls.

## Finding 2: identifiers in paths are never matched

Confirmed in `kc-dev-flow-2/scripts/state_guard.py:263`: matching reads content alone. A private-slug folder with clean file content is accepted. A private-slug basename also passes. A pure rename into that folder is dropped even before matching because `changes()` at line 203 excludes equal blob object ids.

| Path case | Candidate yielded entries | Commit exit | Push exit | Listed path reached remote |
|---|---:|---:|---:|---|
| new-private-folder | 1 | 0 | 0 | true |
| new-private-basename | 1 | 0 | 0 | true |
| pure-rename-private-folder | 0 | 0 | 0 | true |

**Acceptance affected:** the Scope outcome and AC-1 public committed-artifact identifier boundary, including tree paths. AC-3 currently says added lines; it does not explicitly promise path scanning, which is the coverage omission exposed here. FO must authorize the correction separately; this report changes no criterion or design.

**Smallest proposed fix:** retain non-deleted, non-gitlink change entries whose object id is unchanged (including R100 renames), match each pattern against raw path bytes as well as the selected content bytes, and use existing `safe_name()` redaction in refusal output. The equal-id early return proposed for finding 1 must precede gzip/binary handling so a clean archive rename does not rescan inherited blob content. Add new-folder, basename and R100-rename refusal tests at both commit and push, assert that the literal path identifier is absent from diagnostics, and keep the existing archive-rename compatibility case.

## Reproduction and limits

Evidence: `evidence/implementation-1/investigation-1864/{probe.py,results.json,matrix.json,commands.json,findings.json,probe.log}`.

From the task folder, run the retained probe with an existing exact-candidate code checkout and an authorized dispatch scratch directory:

```sh
python3 -B evidence/implementation-1/investigation-1864/probe.py <candidate-code-checkout> <dispatch-scratch>/investigation-1864
```

The command exits 0 when the investigation finishes and the candidate is unchanged; the observed guard/commit/push exits are the per-case values above. Commit and push tests are independent fixtures: the push fixture creates its unpushed commit before installing the guard, without a bypass flag. The probe uses only synthetic identifier lists and local file remotes, installs only in those throwaways, and performs no config write in this repository.

Observed Git: `git version 2.54.0 (Apple Git-157)`. No product files, test files, version, live hooks, PR, or upstream issue were changed. The two-file fix is proposed only; no corrected-candidate result is claimed.
