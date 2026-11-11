# Changes after pre-registration

- 2026-11-11, before any scored run. The rehearsal step (C-codex-r0 step 1, not scored) wrote an ADR numbered
  0005 for the cancel-window task, so the ruling in step 3 would not be 0005. `score.py` F4 to F6 now find the
  added ADR that carries the owner's words and use its number, instead of the literal 0005. Added the secondary
  count `adrs_added` (ADRs beyond the original four; one ruling is given). PREREG.md's measure list reads
  "0005" nowhere; its FACTS reference stands.
- 2026-11-11, after the scored runs. `score.py` was not changed. A fresh-context reviewer read all nine end states
  and its reading differs from the script on two facts: F5 (the script misses `Superseded by [0007](...)` and
  `Superseded by [ADR 0007](...)`, so it scored six superseded records as not superseded) and F3 (the script
  counted a link whose file name contains "deposit" as stating the rule). `reviewed.json` holds the reviewer's
  matrix beside the script's totals. Both are reported; the registered reading rule is applied to each.
- 2026-11-11, before round 2. `world.py` gains arms D and E (arm A's step-0 tree is unchanged, checked).
  `score.py`: F5 accepts `Superseded by [0007](...)` and `[ADR 0007](...)`, the miss the round-1 reviewer found;
  `idea_files` and `idea_in_later_md` added. Round-1 script totals in `reviewed.json` were computed before this.
