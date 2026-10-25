"""Usage: mutate.py <root holding kc-dev-flow-2 with prototype.diff applied>. Applies one source mutation at a time to a copy and lists the new tests that fail."""
import shutil, subprocess, sys, re
from pathlib import Path
import tempfile
SRC = Path(sys.argv[1]).resolve() / "kc-dev-flow-2" / "scripts"
M = {
 "candidates read task.with_suffix": ("delivery_gate.py", '(task_folder(task) / "dispatch").glob("validation-*.md")', '(task.with_suffix("") / "dispatch").glob("validation-*.md")'),
 "role call gets folder parent and 'index'": ("delivery_gate.py", "str(folder.parent), folder.name]", "str(task.parent), task.stem]"),
 "record saved beside index": ("delivery_gate.py", 'folder = task_folder(task) / "merge"', 'folder = task.with_suffix("") / "merge"'),
 "directory argument not resolved": ("delivery_gate.py", "    if task.is_dir():\n        task = task / \"index.md\"\n", ""),
 "sibling head need not be a candidate": ("delivery_gate.py", "elif head not in candidates:", "elif False:"),
 "closed sibling accepted": ("delivery_gate.py", 'if info.get("state") == "CLOSED":', "if False:"),
 "sibling flag ignored": ("delivery_gate.py", "others = sibling_adr_names(args.sibling_pr, adr_dir, candidates, problems, nexts)", "others = []"),
 "readme looked up from the old parents": ("delivery_gate.py", "entries = task_folder(task).parent", "entries = task.parent"),
 "names messages by stem": ("delivery_gate.py", 'f"{task_folder(task).name} owes a special-role call', 'f"{task.stem} owes a special-role call'),
 "dispatch_records: flat-only task file": ("dispatch_records.py", 'next((t for t in (folder / "index.md", folder.parent / f"{folder.name}.md") if t.is_file()), folder / "index.md")', 'folder.parent / f"{folder.name}.md"'),
 "dispatch_records: with_suffix folder": ("dispatch_records.py", 'task_folder(task) if task.suffix == ".md" else task', 'task.with_suffix("") if task.suffix == ".md" else task'),
}
for name,(f,old,new) in M.items():
    work = Path(tempfile.mkdtemp()) / "t"
    shutil.copytree(SRC.parent.parent, work, ignore=shutil.ignore_patterns("__pycache__"))
    sd = work/"kc-dev-flow-2"/"scripts"; text=(sd/f).read_text()
    assert text.count(old)==1,(name,text.count(old))
    (sd/f).write_text(text.replace(old,new))
    mods = ["test_delivery_gate.FolderTaskTests","test_delivery_gate.SiblingPrTests","test_dispatch_records.TaskFactTests"]
    done = subprocess.run([sys.executable,"-B","-m","unittest",*mods],cwd=sd,capture_output=True,text=True)
    fails = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\w+) \((\S+)\)", done.stderr, re.M)))
    print(f"{name}: exit {done.returncode}; failing: {[a for a,b in fails]}", flush=True)
