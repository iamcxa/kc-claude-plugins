#!/usr/bin/env python3
"""Span-match vs keyword-grep post-condition, demonstrated on the real tree (entity 5b).

WHY THIS EXISTS
---------------
The arm builder has to prove that arm B no longer instructs the pre-emit quote
gate. Round 2 proposed proving that with a keyword grep: build arm B, then assert
zero residual hits for `pre-emit` / `quote-the-line` / `§6a quote` /
`verification gate`.

That proof is unsound, and unsound in the sprint's own founding way: it classifies
a region by pattern instead of by reading it. An arm that removes only the
keyword-BEARING spans passes the keyword post-condition while the gate's operative
content is still on disk and still instructing every reviewer.

This script demonstrates that failure against the real `kc-pr-flow/` tree, and
demonstrates that the replacement post-condition -- verbatim span match, table
driven -- rejects the same arm. It is the regression test for the defect, run at
ideation time so the design is not adopted on an argument.

Proof Policy #7: a new check must be shown able to fail.

WHAT IT DOES
------------
  1. Extracts each enumerated span from the BASELINE tree by line range and
     checks its sha256 against the pinned value. A drifted file fails here, which
     is what keeps the enumeration table from going stale silently.
  2. Builds two arms from the baseline:
       arm_keyword -- removes only the spans that MATCH the keyword patterns
       arm_span    -- removes every enumerated CUT span
  3. Runs BOTH post-conditions against BOTH arms and prints the 2x2.

Stdlib only, no network, no model. Run from anywhere:

    python3 span-match-demo.py [--tree <path to kc-pr-flow>]

The site table below is pinned to `f4f4840`, so `--tree` must name a `kc-pr-flow/`
at that revision, not today's worktree. Materialize one:

    git archive f4f4840 kc-pr-flow | tar -x -C /tmp/base-f4f4840
    python3 span-match-demo.py --tree /tmp/base-f4f4840/kc-pr-flow

Run against a later tree it exits non-zero on the first drifted span, by design —
`S8` in particular was deleted from `SKILL.md` by merged PR #82. This file records
what was demonstrated at `f4f4840` and is not re-pinned forward; the harness's own
live table (`kc-pr-flow/scripts/review-ablation-spans.tsv`) is the one that tracks
the tree.

Exit code 0 means the demonstration held: keyword-grep ACCEPTS arm_keyword while
span-match REJECTS it. Non-zero means the demonstration itself failed and the
claim in the entity body is not supported.
"""

import argparse
import hashlib
import pathlib
import re
import shutil
import sys
import tempfile

# --------------------------------------------------------------- the site table
#
# Enumerated by a tree-wide sweep of kc-pr-flow/ at origin/main = f4f4840
# (kc-pr-flow/ is byte-identical at 1ca0ed0). Each span is pinned by the sha256 of
# its exact text, so this table cannot drift against the tree without failing.
#
# kind:
#   cut       remove the whole span
#   cut_sub   remove only a substring of the span, leaving the rest
#   keep      must be present and unmodified in the baseline AND in every arm

SKILL = "skills/kc-pr-review/SKILL.md"
TRIAGE = "reference/review-triage.md"
LEARNED = "reference/learned-patterns.md"

SPANS = [
    # id      file     lines          kind
    ("S1", SKILL, (975, 975), "cut"),
    ("S2", SKILL, (977, 982), "cut"),
    ("S3", SKILL, (984, 984), "cut"),
    ("S4", SKILL, (986, 986), "cut"),
    ("S5", SKILL, (988, 988), "cut"),
    ("S6", SKILL, (990, 990), "cut_sub"),
    ("S7", SKILL, (861, 862), "cut"),
    ("S8", SKILL, (1855, 1855), "cut"),
    ("S9", TRIAGE, (221, 221), "cut"),
    ("S10", TRIAGE, (223, 227), "cut"),
    ("S11", LEARNED, (13, 15), "cut"),
    ("K1", SKILL, (143, 143), "keep"),
    ("K2", TRIAGE, (229, 236), "keep"),
    ("K3", LEARNED, (9, 11), "keep"),
]

# Pins live in a generated sidecar, never typed into this table by hand: a
# hand-typed hash is a number written before it was computed. Regenerate with
# --write-pins after an intentional tree change; a mismatch otherwise means the
# line ranges above no longer name the text they were enumerated from.
PINS_FILE = pathlib.Path(__file__).with_name("span-pins.txt")

# The substring S6 removes, and what must survive that removal.
S6_REMOVE = " after the verification gate"
S6_KEEP = "**Apply confidence gates**"

# The round-2 post-condition, verbatim. `verification gate` carries the
# whitelist carve-out for the Step 2.5 sentence, exactly as specified.
KEYWORD_PATTERNS = [
    r"pre-emit",
    r"quote-the-line",
    r"§6a quote",
    r"verification gate",
]
STEP25_WHITELIST = (
    "Step 2.5 builds a verification gate from explicit concerns"
)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract(tree, relpath, lines):
    """Extract a span by 1-indexed inclusive line range."""
    body = (tree / relpath).read_text(encoding="utf-8").split("\n")
    a, b = lines
    return "\n".join(body[a - 1:b])


# ------------------------------------------------------------------ arm building


def remove_span(tree, relpath, text):
    """Delete one exact verbatim span from a file. Fails if it is not there once."""
    path = tree / relpath
    body = path.read_text(encoding="utf-8")
    n = body.count(text)
    if n != 1:
        raise SystemExit(
            f"FATAL: span occurs {n} times in {relpath}, expected exactly 1"
        )
    # Remove the span plus the newline that terminated it, so no blank hole is
    # left where a block used to be.
    body = body.replace(text + "\n", "", 1)
    path.write_text(body, encoding="utf-8")


def remove_substring(tree, relpath, sub):
    path = tree / relpath
    body = path.read_text(encoding="utf-8")
    if body.count(sub) != 1:
        raise SystemExit(f"FATAL: substring not uniquely present in {relpath}")
    path.write_text(body.replace(sub, "", 1), encoding="utf-8")


def build_arm(baseline, dest, span_ids, resolved):
    """Copy the baseline and apply the removals named by span_ids."""
    shutil.copytree(baseline, dest)
    for sid in span_ids:
        _, relpath, _, kind, text = resolved[sid]
        if kind == "cut":
            remove_span(dest, relpath, text)
        elif kind == "cut_sub":
            remove_substring(dest, relpath, S6_REMOVE)
    return dest


# -------------------------------------------------------------- post-conditions


def keyword_postcondition(tree):
    """Round 2's proof: zero residual keyword hits outside the whitelist.

    Returns (passed, list of residual 'file:line' hits).
    """
    residual = []
    for relpath in (SKILL, TRIAGE, LEARNED):
        path = tree / relpath
        if not path.exists():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if STEP25_WHITELIST in line:
                continue
            for pat in KEYWORD_PATTERNS:
                if re.search(pat, line, re.IGNORECASE):
                    residual.append(f"{relpath}:{i}")
                    break
    return (not residual), residual


def span_postcondition(tree, resolved):
    """The replacement proof: verbatim span match, per enumerated span.

    Every CUT span in the SPEC must be ABSENT; every KEEP span must be PRESENT
    and byte-equal to its pinned baseline text. Returns (passed, violations).

    The span set checked is the enumerated spec, never the set the builder
    happened to apply. Checking only what was applied is a check that cannot
    fail -- it asks the builder to grade its own homework, which is the same
    shape of defect as proving absence by the keywords you chose to grep for.
    """
    violations = []
    for sid, relpath, _, kind, text in resolved.values():
        body = (tree / relpath).read_text(encoding="utf-8")
        if kind in ("cut", "cut_sub"):
            probe = S6_REMOVE if kind == "cut_sub" else text
            if probe in body:
                violations.append(f"{sid} ({relpath}): CUT span still present")
        elif kind == "keep":
            if text not in body:
                violations.append(f"{sid} ({relpath}): KEEP span missing or modified")
    # S6's keep-half: the edit must not have eaten the rule it trims.
    if S6_KEEP not in (tree / SKILL).read_text(encoding="utf-8"):
        violations.append("S6 (SKILL.md): the surviving 'Apply confidence gates' rule was lost")
    return (not violations), violations


# ------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--tree",
        default=str(pathlib.Path(__file__).resolve().parents[4] / "kc-pr-flow"),
        help="path to the baseline kc-pr-flow tree",
    )
    ap.add_argument(
        "--write-pins",
        action="store_true",
        help="regenerate span-pins.txt from the current tree",
    )
    args = ap.parse_args()
    baseline = pathlib.Path(args.tree).resolve()
    if not (baseline / SKILL).exists():
        raise SystemExit(f"FATAL: no {SKILL} under {baseline}")

    print(f"baseline tree: {baseline}\n")

    # 1. Resolve every span against the baseline, and record its hash.
    resolved = {}
    computed = {}
    print("== enumerated spans, resolved against the baseline ==")
    for sid, relpath, lines, kind in SPANS:
        text = extract(baseline, relpath, lines)
        if not text.strip():
            raise SystemExit(f"FATAL: {sid} resolved to empty text -- the tree moved")
        resolved[sid] = (sid, relpath, lines, kind, text)
        computed[sid] = sha(text)
        keyworded = any(
            re.search(p, text, re.IGNORECASE) for p in KEYWORD_PATTERNS
        )
        print(
            f"  {sid:>3} {kind:<7} {relpath}:{lines[0]}-{lines[1]}"
            f"  sha={computed[sid][:12]}  keyword-visible={'YES' if keyworded else 'no '}"
        )

    if args.write_pins:
        PINS_FILE.write_text(
            "".join(f"{s} {computed[s]}\n" for s, *_ in SPANS), encoding="utf-8"
        )
        print(f"\nwrote {PINS_FILE.name} ({len(SPANS)} pins)")
    elif PINS_FILE.exists():
        pinned = dict(
            line.split() for line in PINS_FILE.read_text(encoding="utf-8").split("\n")
            if line.strip()
        )
        drift = [s for s in computed if pinned.get(s) != computed[s]]
        if drift:
            raise SystemExit(
                f"FATAL: span pins do not match the tree for {drift} -- the line "
                f"ranges no longer name the text they were enumerated from"
            )
        print(f"\n  all {len(computed)} spans match their pins in {PINS_FILE.name}")

    cut_ids = [s for s in resolved if resolved[s][3] in ("cut", "cut_sub")]
    keyword_visible = [
        s for s in cut_ids
        if any(re.search(p, resolved[s][4], re.IGNORECASE) for p in KEYWORD_PATTERNS)
    ]
    invisible = [s for s in cut_ids if s not in keyword_visible]
    print(
        f"\n  CUT spans: {len(cut_ids)}   keyword-visible: {len(keyword_visible)}"
        f"   invisible to the keyword grep: {len(invisible)} -> {invisible}"
    )

    # 2. Build the two arms.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        arm_keyword = build_arm(
            baseline, tmp / "arm_keyword", keyword_visible, resolved
        )
        arm_span = build_arm(baseline, tmp / "arm_span", cut_ids, resolved)

        print("\n== post-conditions, both arms ==")
        rows = []
        for name, arm, applied in (
            ("arm_keyword", arm_keyword, keyword_visible),
            ("arm_span", arm_span, cut_ids),
        ):
            kw_ok, kw_hits = keyword_postcondition(arm)
            sp_ok, sp_bad = span_postcondition(arm, resolved)
            rows.append((name, kw_ok, kw_hits, sp_ok, sp_bad))
            print(f"\n  {name}  (removed {len(applied)} spans)")
            print(
                f"    keyword-grep post-condition : "
                f"{'PASS' if kw_ok else 'FAIL'}"
                + ("" if kw_ok else f"  residual hits: {kw_hits}")
            )
            print(
                f"    span-match post-condition   : "
                f"{'PASS' if sp_ok else 'FAIL'}"
            )
            for v in sp_bad:
                print(f"        - {v}")

        # 3. The claim under test.
        kw_arm = rows[0]
        span_arm = rows[1]
        print("\n== the claim this script exists to test ==")
        ok = True

        claim1 = kw_arm[1] is True
        print(
            f"  [{'OK ' if claim1 else 'XX '}] keyword-grep ACCEPTS an arm that still "
            f"instructs the gate"
        )
        ok &= claim1

        claim2 = kw_arm[3] is False
        print(
            f"  [{'OK ' if claim2 else 'XX '}] span-match REJECTS that same arm "
            f"({len(kw_arm[4])} violations)"
        )
        ok &= claim2

        claim3 = span_arm[3] is True and span_arm[1] is True
        print(
            f"  [{'OK ' if claim3 else 'XX '}] both post-conditions ACCEPT the fully "
            f"ablated arm (the check is not always-reject)"
        )
        ok &= claim3

        # A KEEP span must be able to fail too, or the keep half is vacuous.
        arm_bad_keep = build_arm(baseline, tmp / "arm_bad_keep", cut_ids, resolved)
        remove_span(arm_bad_keep, TRIAGE, resolved["K2"][4])
        keep_ok, keep_bad = span_postcondition(arm_bad_keep, resolved)
        claim4 = keep_ok is False and any("K2" in v for v in keep_bad)
        print(
            f"  [{'OK ' if claim4 else 'XX '}] span-match REJECTS an arm that also "
            f"ablated a KEEP span (K2, the collator table)"
        )
        ok &= claim4

        if not ok:
            print("\nDEMONSTRATION FAILED -- the entity body's claim is unsupported.")
            return 1
        print("\nDemonstration held.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
