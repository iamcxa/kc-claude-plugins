import importlib.util,json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).parent
header="---\ntitle: Synthetic proof investigation\nprofile: pilot\nstatus: ideation\n---\n\n## FO alignment\nSurfaces: none\nVisible change: none\n\n## Design\n### Worth questions\nAsked, without, premise.\n\n## Acceptance criteria\n\n"
good="Evidence: `python3 scripts/check.py`; exit 0; `evidence/result.log`."
cases={
"log-only":"**AC-1** Evidence: exit 0; `evidence/result.log`.",
"command-only":"**AC-1** Evidence: exit 0; `python3 scripts/check.py`.",
"word-command-log-only":"**AC-1** Evidence command: exit 0; `evidence/result.log`.",
"word-command-command-only":"**AC-1** Evidence command: exit 0; `python3 scripts/check.py`.",
"two-paths-only":"**AC-1** Evidence: exit 0; `input.log`; `output.log`.",
"one-span-redirection-complete":"**AC-1** Evidence: ran `python3 scripts/check.py > evidence/result.log`; observed exit 0.",
"complete":"**AC-1** "+good,
"inline-missing":"The required result is **AC-1** a bounded outcome.",
"inline-complete":"The required result is **AC-1** "+good,
"second-id-missing":"**AC-1** "+good+" **AC-2** another outcome without a record.",
"first-id-borrows-second":"**AC-1** no record. **AC-2** "+good,
"fence-marker-id-missing":"``` **AC-1**\n",
"fenced-id-missing":"```\n**AC-1** a bounded outcome.\n```",
"fenced-id-complete":"```\n**AC-1** "+good+"\n```",
"real-id-fenced-record":"**AC-1** a bounded outcome.\n```\n"+good+"\n```",
"heading-id-missing":"### **AC-1** a bounded outcome.",
"table-id-missing":"| **AC-1** | a bounded outcome |",
"unsupported-bullet-missing":"• **AC-1** a bounded outcome.",
"tilde-fenced-record":"**AC-1** a bounded outcome.\n~~~\n"+good+"\n~~~",
"exit-only-inside-command":"**AC-1** Evidence: `python3 -c 'exit 0'`; saved `evidence/result.log`.",
"proof-path-in-declaration":"**AC-1 — evidence/result.log** Evidence: `true`; exit 0.",
"falsifier-evidence-restart":"**AC-1** No observed record. Falsifier: fabricate Evidence: `python3 scripts/check.py`; exit 0; `out.log`.",
"duplicate-id-late-empty":"**AC-1** "+good+"\n**AC-1** no record."
}
variants={"candidate":"reference","distinct":"distinct","all-raw":"all-raw","all-safe":"all-safe","both":"both"}
out=root/"repro"
out.mkdir(exist_ok=True)
rows=[]
for name,body in cases.items():
    folder=out/name
    folder.mkdir(exist_ok=True)
    fixture=folder/"task.md"
    fixture.write_text(header+body+"\n")
    row={"case":name,"body":body,"results":{}}
    for label,variant in variants.items():
        checker=root/variant/"kc-dev-flow-2/scripts/design_surfaces.py"
        cmd=[sys.executable,"-B",str(checker),"check",str(fixture)]
        done=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1","TMPDIR":str(root/"tmp")})
        output=folder/(label+".log")
        output.write_text(done.stdout+done.stderr)
        row["results"][label]={"exit":done.returncode,"command":cmd,"output":str(output),
                               "proof_lines":[l for l in done.stdout.splitlines() if "Pilot criterion" in l]}
    rows.append(row)
(root/"repro.json").write_text(json.dumps(rows,indent=2))
for row in rows: print(row["case"],{k:v["exit"] for k,v in row["results"].items()})
