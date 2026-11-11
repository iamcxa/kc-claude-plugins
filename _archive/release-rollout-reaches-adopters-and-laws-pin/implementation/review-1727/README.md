# Read integrity follow-up: RoboRev job 1727

Candidate: `61529999eb4184b44328fe2fbad545b1b0b0ed92`.
Prior candidate: `ba98f3ca95c1f879bf460fbb08976f337e18c4c8`.
Original base: `e8664a72b0f904e5dda3c391d52ab3abaca876b4`.

## Finding adjudication

The specific claim that matching-refs silently stops at a first page is not
substantiated. GitHub's own reference lists no page/per_page query parameters and
no pagination threshold. On 2026-11-11 the component prefix returned 49 refs with
or without --paginate. A broader public prefix returned all 165 repository tags
in one response. Setting per_page=1&page=2 returned the same sets, and no tested
response had Link pagination. See refs-probe.json, its saved public responses,
and sources.json. These probes do not prove every hypothetical server limit;
they agree with the documented non-paginated endpoint. Github.releases is
byte-identical to the prior candidate, so no fictional page fixture or needless
pagination mechanism was added to it.

## Survey and bounded repairs

read-survey.json enumerates every gh read, its result shape, cap behavior and
change/retention reason. The survey found two real boundary defects:

- The CLI already follows code-search pages, but JSON exports only items. Its
  result cap and incomplete_results metadata were invisible to the old reader.
  Search now uses raw REST pages, preserves completeness metadata and prints
  search: unavailable for caps, timeouts and results ending before total_count.
  That diagnostic does not change the listed-row debt exit. Index/access/scope
  restrictions remain part of GitHub search; this is a cross-check, not a fleet
  registry. No broadened owner enumeration or query partitioning was added.
- A successful contents response can omit a large file's content. The public
  GitHub OpenAPI file probe returned size 14,216,605, encoding none and empty
  content. The prior reader accepted that as empty text; the candidate explicitly
  marks it unreadable. The tests show two omitted workflow/laws payloads no
  longer compare equal. The directory cap is irrelevant to exact-file reads;
  large unsupported downloads fail rather than gaining a new raw-download route.

All other reads are single objects, not paginated collection calls. The report
keeps the original comparison semantics, the both-owed merge order and every
criterion unchanged. This round adds no independent product rule or ADR.

## Evidence and reproduction

23 package_version tests pass. The prior candidate has five failing
cases/subcases for ignored completeness or omitted file content. The page-2
fixture is a wiring/regression test; the old CLI already paginated and that
fixture is not presented as a prior CLI pagination defect. Five mutations reject
first-page-only traversal, ignored incomplete/cap/short-page metadata and the
missing content guard. Original controls, legacy byte comparisons and the
amendment-2 order/byte controls pass again.

```sh
python3 -B prove.py /absolute/path/to/the/candidate-worktree
python3 -B refs-probe.py
```

The first command uses fresh temporary copies and the saved public large-content
response; the second performs only public read-only API calls. Original and order
controls can be rerun with their respective subfolder's prove.py and the same
candidate path. All Python probes use -B and fresh cache-free copies.

The fresh live run reports 11 listed rows, four unlisted, exit 0, with no search
unavailable diagnostic; listed output is byte-identical to the prior candidate.
Full private output stays only /tmp/rollout-review-1727/live-output.txt, not in
this directory. No adopter list or private unlisted name is committed here.
The two independent validator choices remain due.

The document-impact check lists ADR 0075 and maintain-flow. Both are unaffected:
their read-only debt report, error policy and post-merge pin sequence remain
correct; the internal API integrity checks clarify those promises. Workflow and
lifecycle documents are byte-identical to the prior candidate, so word-count
moments remain unchanged except diagnostics at release-report time. No CI or
version file changed, and hosted cost per PR was not measured. FO still owns
product push, Draft PR #838, RoboRev rerun, hosted CI and independent validation.
