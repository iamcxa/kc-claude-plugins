import json, sys
arm = sys.argv[1]
calls = []; usage = None; result = None; model = set(); texts = []
for line in open(f"/tmp/val643-replay/{arm}/stream.jsonl"):
    line = line.strip()
    if not line.startswith("{"): continue
    e = json.loads(line)
    if e.get("type") == "assistant":
        m = e["message"]; model.add(m.get("model"))
        for b in m.get("content", []):
            if b.get("type") == "tool_use":
                calls.append((b["name"], b["input"]))
            elif b.get("type") == "text":
                texts.append(b["text"])
    elif e.get("type") == "result":
        result = e
for i, (n, inp) in enumerate(calls, 1):
    s = inp.get("command") or inp.get("skill") or inp.get("file_path") or json.dumps(inp, ensure_ascii=False)
    s = (inp.get("skill") and f"skill={inp['skill']} args={inp.get('args','')}") or s
    print(f"{i:2d} {n}: {s[:230]!r}")
print("models", model, "ncalls", len(calls))
if result:
    print("result usage", json.dumps(result.get("usage")), "num_turns", result.get("num_turns"), "duration_ms", result.get("duration_ms"), "is_error", result.get("is_error"))
    print("modelUsage", json.dumps(result.get("modelUsage"))[:800])
    print("FINAL:", (result.get("result") or "")[:1500])
