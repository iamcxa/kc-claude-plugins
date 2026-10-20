import re, sys, pathlib
W = pathlib.Path(sys.argv[1])
RAW = pathlib.Path(sys.argv[2])
OLD = RAW  # first-run prompts live here
plain = (OLD / "prompt-plain.md").read_text()
lens = (OLD / "prompt-lens.md").read_text()
lens_block = lens[lens.index("Reviewer lens."):]
head, rest = plain.split("The stories:\n", 1)
tail = rest[rest.index("Task: find the questions"):]
for t in ["number-guards-readme-shrink", "fo-write-checks", "chat-only-evidence-observer-blind",
          "delivery-gate-settles-skipped-checks", "special-role-calls-fire-when-needed"]:
    seed = (W / "seeds" / f"{t}.seed.md").read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", seed, re.S)
    fm, body = m.groups()
    title = re.search(r"^title: (.*)$", fm, re.M).group(1)
    intro, after = body.split("## Scope", 1)
    scope = re.split(r"\n## ", after, 1)[0].strip("\n")
    story = f"Story id: {t}\nCard: {title}\n"
    if intro.strip():
        story += intro.strip() + "\n"
    story += "Scope:\n" + scope + "\n\n"
    h = head.replace("/tmp/replay-w0OHE1/snap", str(W / t / "snap"))
    p = h + "The stories:\n" + story + tail
    (RAW / t / "prompt-plain.md").write_text(p)
    (RAW / t / "prompt-lens.md").write_text(p.rstrip("\n") + "\n\n" + lens_block)
    (W / t / "prompt-plain.md").write_text(p)
    (W / t / "prompt-lens.md").write_text(p.rstrip("\n") + "\n\n" + lens_block)
