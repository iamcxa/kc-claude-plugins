import sys, re, pathlib, json
sys.path.insert(0, "/tmp/dl-replay/pkg/kc-dev-flow-2/scripts")
import delivery_gate as g
MD = re.compile(r"(?<![\w:/])(?:[~./\w-]+/)?[\w.-]+\.md(?::\d+(?::\d+)?)?")
for arg in sys.argv[1:]:
    state, repo = map(pathlib.Path, arg.split("="))
    tasks_hit = set(); files = set()
    for task in sorted(list(state.glob("*.md")) + list(state.glob("_archive/*.md"))):
        if task.name == "README.md": continue
        rep = g.VALIDATION_SECTION.findall(task.read_text())
        if not rep: continue
        for v in dict.fromkeys(MD.findall(g.URL.sub(" ", rep[-1]))):
            v = re.sub(r":\d+(?::\d+)?$", "", v)
            if v.startswith(("/", "~")): continue
            p = repo / v
            if p.is_file() and g.fenced_steps(p.read_text()):
                tasks_hit.add(task.stem); files.add(v)
    print(f"{repo.name}: {len(tasks_hit)} tasks whose latest validation report names a repo-relative .md with fences; {len(files)} files e.g. {sorted(files)[:5]}")
