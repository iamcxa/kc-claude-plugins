# usage: python3 -I fixtures.py <delivery_gate.py>; one line per case: ok/BAD, name, exit, S4/S5 lines. Base = 0.36.0, candidate = proto.diff applied.
import subprocess, sys, tempfile, textwrap
from pathlib import Path
DG = sys.argv[1]
STEP = "Candidate: none\n\n### Step 1\nAsked: {asked}\nRan: fresh shell 2026-11-09T05:00:00Z\nObserved: ok\n"
ASK = "Open the preview and check the tab icon."
YAML_CARD = textwrap.dedent("""\
    # Built review
    ```yaml
    design_review:
      adrs_read:
        - docs/adr/0064-the-first-screen-leads-with-sign-in.md (Accepted)
    ```
    """)
CE_CARD = textwrap.dedent("""\
    ```yaml
    chief_engineer_advice:
      outcome: A Pilot stage dispatch records its actual inputs in the stamp commit.
    ```
    """)
SH_CARD = "```sh\nprintf unrecorded\n```\n"
def case(name, message, cards=None, asked=ASK, want=0):
    root = Path(tempfile.mkdtemp())
    folder = root / "task"; (folder / "review").mkdir(parents=True)
    for rel, body in (cards or {}).items():
        (folder / rel).parent.mkdir(parents=True, exist_ok=True); (folder / rel).write_text(body)
    rec = folder / "review" / "captain-steps.md"; rec.write_text(STEP.format(asked=asked))
    msg = root / "message.md"; msg.write_text(message.replace("{root}", str(root)))
    run = subprocess.run([sys.executable, "-B", DG, "steps", str(rec), "--text-file", str(msg)], capture_output=True, text=True)
    lines = [l for l in run.stdout.splitlines() if " S4" in l or " S5" in l or "complete" in l]
    flag = "ok " if run.returncode == want else "BAD"
    print(f"{flag} {name}: exit {run.returncode} (want {want}) | " + " ; ".join(lines))
existing = Path(tempfile.mkdtemp()) / "existing.txt"; existing.write_text("x")
case("in1 site URL paths in code spans", ASK + " PR title: `fix(relay): /llms.txt teaches agents`; pages `/web/favicon.svg` and `/pair`.")
case("in2 elided package path", ASK + " Ran `python3 .../scripts/adr_lint.py docs/adr --since a3f28ef6` exit 0.")
case("in3 XML namespace URI in braces", ASK + " XML root `{http://www.w3.org/2000/svg}svg`.")
case("in4 YAML block in a mentioned design file", ASK + " Design review: task/design/built-review.md.", {"design/built-review.md": YAML_CARD})
case("in5 YAML block in a chief-engineer report", ASK + " Report review/chief-engineer-1.md.", {"review/chief-engineer-1.md": CE_CARD})
case("hold1 real sh fence in a mentioned card", ASK + " Steps: task/acceptance.md.", {"acceptance.md": SH_CARD}, want=1)
case("hold2 real shell fence in the message", ASK + "\n```bash\nprintf unrecorded\n```\n", want=1)
case("hold3 empty-info fence in the message", ASK + "\n```\nprintf unrecorded\n```\n", want=1)
case("hold4 missing path under an existing root", ASK + " Read {root}/missing.txt", want=1)
case("hold5 existing absolute path passes", ASK + f" Read {existing}")
case("hold6 bare https link in the message", ASK + " Open https://example.test/a", want=1)
case("hold7 yaml fence in the message itself (11/03 rule)", ASK + "\n```yaml\nkey: value\n```\n", want=1)
case("hold8 'sh run' fence in a mentioned card", ASK + " Steps: task/acceptance.md.", {"acceptance.md": "```sh run\nprintf unrecorded\n```\n"}, want=1)
