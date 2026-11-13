"""Count proof-record refusals with the candidate's main(argv), retaining counts only."""
import contextlib,importlib.util,io,json,re,sys,tempfile
from pathlib import Path
checker,out=Path(sys.argv[1]),Path(sys.argv[2])
sys.path.insert(0,str(checker.parent))
spec=importlib.util.spec_from_file_location("corpus_design_surfaces",checker)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
report={}
for arg in sys.argv[3:]:
    label,root=arg.split("=",1)
    root=Path(root)
    files=[path for path in sorted(list(root.glob("*.md"))+list(root.glob("_archive/*.md")))
           if re.search(r"\A---\n(?:.*\n)*?profile:[ \t]*pilot[ \t]*\n(?:.*\n)*?---\n",path.read_text())]
    counts={"pilot task files":len(files),"in ideation now":sum(bool(re.search(r"^status:[ \t]*ideation\b",p.read_text(),re.M)) for p in files)}
    for mode,force in (("as-is (stage+profile)",False),("forced ideation, no exemption",True)):
        refused=clean=approved_refused=archived_refused=0
        with tempfile.TemporaryDirectory() as directory:
            for source in files:
                text=source.read_text()
                approved=module.design_approved(text)
                if force:
                    text=re.sub(r"^status:.*$","status: ideation",text,count=1,flags=re.M)
                    text=re.sub(r"^gates:\n(?:[ \t]+.*\n|\n)*","",text,count=1,flags=re.M)
                path=Path(directory)/source.name
                path.write_text(text)
                output=io.StringIO()
                with contextlib.redirect_stdout(output): code=module.main(["check",str(path)])
                hit="Pilot criterion" in output.getvalue()
                refused+=hit
                clean+=(not hit) and bool(re.search(r"^[ \t]*(?:[-*+][ \t]+)?\*\*AC-",text,re.M))
                if not force:
                    approved_refused+=hit and approved
                    archived_refused+=hit and "_archive" in source.parts
        counts["refused: "+mode]=refused
        counts["declared criteria, none refused: "+mode]=clean
        if not force:
            counts["approved proof refusals"]=approved_refused
            counts["archived proof refusals"]=archived_refused
    report[label]=counts
out.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
sys.exit(0 if all(not r["approved proof refusals"] and not r["archived proof refusals"] for r in report.values()) else 1)
