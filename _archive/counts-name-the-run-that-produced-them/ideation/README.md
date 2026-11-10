# Ideation replays, 2026-11-09 (read-only)

All scripts read committed state with `git show` / `git ls-tree`, or learn records on disk; none writes.

- `scan_replay.py <state checkout> <label> 2026-11-05T00:00:00Z` → `scan_replay.out`: the proposed count scan over committed
  validation briefing summaries, split at the cut (ADR 0055's printed rule shipped 2026-11-04). Run 2026-11-09T05:15Z.
- `learn_replay2.py <git common dirs>` → `learn_replay.out`: count tokens in completed learn `add` entries' Evidence,
  against the decision's referenced pack evidence. Run 2026-11-09.
- `sourced_sample.py <state checkout> 2026-11-05T00:00:00Z` → `sourced-after-*.out`: post-cut count sentences with no
  bracketed date, backticked command or `report, not run` (ADR 0055's form, regex `sourced.py`). Run 2026-11-09.
