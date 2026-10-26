"""Falsifier probes for the four FO-written-line checks. usage: python3 -B -I fwl_probe.py <scripts dir>
Builds fixtures in a temp dir, runs the package scripts as FO would, prints exit code and first line of output."""
import subprocess, sys, tempfile
from pathlib import Path

S = Path(sys.argv[1])
FM = """---
title: t
variant: kc-dev-flow-2
profile: pilot
status: {status}
gates:
    version: 1
    records:
        - id: gate:t:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:t-ideation-1
              briefing:
                id: briefing:t:ideation:attempt-1:revision-1
                room-ref: ./t/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:t:ideation:1
                by: person:captain
                at: "2026-10-25T10:00:00Z"
                decision: approve
                reason: {reason}
---
"""
RECORD = "Dispatched: from {sha}\nModel: sonnet\n## Checklist\n- x\n## Scope notes\nPackage root: /p\nSend your completion message to `main`.\n"


def run(*argv):
    done = subprocess.run([sys.executable, "-B", *map(str, argv)], capture_output=True, text=True)
    out = (done.stdout or done.stderr).strip().splitlines()
    return done.returncode, (out[0][:90] if out else "") + (f" | +{len(out)-1} line(s): {out[-1][:70]}" if len(out) > 1 else "")


def task(dirp, body, status="ideation", reason="Captain approved"):
    (dirp / "t").mkdir(exist_ok=True)
    (dirp / "t" / "dispatch").mkdir(exist_ok=True)
    (dirp / "t" / "dispatch" / "ideation-1.md").write_text(RECORD.format(sha="a" * 40))
    (dirp / "t.md").write_text(FM.format(status=status, reason=reason) + body)
    return dirp / "t.md", dirp / "t" / "dispatch" / "ideation-1.md"


def show(label, result):
    print(f"{label:<62} exit {result[0]} {result[1]}")


with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    names = lambda rec: run(S / "dispatch_records.py", "--names", rec)
    print("--- 1 Result line before an alignment-needed ideation dispatch")
    t, rec = task(d, "## FO alignment\n\nAlignment: needed before ideation: x\nSurfaces: none\nVisible change: none\n")
    show("needed, no Result", names(rec))
    t, rec = task(d, "## FO alignment\n\nAlignment: needed before ideation: x\nResult: aligned 2026-10-25 by 「好」\nSurfaces: none\nVisible change: none\n")
    show("needed, Result present", names(rec))
    t, rec = task(d, "## FO alignment\n\nAlignment: not needed before ideation: x\nSurfaces: none\nVisible change: none\n")
    show("not needed, no Result", names(rec))
    t, rec = task(d, "## FO alignment\n\nAlignment: not needed: x\n```\nAlignment: needed\n```\nSurfaces: none\nVisible change: none\n")
    show("not needed, fenced example says needed", names(rec))
    t, rec = task(d, "## FO alignment\n\nNeeded at ideation: the design.\nSurfaces: none\nVisible change: none\n")
    show("other spelling (not judged, bounded claim)", names(rec))

    print("--- 2 backslash-quote on a Captain or Asked line")
    base = "## FO alignment\n\nAlignment: not needed: x\nSurfaces: none\nVisible change: none\n\n## Acceptance criteria\n\n**AC-1** x\n\n## Captain amendments\n\n### Amendment 1 — 2026-10-25, chat\n"
    t, rec = task(d, base + 'Captain: 「好」 (chat)\nAsked: "approve \\"x\\" now?"\nSupersedes: none\nDesign: none\n')
    show("Asked holds \\\"", run(S / "design_surfaces.py", "check", t))
    show("same, dispatch --names", names(rec))
    t, rec = task(d, base + 'Captain: 「好」 (chat)\nAsked: "approve x now?"\nSupersedes: none\nDesign: none\n')
    show("Asked clean", run(S / "design_surfaces.py", "check", t))
    t, rec = task(d, base + 'Captain: 「好」 (chat)\nAsked: x\nSupersedes: AC-0 (no replacement: probe)\nDesign: none\nSuperseded text:\n\n    **AC-0** a \\"quoted\\" word\n')
    show("\\\" only inside a moved criterion", run(S / "design_surfaces.py", "check", t))

    print("--- 3 gate question names the merge but not the hold-out")
    q = d / "q.txt"
    t, rec = task(d, "x\n")
    sufnec = "Sufficiency: AC-1 met. Necessity: used by FO. "
    q.write_text(sufnec + "Approval covers merging the full head with --match-head-commit set to it, and removing its worktree.")
    show("grant, no hold-out", run(S / "delivery_gate.py", "question", t, "--text-file", q))
    q.write_text(sufnec + "Approval covers merging the full head with --match-head-commit, unless he says he merges or holds.")
    show("grant, unless he says he merges or holds", run(S / "delivery_gate.py", "question", t, "--text-file", q))
    q.write_text(sufnec + "Approval covers merging; if the Captain says he merges or holds, the merge is excluded: --match-head-commit.")
    show("grant, 'If the Captain says he merges or holds'", run(S / "delivery_gate.py", "question", t, "--text-file", q))
    q.write_text(sufnec + "Approve delivery of the validated head.")
    show("no grant named", run(S / "delivery_gate.py", "question", t, "--text-file", q))

    print("--- 4 Override line in the task and in no resolution reason")
    body = "## FO alignment\n\nAlignment: not needed: x\nSurfaces: none\nVisible change: none\n\n## Acceptance criteria\n\n**AC-1** x\n\nOverride: recommended option A; Captain chose option B; area: scripts.\n"
    t, rec = task(d, body, reason="Captain approved")
    show("Override in body, none in the reason", run(S / "design_surfaces.py", "check", t))
    t, rec = task(d, body, reason="'Override: recommended option A; Captain chose option B; area: scripts.'")
    show("Override in body and in the reason", run(S / "design_surfaces.py", "check", t))
    t, rec = task(d, body.replace("Override: recommended option A; Captain chose option B; area: scripts.", "Write Override: recommended <option>; Captain chose <option>; area: <area> in the reason."), reason="Captain approved")
    show("placeholder form quoted in prose", run(S / "design_surfaces.py", "check", t))
    t, rec = task(d, body.replace("Override: recommended option A; Captain chose option B; area: scripts.", "The line reads Override: recommended ...; Captain chose ...; area: ... in the reason."), reason="Captain approved")
    show("ellipsis form quoted in prose", run(S / "design_surfaces.py", "check", t))

    print("--- 5 a superseded criterion waits in place until a dispatch checklist names the amendment")
    body5 = ("## FO alignment\n\nAlignment: not needed: x\nSurfaces: none\nVisible change: none\n\n## Acceptance criteria\n\n"
             "**AC-1** old.\n\n**AC-2** Amended by Captain, amendment 1: new.\n\n## Captain amendments\n\n### Amendment 1 — 2026-10-25, chat\n"
             "Captain: 「改」 (chat)\nAsked: 「改嗎？」\nSupersedes: AC-1\nDesign: none\n")
    t, rec = task(d, body5)
    (d / "t" / "dispatch" / "ideation-1.md").write_text(RECORD.format(sha="a" * 40))
    show("amendment named in no checklist, AC-1 still declared", run(S / "design_surfaces.py", "check", t))
    (d / "t" / "dispatch" / "implementation-1.md").write_text(RECORD.format(sha="a" * 40).replace("- x", "- Apply Captain amendment 1"))
    show("a checklist names amendment 1, AC-1 still declared", run(S / "design_surfaces.py", "check", t))
