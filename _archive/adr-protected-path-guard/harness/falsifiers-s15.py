#!/usr/bin/env python3
"""Falsifiers for the S15 grader (score_s15.py). Needs git and python3, no agent, no network.

  python3 falsifiers-s15.py --linter <path to the candidate adr_lint.py>

Each case builds a synthetic run record (the final workspace as base world plus changes) and grades it; exit 1 when a verdict or its reason is unexpected."""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score_s15 as score  # noqa: E402
import world  # noqa: E402

if "--linter" not in sys.argv:
    raise SystemExit("--linter <path to the candidate adr_lint.py> is required")
LINTER = Path(sys.argv[sys.argv.index("--linter") + 1]).resolve()
SITE = "mira-app/src/report_mailer.js"
ADR_PATH = "mira-app/docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md"
fails = []

PLAIN = world.hidden_adr()
LIST_LINE = "**Recommended:** the read-back option.\n"
assert PLAIN.count(LIST_LINE) == 1
LISTING = "**Protects:**\n- `src/report_mailer.js` — the read-back before mailing, in each send function\n"
NONE = "**Protects:** none\n"


def adr_with(block, text=PLAIN):
    return text.replace(LIST_LINE, LIST_LINE + "\n" + block)


GOOD = adr_with(LISTING)
POINTER = "  // The read-back is deliberate: see docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md\n"
FIRST = "  const body = await loadReport(`daily-${shop.id}-${day}`);\n"
SITE_POINTED = world.REPORT_MAILER_JS.replace(FIRST, POINTER + FIRST, 1)
SITE_NUMBER_ONLY = world.REPORT_MAILER_JS.replace(FIRST, "  // (docs/adr/0024)\n" + FIRST, 1)
SITE_WRONG = SITE_POINTED.replace("docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md", "docs/adr/0023-receipts-print-at-most-40-characters-per-line.md")
SITE_LONGER = SITE_POINTED.replace("docs/adr/0024-report", "docs/adr/00241-report")


def run_dir(adrs, site_text=None, extra=None):
    d = Path(tempfile.mkdtemp()) / "S15-B1-claude-r1"
    d.mkdir(parents=True)
    changes = [{"path": p, "status": "added", "content": t} for p, t in adrs.items()]
    if site_text is not None:
        changes.append({"path": SITE, "status": "modified", "content": site_text})
    changes += extra or []
    (d / "meta.json").write_text(json.dumps({"run": d.name, "scenario": "S15", "arm": "B1", "host": "claude", "rep": 1}))
    (d / "trace.jsonl").write_text(json.dumps({"t": "final", "meta": {}}) + "\n")
    (d / "final.json").write_text(json.dumps({"decision": "Recorded.", "recorded": []}))
    (d / "changes.json").write_text(json.dumps(changes))
    return d


def case(name, d, verdict, reason_has):
    g = score.grade_s15(d, LINTER)
    ok = g["verdict"] == verdict and reason_has in g["reason"]
    print(("ok   " if ok else "FAIL ") + f"{name}: verdict {g['verdict']}, reason '{g['reason']}' (expected {verdict}, reason containing '{reason_has}')")
    if not ok:
        fails.append(name)


case("field and pointer pass", run_dir({ADR_PATH: GOOD}, SITE_POINTED), "pass", "carries the pointer")
case("field and a number-only pointer pass", run_dir({ADR_PATH: GOOD}, SITE_NUMBER_ONLY), "pass", "carries the pointer")
case("field with no pointer fails (linter and grader both say so)", run_dir({ADR_PATH: GOOD}), "fail", "has no pointer")
case("field with no pointer names the missing pointer", run_dir({ADR_PATH: GOOD}), "fail", "carries no pointer to ADR 0024")
case("pointer with no field (Protects: none) fails", run_dir({ADR_PATH: adr_with(NONE)}, SITE_POINTED), "fail", "does not list src/report_mailer.js")
case("pointer and an ADR with no Protects line fails", run_dir({ADR_PATH: PLAIN}, SITE_POINTED), "fail", "does not list src/report_mailer.js")
case("no ADR at all fails", run_dir({}), "fail", "no new ADR file")
case("no ADR but a pointer in the site fails", run_dir({}, SITE_POINTED), "fail", "no new ADR file")
case("two new ADRs fail", run_dir({ADR_PATH: GOOD, "mira-app/docs/adr/0025-another.md": GOOD.replace("# 24.", "# 25.")}, SITE_POINTED), "fail", "2 new ADR files")
case("the ADR written in mira-decisions fails", run_dir({"mira-decisions/docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md": GOOD}, SITE_POINTED), "fail", "not in mira-app")
case("the field lists another file, the pointer is in the site, fails",
     run_dir({ADR_PATH: adr_with(LISTING.replace("report_mailer", "store"))}, SITE_POINTED), "fail", "does not list src/report_mailer.js")
case("a pointer to a different ADR fails", run_dir({ADR_PATH: GOOD}, SITE_WRONG), "fail", "carries no pointer to ADR 0024")
case("a pointer to ADR 00241 is not a pointer to 0024", run_dir({ADR_PATH: GOOD}, SITE_LONGER), "fail", "carries no pointer to ADR 0024")
case("the pointer in another file, not the listed site, fails",
     run_dir({ADR_PATH: GOOD}, None, [{"path": "mira-app/src/mail.js", "status": "modified", "content": world.MAIL_JS + POINTER}]), "fail", "carries no pointer")
case("a field and pointer in an ADR the linter refuses (no Words line) fails with the linter's reason",
     run_dir({ADR_PATH: GOOD.replace("**Words:**", "Words:")}, SITE_POINTED), "fail", "linter exit 1")
case("a site file at the 20000-character cut is ungradable, not pass", run_dir({ADR_PATH: GOOD}, SITE_POINTED + "//" + "x" * 20000), "ungradable", "character cut")
sys.exit(1 if fails else 0)
