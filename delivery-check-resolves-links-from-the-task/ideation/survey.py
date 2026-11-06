import sys, json, re, pathlib
sys.path.insert(0, "/tmp/dl-replay/pkg/kc-dev-flow-2/scripts")
import delivery_gate as g
MD = re.compile(r"(?<![\w:/])(?:[~./\w-]+/)?[\w.-]+\.md(?::\d+(?::\d+)?)?")
for state, repo in [(a, b) for a, b in (x.split("=") for x in sys.argv[1:])]:
    state = pathlib.Path(state); repo = pathlib.Path(repo)
    stats = {}
    tasks = 0
    for task in sorted(list(state.glob("*.md")) + list(state.glob("_archive/*.md"))):
        if task.name == "README.md": continue
        folder = task.with_suffix("")
        texts = []
        rep = g.VALIDATION_SECTION.findall(task.read_text())
        if rep: texts.append(rep[-1])
        for b in sorted(folder.glob("review/validation/briefing-*/index.json")):
            try:
                d = json.loads(b.read_text()); texts.append(d.get("question", "")); texts += [a.get("summary", "") for a in d.get("artifacts", [])]
            except Exception: pass
        if not texts: continue
        tasks += 1
        for v in dict.fromkeys(MD.findall(g.URL.sub(" ", "\n".join(texts)))):
            v = re.sub(r":\d+(?::\d+)?$", "", v)
            if v.startswith(("/", "~")): continue
            # archived tasks: their folder moved with them
            where = tuple(b for b, base in (("task", folder), ("state", state), ("repo", repo)) if (base / v).is_file())
            stats.setdefault(where, []).append(f"{task.stem}:{v}")
    print(f"== {state} tasks-with-validation-text={tasks}")
    for k, v in sorted(stats.items(), key=lambda kv: -len(kv[1])):
        print(f"  {k or ('none',)}: {len(v)}  e.g. {v[:4]}")
